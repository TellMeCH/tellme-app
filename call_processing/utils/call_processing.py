import time
from datetime import datetime
from io import BytesIO
from django.conf import settings
import deepgram
import httpx
from pydub import AudioSegment
from langfuse.decorators import observe, langfuse_context


class CallProcessingPipeline:
    """
    A processing pipeline in charge of the transcription, diarization, and mining of call recording data.

    Steps:
    1. Splits the recording into CHUNK_SIZE minute segments.
    2. Transcribes each chunk with Deepgram.
    3. Ensures consistency in detected language across chunks.
    4. Logs the entire process in Langfuse for observability.

    Attributes:
        CHUNK_SIZE (float): Duration of each audio chunk in minutes.
        TRANSCRIPTION_MODEL_NAME (str): The name of the transcription model to use.
        TRANSCRIPTION_MAX_RETRIES (int): Maximum retries per recording chunk when dealing with the Deepgram API
        TRANSCRIPTION_BASE_DELAY (float): Base waiting time per recording chunk when dealing with the Deepgram API
        TRANSCRIPTION_BACKOFF_FACTOR (int): Back-off factor per recording chunk when dealing with the Deepgram API
    """
    CHUNK_SIZE: float = 0.1
    TRANSCRIPTION_MODEL_NAME: str = 'whisper-medium'
    TRANSCRIPTION_MAX_RETRIES: int = 5
    TRANSCRIPTION_BASE_DELAY: float = 1.0
    TRANSCRIPTION_BACKOFF_FACTOR: int = 2

    def __init__(self) -> None:
        """
        Initializes the pipeline by setting up the Deepgram client and transcription options.

        Raises:
            ValueError: If the DEEPGRAM_API_KEY is not set in the environment.
        """
        if not hasattr(settings, 'DEEPGRAM_API_KEY') or not settings.DEEPGRAM_API_KEY:
            raise ValueError("Deepgram API key not found. Please set the DEEPGRAM_API_KEY environment variable.")

        self.deepgram = deepgram.DeepgramClient(settings.DEEPGRAM_API_KEY)
        self.transcription_options = deepgram.PrerecordedOptions(
            model=self.TRANSCRIPTION_MODEL_NAME,
            smart_format=True,
            detect_language=True,
            punctuate=True,
            diarize=True,
        )

    @observe()
    def __call__(self, file_data: bytes, file_metadata: dict[str, str]) -> (str, str):
        """
        Processes the given audio data through the pipeline and returns the transcript and base language.

        This top-level method is decorated with @observe(), creating a top-level Langfuse trace.

        Args:
            file_data (bytes): Raw binary data of the audio file.
            file_metadata (dict[str, str]): Contains file metadata for Langfuse

        Returns:
            Tuple[str, str]: The full transcript and the detected language of the audio.
        """
        langfuse_context.update_current_trace(
            name="Call Processing",
            user_id='Cloud Task Manager',
            tags=[settings.TELLME_ENV],
            metadata=file_metadata
        )
        transcript, language = self._transcribe(file_data)

        if len(transcript) == 0:
            raise ValueError('Call Processing: Produced transcript is empty.')

        return transcript, language

    @observe()
    def _transcribe(self, file_data: bytes) -> (str, str):
        """
        Internal method to handle the full transcription process:
        1. Cuts the audio into chunks.
        2. Transcribes each chunk.
        3. Checks for consistent language detection.

        Args:
            file_data (bytes): The raw audio data to transcribe.

        Returns:
            Tuple[str, str]: The full transcript and the detected base language.

        Raises:
            Warning: If language changes across chunks.
        """
        recording_chunks = self.cut_into_chunks(file_data)
        base_language = None
        full_transcript = None

        for i, chunk in enumerate(recording_chunks):
            chunk_transcript, chunk_language = self.transcribe_chunk(chunk)
            if i == 0:
                base_language = chunk_language
                full_transcript = chunk_transcript
            else:
                if base_language != chunk_language:
                    raise Warning(f'Detected language changed suddenly from {base_language} to {chunk_language}.')
                full_transcript += '\n' + chunk_transcript

        if base_language is None:
            base_language = "unknown"
        if full_transcript is None:
            full_transcript = ""

        return full_transcript, base_language

    def cut_into_chunks(self, file_data: bytes) -> list[bytes]:
        """
        Splits the provided audio data into CHUNK_SIZE minute segments using pydub.

        Args:
            file_data (bytes): The raw audio file data.

        Returns:
            List[bytes]: A list of chunks in bytes format.
        """
        # Load the audio file from bytes
        audio = AudioSegment.from_file(BytesIO(file_data), format="wav")

        # Calculate chunk length in milliseconds.
        chunk_length_ms = int(self.CHUNK_SIZE * 60 * 1000)
        chunks = []

        # Iterate over the audio by chunk_length_ms intervals.
        for start_ms in range(0, len(audio), chunk_length_ms):
            end_ms = start_ms + chunk_length_ms
            chunk = audio[start_ms:end_ms]
            # Export chunk to bytes in memory
            chunk_buffer = BytesIO()
            chunk.export(chunk_buffer, format="wav")
            chunks.append(chunk_buffer.getvalue())

        return chunks

    @observe(as_type="generation")
    def transcribe_chunk(self, chunk_data: bytes) -> (str, str):
        """
        Transcribes a single audio chunk using the Deepgram API, with exponential backoff on 429 responses.

        Decorated with @observe() so each chunk call is a child observation under the main trace.
        This allows you to associate each chunk call to Deepgram with a separate observation in Langfuse.

        Args:
            chunk_data (bytes): The raw binary data of the audio chunk.

        Returns:
            Tuple[str, str]: The transcript text and detected language for this chunk.

        Raises:
            httpx.HTTPError: If transcription fails after multiple retries.
        """
        payload = {'buffer': chunk_data}

        delay = self.TRANSCRIPTION_BASE_DELAY

        # Update Langfuse observation with input metadata
        langfuse_context.update_current_observation(
            name="Deepgram Transcription Chunk",
            model=f'deepgram-{self.TRANSCRIPTION_MODEL_NAME}',
            start_time=datetime.now(),
        )

        for attempt in range(self.TRANSCRIPTION_MAX_RETRIES):
            try:
                response = self.deepgram.listen.rest.v("1").transcribe_file(
                    payload, self.transcription_options, timeout=httpx.Timeout(600.0, connect=10.0)
                )

                transcript = response['results']['channels'][0]['alternatives'][0]['paragraphs']['transcript']
                transcript = transcript.replace("\n\n", "\n").strip()
                language = response['results']['channels'][0]['detected_language']

                # Update observation with results
                langfuse_context.update_current_observation(
                    end_time=datetime.now(),
                    metadata={'attempts_required': attempt + 1},
                    input={"chunk_size_bytes": len(chunk_data), "chunk_size_seconds": response.metadata.duration},
                    output={"transcript_preview": transcript[:100], "language": language},
                    usage={'total': response.metadata.duration}
                )

                return transcript, language

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429 and attempt < self.TRANSCRIPTION_MAX_RETRIES - 1:
                    # Exponential backoff for rate-limited requests
                    time.sleep(delay)
                    delay *= self.TRANSCRIPTION_BACKOFF_FACTOR
                else:
                    # Update Langfuse observation with error info
                    langfuse_context.update_current_observation(
                        status_message=str(e),
                        level="ERROR"
                    )
                    raise e

        # If we somehow didn't return or raise in the loop, raise a generic error
        raise httpx.HTTPError("Failed to transcribe chunk after multiple retries.")
