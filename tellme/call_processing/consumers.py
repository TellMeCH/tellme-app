import asyncio
import json
import logging
import os
import datetime
import tempfile
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from tellme.call_processing.utils import audio_utils, processing_utils
from tellme.call_processing.utils.audiohook_utils import (
    verify_audiohook_signature,
    get_org_from_audiohook_headers,
    select_media,
)

logger = logging.getLogger('django')


class AudioHookConsumer(AsyncWebsocketConsumer):
    """
    Async Django Channels consumer implementing the Genesys AudioHook protocol (v2).

    Authentication:
      - X-API-KEY header → hashed with HASH_KEY → OrganizationAPIKey → Organization
      - HMAC-SHA256 signature verified against settings.CX_CLIENT_SECRET
      - audiohook-organization-id header cross-validated against organization.cx_system_org_id

    Why AsyncWebsocketConsumer?
      Audio arrives continuously at ~100ms intervals while the server also handles
      HMAC verification, DB lookups, and file I/O. The async variant handles all
      concurrent connections on a single event loop thread: each `await` yields
      control to other connections instead of blocking a thread for the full duration.
    """

    AUDIOHOOK_SAMPLE_RATE = 8000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.org = None
        self.customer_id = None
        self.customer_ani = None
        self.agent_id = None
        self.conversation_id = None
        self.language = 'en-us'
        self.chosen_media = None
        self.connection_timestamp = None
        self.server_seq = 0
        self.last_client_seq = 0
        self.session_id = None
        self.recording_started = False
        self.recording_closed = False
        self.error_close = False
        self.temp_file = None
        self.temp_file_path = None

    def increment_server_seq(self):
        self.server_seq += 1
        return self.server_seq

    # Connection lifecycle
    async def connect(self):
        """
        Accept the WebSocket upgrade, then authenticate and resolve the organization.
        The connection is always accepted first so that a 'disconnect' error message
        can be sent back before closing if authentication fails.
        """
        await self.accept()

        headers = dict(self.scope.get('headers', []))

        # Extract the session ID immediately from the header (not from the first message)
        raw_session_id = headers.get(b'audiohook-session-id', b'').decode('utf-8')
        self.session_id = raw_session_id if raw_session_id else str(uuid.uuid4())

        # Verify HMAC-SHA256 signature (includes ≥500ms artificial delay on failure)
        request_path = self.scope.get('path', '/ws/audiohook/')
        authority = headers.get(b'host', b'').decode('utf-8')
        str_headers = {k.decode(): v.decode() for k, v in headers.items()}
        is_valid, reason = await verify_audiohook_signature(str_headers, request_path, authority)
        if not is_valid:
            logger.warning(f'AudioHook signature verification failed: {reason}')
            await self.send_disconnect('unauthorized', reason)
            return

        # Resolve organization via API key + cx_system_org_id cross-validation
        try:
            self.org = await get_org_from_audiohook_headers(headers)
        except AuthenticationFailed as e:
            logger.warning(f'AudioHook org resolution failed: {e}')
            await self.send_disconnect('unauthorized', str(e))
            return

        logger.info(f'AudioHook session {self.session_id}: authenticated org {self.org.id}')

        self.connection_timestamp = datetime.datetime.now(datetime.UTC)
        tf = tempfile.NamedTemporaryFile(prefix='audiohook_', delete=False)
        self.temp_file = tf
        self.temp_file_path = tf.name
        logger.info(f'AudioHook session {self.session_id}: temp file {self.temp_file_path}')

    async def disconnect(self, code):
        """Called when the WebSocket connection is closed for any reason."""
        if not self.recording_closed:
            await asyncio.get_event_loop().run_in_executor(None, self._finalize_recording_sync)

    # Message routing
    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            await self._handle_protocol_message(text_data)
        elif bytes_data is not None:
            await self._handle_audio_frame(bytes_data)

    async def _handle_protocol_message(self, raw_text: str):
        try:
            message = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.warning(f'AudioHook session {self.session_id}: invalid JSON from client')
            await self.send_disconnect('error', 'Invalid JSON')
            return

        seq = message.get('seq')
        if not isinstance(seq, int) or seq != self.last_client_seq + 1:
            logger.error(
                f'AudioHook session {self.session_id}: out-of-order seq '
                f'got={seq}, expected={self.last_client_seq + 1}'
            )
            await self.send_disconnect('error', 'Out-of-order seq')
            return
        self.last_client_seq = seq

        msg_type = message.get('type')

        # After a disconnect has been sent, only a 'close' can proceed normally.
        # All other message types are silently ignored; the client should send 'close' once it processes the disconnect.
        if msg_type == 'close':
            await self._handle_close(message)
        elif self.error_close:
            pass
        elif msg_type == 'open':
            await self._handle_open(message)
        elif msg_type == 'ping':
            await self._handle_ping()
        elif msg_type == 'update':
            await self._handle_update(message)
        elif msg_type == 'discarded':
            await self._handle_discarded(message)
        elif msg_type == 'error':
            await self._handle_error(message)
        elif msg_type in ('paused', 'resumed'):
            # AudioHook Monitor: acknowledge receipt but take no action
            pass
        else:
            logger.info(f'AudioHook session {self.session_id}: ignoring unknown type {msg_type!r}')

    # Protocol message handlers
    async def _handle_open(self, message):
        """
        Handle the AudioHook 'open' message sent by Genesys at session start.

        Expected parameters for TellMe integration:
          parameters.organizationId   (str, required)
              UUID string matching the Organization.cx_system_org_id configured in TellMe.
              Set in Genesys: AudioHook integration → Advanced → Custom Configuration → organizationId.

          parameters.participant.id   (str, optional)
              Genesys participant UUID for the customer leg of the call.
              Used as the customer reference when looking up / creating a Customer record.

          parameters.participant.ani  (str, optional)
              Caller's phone number (E.164). Fallback customer reference when participant.id is absent.

          parameters.conversationId   (str, optional)
              Genesys conversation UUID. Stored on the TellMe Conversation for cross-system traceability.

          parameters.language         (str, optional, default 'en-us')
              BCP-47 language tag, e.g. 'de-ch'. Overrides the Organization default during transcription.

          parameters.customConfig     (object, optional)
              Arbitrary key/value pairs passed through from the Genesys integration config.
              TellMe reads the following keys:
                agent_id  (int, required for processing)
                    Integer primary key of the TellMe Agent record that handled the call.
                    Obtain from `python manage.py create_sample_data` output or the Django admin.
                    Set in Genesys: AudioHook integration → Advanced → Custom Configuration
                    as {"agent_id": <integer>}.

          parameters.media            (array, required)
              List of offered media formats. TellMe accepts PCMU at 8000 Hz, stereo or mono.
        """
        params = message.get('parameters', {})

        # Validate organizationId in the message body matches the header-derived org
        incoming_org_id = params.get('organizationId', '')
        if str(self.org.cx_system_org_id) != incoming_org_id:
            logger.warning(
                f'AudioHook session {self.session_id}: organizationId mismatch '
                f'header={self.org.cx_system_org_id}, body={incoming_org_id}'
            )
            await self.send_disconnect('unauthorized', 'organizationId mismatch')
            return

        self.conversation_id = params.get('conversationId')
        participant = params.get('participant', {})
        self.customer_id = participant.get('id')
        self.customer_ani = participant.get('ani')
        self.language = params.get('language', 'en-us')

        # Agent ID from customConfig (no native agent field in the AudioHook protocol)
        custom_config = params.get('customConfig') or {}
        self.agent_id = custom_config.get('agent_id')

        chosen = select_media(params.get('media', []))
        if not chosen:
            await self.send_disconnect('error', 'No acceptable media format offered')
            return

        self.chosen_media = chosen
        self.recording_started = True

        await self.send(text_data=json.dumps({
            'version': '2',
            'type': 'opened',
            'seq': self.increment_server_seq(),
            'clientseq': self.last_client_seq,
            'id': self.session_id,
            'parameters': {
                'startPaused': False,
                'media': [chosen],
            },
        }))
        logger.info(
            f'AudioHook session {self.session_id}: opened with media={chosen}, '
            f'customer={self.customer_id}, agent={self.agent_id}'
        )

    async def _handle_ping(self):
        await self.send(text_data=json.dumps({
            'version': '2',
            'type': 'pong',
            'seq': self.increment_server_seq(),
            'clientseq': self.last_client_seq,
            'id': self.session_id,
            'parameters': {},
        }))
        logger.debug(f'AudioHook session {self.session_id}: pong sent')

    async def _handle_close(self, message):
        reason = message.get('parameters', {}).get('reason', 'end')
        logger.info(f'AudioHook session {self.session_id}: received close reason={reason}')

        self.recording_closed = True
        await self.send(text_data=json.dumps({
            'version': '2',
            'type': 'closed',
            'seq': self.increment_server_seq(),
            'clientseq': self.last_client_seq,
            'id': self.session_id,
            'parameters': {},
        }))
        logger.info(f'AudioHook session {self.session_id}: sent closed')

        await asyncio.get_event_loop().run_in_executor(None, self._finalize_recording_sync)
        await self.close()

    async def _handle_update(self, message):
        self.language = message.get('parameters', {}).get('language', self.language)
        await self.send(text_data=json.dumps({
            'version': '2',
            'type': 'updated',
            'seq': self.increment_server_seq(),
            'clientseq': self.last_client_seq,
            'id': self.session_id,
            'parameters': {},
        }))
        logger.info(f'AudioHook session {self.session_id}: language updated to {self.language}')

    async def _handle_discarded(self, message):
        params = message.get('parameters', {})
        logger.info(
            f'AudioHook session {self.session_id}: audio discarded '
            f"start={params.get('start')}, discarded={params.get('discarded')}"
        )
        # No response required for AudioHook Monitor

    async def _handle_error(self, message):
        params = message.get('parameters', {})
        logger.error(
            f'AudioHook session {self.session_id}: client error '
            f"code={params.get('code')}, message={params.get('message')}"
        )
        # No response required; client will send close

    async def _handle_audio_frame(self, data: bytes):
        if not self.recording_closed and not self.error_close:
            if self.temp_file:
                self.temp_file.write(data)
            else:
                logger.warning(f'AudioHook session {self.session_id}: no temp file open')
        else:
            logger.warning(f'AudioHook session {self.session_id}: audio received after close, ignoring')

    # Error signalling
    async def send_disconnect(self, reason: str, info: str = ''):
        """
        Send a 'disconnect' message to the client.
        reason must be one of: 'completed', 'unauthorized', 'error'
        After calling this, self.error_close is set so further non-close messages are ignored.
        """
        await self.send(text_data=json.dumps({
            'version': '2',
            'type': 'disconnect',
            'seq': self.increment_server_seq(),
            'clientseq': self.last_client_seq,
            'id': self.session_id or '',
            'parameters': {'reason': reason, 'info': info},
        }))
        self.error_close = True
        logger.error(f'AudioHook session {self.session_id}: sent disconnect reason={reason} info={info!r}')

    # Recording finalization (runs in a thread pool executor)
    def _finalize_recording_sync(self):
        """
        Close the temp file, encode the audio as WAV, upload to GCS, and create a
        Cloud Task for processing. Runs synchronously in a thread pool so the event
        loop is not blocked during I/O.
        """
        if not self.recording_started:
            logger.info(f'AudioHook session {self.session_id}: recording never started, skipping finalize')
            return

        if self.temp_file:
            self.temp_file.close()

        if not self.temp_file_path or not os.path.exists(self.temp_file_path):
            logger.warning(f'AudioHook session {self.session_id}: no audio data received')
            return

        size_bytes = os.path.getsize(self.temp_file_path)
        logger.info(f'AudioHook session {self.session_id}: local file size {size_bytes} bytes')

        channels = len(self.chosen_media.get('channels', [])) if self.chosen_media else 2
        audio_format = self.chosen_media.get('format', 'PCMU') if self.chosen_media else 'PCMU'

        if not self.error_close and size_bytes > 0:
            if audio_format == 'PCMU':
                wav_data = audio_utils.decode_mulaw_file_to_wav(
                    self.temp_file_path,
                    channels=channels,
                    sample_rate=self.AUDIOHOOK_SAMPLE_RATE,
                )
            else:
                logger.warning(
                    f'AudioHook session {self.session_id}: unsupported format {audio_format}, skipping upload'
                )
                os.remove(self.temp_file_path)
                return

            # customer_id falls back to the ANI if no UUID participant ID was provided
            customer_ref = self.customer_id or self.customer_ani or 'unknown'
            blob_name = (
                f'{self.org.id}/{customer_ref}_{self.agent_id}_'
                f'{self.connection_timestamp.isoformat()}.wav'
            )
            message, status_code = processing_utils.upload_file_and_create_processing_task(
                blob_name,
                self.agent_id,
                customer_ref,
                self.org.id,
                self.connection_timestamp,
                logger,
                True,
                wav_data,
            )
            logger.info(message['message'])

        # Remove local file
        os.remove(self.temp_file_path)
        logger.info(f'AudioHook session {self.session_id}: removed temp file {self.temp_file_path}')
