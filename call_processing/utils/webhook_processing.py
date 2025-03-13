import io
import requests
from datetime import datetime
from django.conf import settings
from pydub import AudioSegment
from call_processing.utils.gcs_utils import upload_to_gcs
from call_processing.utils.queue_utils import create_storage_path


def parse_created_date(rec):
    dt_str = rec.get("date_created") or ""
    return datetime.strptime(dt_str, "%a, %d %b %Y %H:%M:%S %z")


def process_webhook_recordings(call_sid, organization, customer_id, agent_id, timestamp, logger):
    """
    1. Uses the Organization's credentials to query the 'List Recordings' API.
    2. Downloads each returned mp3 recording.
    3. Concatenates them into a single WAV file (in-memory).
    4. Returns a tuple: (output_buffer, file_name).

    Raises:
        RuntimeError: If something goes wrong (network error, no recordings, etc.).
    """

    # Pull credentials from the Organization model
    # TODO: Add account_id, auth_token, provider to the Organization Model
    account_sid = organization.account_id
    auth_token = organization.auth_token
    base_url = settings.COMMUNICATIONS_API_URLS[organization.provider]

    if organization.provider == 'avaya':
        # Query Avaya for the recordings matching the given CallSid
        recordings_endpoint = f"{base_url}/Accounts/{account_sid}/Recordings.json"
        params = {"CallSid": call_sid}
        try:
            response = requests.get(
                recordings_endpoint,
                params=params,
                auth=(account_sid, auth_token),
                timeout=30
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            msg = f"Error fetching recordings from Avaya for CallSid {call_sid}: {str(exc)}"
            logger.error(msg)
            raise RuntimeError(msg)

        data = response.json()
        recordings = data.get("recordings", [])

        if not recordings:
            msg = f"No recordings found for CallSid {call_sid}"
            logger.warning(msg)
            raise RuntimeError(msg)

        # Sort recordings chronologically
        recordings_sorted = sorted(recordings, key=parse_created_date)

        folder_prefix = create_storage_path(organization.id, customer_id, agent_id, timestamp)

        # Download each MP3, convert to WAV, and upload
        uploaded_uris = []
        for i, rec in enumerate(recordings_sorted):
            recording_sid = rec.get("sid", "unknownsid")
            recording_url = rec.get("recording_url")
            if not recording_url:
                logger.warning(f"Recording {recording_sid} has no 'recording_url'; skipping.")
                continue

            try:
                mp3_resp = requests.get(recording_url, timeout=30)
                mp3_resp.raise_for_status()
            except Exception as exc:
                logger.error(f"Error downloading MP3 from {recording_url}: {str(exc)}")
                continue

            try:
                # Convert MP3 bytes to a pydub AudioSegment
                audio_segment = AudioSegment.from_file(io.BytesIO(mp3_resp.content), format="mp3")

                # Export to WAV in-memory
                wav_buffer = io.BytesIO()
                audio_segment.export(wav_buffer, format="wav")
                wav_buffer.seek(0)
            except Exception as exc:
                logger.error(f"Error converting MP3 to WAV for recording {recording_sid}: {str(exc)}")
                continue

            # Build the GCS destination path for this snippet
            destination_blob_name = f"{folder_prefix}/recording_{i}_{recording_sid}.wav"

            try:
                gcs_uri = upload_to_gcs(wav_buffer, destination_blob_name)
                uploaded_uris.append(gcs_uri)
                logger.info(f"Uploaded recording SID={recording_sid} to {gcs_uri}")
            except Exception as exc:
                logger.error(f"GCS upload failed for {recording_sid}: {str(exc)}")

        if not uploaded_uris:
            raise RuntimeError("All WAV conversions or uploads failed.")

        return uploaded_uris
