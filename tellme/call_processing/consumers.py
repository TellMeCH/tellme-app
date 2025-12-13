import json
import logging
import os
import datetime
import tempfile
import hashlib
from channels.generic.websocket import WebsocketConsumer
from rest_framework import exceptions
from django.utils import timezone
from django.conf import settings
from tellme.call_miner.models import OrganizationAPIKey
from tellme.call_processing.utils import audio_utils, processing_utils

logger = logging.getLogger('django')


class AudioHookConsumer(WebsocketConsumer):
    """
    A Channels consumer that:
     - Authenticates with an API key (replicating OrganizationAPIKeyAuthentication).
     - Chooses the two-channel format in "opened".
     - Checks "seq" in each incoming message.
     - Streams audio to a GCS temp file, then moves it to a final bucket.
    """
    AUDIOHOOK_CHANNELS = 2
    AUDIOHOOK_SAMPLE_RATE = 8000
    MAXIMUM_ERROR_RETRIES = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.org = None
        self.customer_id = None
        self.agent_id = None
        self.connection_timestamp = None
        self.server_seq = 0         # Outgoing seq for messages the app sends
        self.last_client_seq = 0    # The last seq received from client (Genesys)
        self.session_id = None
        self.recording_started = False
        self.recording_closed = False
        self.error_close = False
        self.error_retries = 0  # Number of times to wait until the client sends "close" after an error
        self.temp_file = None
        self.temp_file_path = None

    def increment_server_seq(self):
        self.server_seq += 1
        return self.server_seq

    @staticmethod
    def authenticate_api_key_from_scope_headers(headers):
        """
        Replicate OrganizationAPIKeyAuthentication with synchronous logic:
        read from scope headers, find X-Tellme-Api-Key header with X-API-KEY prefix, check DB, etc.
        """
        auth_header = None
        for (name, value) in headers:
            if name == b'x-tellme-api-key':
                auth_header = value.decode('utf-8')
                break

        if not auth_header:
            raise exceptions.AuthenticationFailed("No X-Tellme-Api-Key header found.")

        # Check if the header starts with the expected keyword (X-API-KEY <key>)
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'X-API-KEY':
            raise exceptions.AuthenticationFailed("Invalid X-Tellme-Api-Key header format.")

        api_key = parts[1]
        logger.debug("Got API key from scope headers.")
        hashed_key = hashlib.sha256((settings.HASH_KEY + api_key + settings.HASH_KEY).encode('utf-8')).hexdigest()
        try:
            org_api_key = OrganizationAPIKey.objects.get(hashed_api_key=hashed_key)
        except OrganizationAPIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid API key.")

        if org_api_key.expires < timezone.now():
            raise exceptions.AuthenticationFailed("API key expired.")

        return org_api_key.organization

    def connect(self):
        """
        Called upon WebSocket connect. Fetch and verify the Authorization
        header from scope, then accept or close the connection.
        """
        self.accept()
        try:
            self.org = self.authenticate_api_key_from_scope_headers(self.scope["headers"])
            logger.info(f"Authenticated Organization: {self.org.id}")
        except exceptions.AuthenticationFailed as e:
            logger.warning(f"Authentication failed: {e}")
            self.send_error('unauthorized', str(e))
            return

        # Define connection timestamp
        self.connection_timestamp = datetime.datetime.now(datetime.UTC)

        # Create a local temp file to store raw audio
        tf = tempfile.NamedTemporaryFile(prefix="audiohook_", delete=False)
        self.temp_file = tf
        self.temp_file_path = tf.name
        logger.info(f"Created local temp file: {self.temp_file_path}")

    def handle_open(self, message):
        """
        Handle Genesys' 'open' message: pick the 2-channel media format from 'media',
        set the customer ID, and  then respond with 'opened'.
        """
        self.recording_started = True

        # Extract the customer ID from the message
        self.customer_id = message['parameters'].get('participant', {'id': None}).get('id')

        # Extract the agent ID from the message (Fake, to see how Genesys provides this)
        self.agent_id = message['parameters'].get('agent', {'id': None}).get('id')

        # Of the offered media, select the configuration that offers 2 channels. If no such option exist, select
        # the first configuration in the offered media
        chosen = []
        options = message['parameters'].get('media', [])
        for opt in options:
            if len(opt.get('channels', [])) == 2:
                chosen = [opt]
                break
        if not chosen and len(options) > 0:
            chosen = [options[0]]

        opened = {
            "version": "2",
            "type": "opened",
            "seq": self.increment_server_seq(),
            "clientseq": self.last_client_seq,
            "id": self.session_id,
            "parameters": {
                "startPaused": False,
                "media": chosen,
            }
        }
        self.send(text_data=json.dumps(opened))
        logger.info(f"Sent 'opened', chosen media={chosen}")

    def handle_ping(self):
        """
        Handle Genesys' 'ping' message responding with 'pong'.
        """
        pong_msg = {
            "version": "2",
            "type": "pong",
            "seq": self.increment_server_seq(),
            "clientseq": self.last_client_seq,
            "id": self.session_id,
            "parameters": {}
        }
        self.send(text_data=json.dumps(pong_msg))
        logger.debug("Responded with 'pong'.")

    def handle_close(self, message):
        """
        Handle Genesys' 'close' message by responding with 'closed' and finalizing the recording.
        """
        reason = message["parameters"].get("reason", "end")
        logger.info(f"Received 'close' with reason={reason}")

        self.recording_closed = True
        closed_msg = {
            "version": "2",
            "type": "closed",
            "seq": self.increment_server_seq(),
            "clientseq": self.last_client_seq,
            "id": self.session_id,
            "parameters": {}
        }
        self.send(text_data=json.dumps(closed_msg))
        logger.info("Sent 'closed' response.")

        # Now finalize
        self.finalize_recording()
        self.disconnect(200)
        self.close()

    def handle_protocol_message(self, raw_text):
        """
        Parse the incoming JSON message (e.g. 'open', 'ping', 'close'),
        check seq, and respond accordingly.
        """
        try:
            message = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON from client.")
            self.send_error("error", "Invalid JSON")
            return

        msg_type = message.get("type")
        seq = message.get("seq")

        # Check that seq is equal to last_client_seq + 1
        if not isinstance(seq, int) or seq != self.last_client_seq + 1:
            logger.error(f"Out-of-order seq: got={seq}, expected={self.last_client_seq + 1}")
            self.send_error("error", "Out-of-order seq")
            return
        self.last_client_seq = seq

        self.session_id = message.get("id", self.session_id)

        # Dispatch based on msg_type. If an error has occurred, only accept 'close'
        if msg_type == 'close':
            self.handle_close(message)
        else:
            if not self.error_close:
                if msg_type == "open":
                    self.handle_open(message)
                elif msg_type == "ping":
                    self.handle_ping()
                else:
                    logger.info(f"Unhandled msg_type='{msg_type}', ignoring.")
            else:
                # If disconnect has been sent, and the connection has not yet been closed, simply send 'disconnect'
                # again, until a maximum retry count is met
                self.send_error('error', 'Expected "close" message.')
                self.error_retries += 1

                if self.error_retries > self.MAXIMUM_ERROR_RETRIES:
                    self.finalize_recording()
                    self.disconnect(400)
                    self.close()

    def handle_audio_frame(self, data: bytes):
        """
        Append the incoming audio chunk to the local temp file, unless already closed or an error has occurred.
        """
        if not self.recording_closed and not self.error_close:
            if self.temp_file:
                self.temp_file.write(data)
            else:
                logger.warning("No temp file open to write audio data.")
        else:
            logger.warning("Received audio after 'close' was requested, ignoring.")

    def receive(self, text_data=None, bytes_data=None):
        """
        Called each time the server receives a message from the client.
        """
        if text_data is not None:
            self.handle_protocol_message(text_data)
        elif bytes_data is not None:
            self.handle_audio_frame(bytes_data)

    def finalize_recording(self):
        """
        After closing, upload and rename the temporary file to GCS, remove the local temp file,
        and optionally create a Cloud Task to further process.
        """
        if not self.recording_started:
            logger.info("Recording never started; skipping finalize.")
            return

        if self.temp_file:
            self.temp_file.close()

        if self.temp_file_path and os.path.exists(self.temp_file_path):
            size_bytes = os.path.getsize(self.temp_file_path)
            logger.info(f"Local file size: {size_bytes} bytes")
        else:
            logger.warning("No audio data received.")
            return

        if not self.error_close and size_bytes > 0:
            # Encode as WAV with linear PCM and proper headers
            # Note to self: examine whether this takes too long/blocks the consumer
            wav_data = audio_utils.decode_mulaw_file_to_wav(
                self.temp_file_path,
                channels=self.AUDIOHOOK_CHANNELS,
                sample_rate=self.AUDIOHOOK_SAMPLE_RATE
            )

            # Upload to GCS and create Task
            blob_name = f"{self.org.id}/{self.customer_id}_{self.agent_id}_{self.connection_timestamp.isoformat()}.wav"
            message, status_code = queue_utils.upload_file_and_create_processing_task(
                blob_name, self.agent_id, self.customer_id, self.org.id, self.connection_timestamp, logger,
                True, wav_data  # Note to self: Consider whether checking agent validity is reasonable
            )
            logger.info(message['message'])

        # Remove local file
        os.remove(self.temp_file_path)
        logger.info(f"Removed local temp file {self.temp_file_path}")

    def send_error(self, reason: str, message: str):
        """
        Send a synchronous 'error' message to Genesys.
        """
        error_msg = {
            "version": "2",
            "type": "disconnect",
            "seq": self.increment_server_seq(),
            "clientseq": self.last_client_seq,
            "id": self.session_id or "",
            "parameters": {
                "reason": reason,
                "info": message
            }
        }
        self.send(text_data=json.dumps(error_msg))
        self.error_close = True
        logger.error(f"Sent 'error' with reason={reason}, message={message}")
