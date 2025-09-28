"""
CallTranscriber handles audio transcription and diarization.

This module contains all transcription-related functionality including:
- Audio chunking
- Speech-to-text via Deepgram and Groq
- Speaker diarization via Vertex AI
"""

import httpx
from datetime import datetime
from io import BytesIO
from pydub import AudioSegment
from django.conf import settings
import deepgram
import groq
from google import genai
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context
from deepgram.clients.common.v1.errors import DeepgramApiError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception
from google.genai import types

from tellme.call_processing.utils.llm_configs import DIARIZATION_CONFIG, DIARIZATION_PROMPT
from tellme.call_processing.utils import gcs_utils
from .utils import vertexai_retry_logic


# Transcription costs in dollars per second
DEEPGRAM_COSTS = {
    'whisper-medium': 0.00007,
    'whisper-large': 0.00008
}
GROQ_COSTS = {
    'whisper-large-v3': 0.111 / 3600,
    'whisper-large-v3-turbo': 0.04 / 3600
}


class CallTranscriber:
    """
    Handles audio transcription and diarization for call processing.

    This class manages the conversion of audio files to text transcripts,
    including chunking, transcription via multiple providers, and speaker diarization.
    """

    def __init__(self, chunk_size=5.0, max_retries=5, base_delay=5.0, backoff_factor=2,
                 transcription_model_deepgram='whisper-medium',
                 transcription_model_groq='whisper-large-v3'):
        """
        Initialize the CallTranscriber with necessary clients and configuration.

        Args:
            chunk_size (float): Audio chunk size in minutes
            max_retries (int): Maximum retry attempts
            base_delay (float): Base delay for exponential backoff
            backoff_factor (int): Backoff multiplier
            transcription_model_deepgram (str): Deepgram model name
            transcription_model_groq (str): Groq model name

        Raises:
            RuntimeError: If required API keys are not found
        """
        # Initialize clients
        if not hasattr(settings, 'DEEPGRAM_API_KEY') or not settings.DEEPGRAM_API_KEY:
            raise RuntimeError("Deepgram API key not found. Please set the DEEPGRAM_API_KEY setting value.")
        self.deepgram = deepgram.DeepgramClient(settings.DEEPGRAM_API_KEY)

        if not hasattr(settings, 'GROQ_API_KEY') or not settings.GROQ_API_KEY:
            raise RuntimeError("Groq API key not found. Please set the GROQ_API_KEY setting value.")
        self.groq = groq.Groq(api_key=settings.GROQ_API_KEY)

        self.vertexai = genai.Client(
            vertexai=True,
            project=settings.GOOGLE_CLOUD_PROJECT,
            location='us-central1'
        )

        # Initialize transcription options
        self.transcription_options = deepgram.PrerecordedOptions(
            model=transcription_model_deepgram,
            smart_format=True,
            detect_language=True,
            punctuate=True,
            diarize=True,
        )

        # Initialize diarization prompt
        self.diarization_prompt = Langfuse().get_prompt(
            'call_diarization',
            label=[k for k in ['development', 'staging', 'production'] if settings.TELLME_ENV in k][0],
            fallback=DIARIZATION_PROMPT
        )

        self.chunk_size = chunk_size
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor
        self.transcription_model_deepgram = transcription_model_deepgram
        self.transcription_model_groq = transcription_model_groq

    @observe(capture_output=False)
    def transcribe(self, file_name: str, transcription_method: str) -> tuple[str, str, float]:
        """
        Handle the full transcription process for audio files.

        This method processes audio files by:
        1. Determining if the location is a directory or file
        2. Creating a list of target file paths
        3. Processing each file by splitting into chunks
        4. Transcribing each chunk
        5. Checking for consistent language detection
        6. Applying diarization if needed

        Args:
            file_name (str): The GCS path to audio file or directory
            transcription_method (str): Transcription method to use ('deepgram' or 'groq')

        Returns:
            tuple[str, str, float]: Full transcript, detected language, call duration in seconds

        Raises:
            Warning: If language changes across chunks
            ValueError: If transcription method is not supported
            RuntimeError: If file is empty or transcription fails
        """
        methods = {
            'deepgram': self.transcribe_chunk_with_deepgram,
            'groq': self.transcribe_chunk_with_groq
        }
        fallback_exceptions = {
            'deepgram': (ValueError, httpx.HTTPError, DeepgramApiError),
            'groq': (ValueError, httpx.HTTPError)
        }

        if transcription_method not in methods:
            raise ValueError(f'Provided transcription_method is not supported ({transcription_method})')

        fallback_name = [m for m in methods.keys() if m != transcription_method][0]
        fallback_exceptions = fallback_exceptions[transcription_method]

        # Determine target files
        if file_name.endswith('.wav'):
            target_paths = [file_name]
        else:
            target_paths = gcs_utils.list_files_in_gcs(file_name, '*.wav')

        total_duration = 0
        total_size = 0
        chunk_count = 0
        base_language = None
        full_transcript = ''
        go_to_fallback = False

        for path in target_paths:
            file_data = gcs_utils.download_from_gcs(path)

            if len(file_data) == 0:
                raise RuntimeError(f'File {path} is empty')

            recording_chunks, file_duration = self.cut_into_chunks(file_data)
            total_duration += file_duration
            total_size += len(file_data)
            chunk_count += len(recording_chunks)
            file_transcript = ''

            # Try primary method
            if not go_to_fallback:
                for chunk in recording_chunks:
                    try:
                        chunk_transcript, chunk_language = methods[transcription_method](chunk)
                    except fallback_exceptions:
                        base_language = None
                        file_transcript = ''
                        go_to_fallback = True
                        break

                    if not file_transcript:
                        base_language = chunk_language
                        file_transcript = chunk_transcript
                    else:
                        if base_language != chunk_language:
                            raise Warning(f'Language changed from {base_language} to {chunk_language}.')
                        file_transcript += '\n' + chunk_transcript

            # Fallback method
            if go_to_fallback:
                for chunk in recording_chunks:
                    try:
                        chunk_transcript, chunk_language = methods[fallback_name](chunk)
                    except Exception as e:
                        raise RuntimeError(f'Fallback transcription failed: {e}')

                    if not file_transcript:
                        base_language = chunk_language
                        file_transcript = chunk_transcript
                    else:
                        if base_language != chunk_language:
                            raise Warning(f'Language changed from {base_language} to {chunk_language}.')
                        file_transcript += '\n' + chunk_transcript

            full_transcript += ('\n' if full_transcript else '') + file_transcript

        if base_language is None:
            base_language = "unknown"

        # Apply diarization if transcription was done with Groq or fallback
        if transcription_method == 'groq' or (transcription_method != 'groq' and go_to_fallback):
            full_transcript = self.diarize_transcript(full_transcript)

        langfuse_context.update_current_trace(
            metadata={
                'chunk_count': chunk_count,
                'total_duration_minutes': round(total_duration / 60000, 2),
                'total_size_mbs': round(total_size / 1000000, 2)
            }
        )

        return full_transcript, base_language, total_duration / 1000

    def cut_into_chunks(self, file_data: bytes) -> tuple[list[bytes], int]:
        """
        Split audio data into chunks for processing.

        Args:
            file_data (bytes): Raw audio file data

        Returns:
            tuple[list[bytes], int]: List of audio chunks and original duration in milliseconds
        """
        audio = AudioSegment.from_file(BytesIO(file_data), format="wav")
        chunk_length_ms = int(self.chunk_size * 60 * 1000)
        chunks = []

        for start_ms in range(0, len(audio), chunk_length_ms):
            end_ms = start_ms + chunk_length_ms
            chunk = audio[start_ms:end_ms]
            chunk_buffer = BytesIO()
            chunk.export(chunk_buffer, format="wav")
            chunks.append(chunk_buffer.getvalue())

        return chunks, len(audio)

    @observe(as_type="generation")
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=2, exp_base=2, min=5.0),
        stop=stop_after_attempt(5),
        retry=retry_if_exception(
            lambda e: (isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429) or
                      (isinstance(e, DeepgramApiError) and e.status == '429')
        )
    )
    def transcribe_chunk_with_deepgram(self, chunk_data: bytes) -> tuple[str, str]:
        """
        Transcribe a single audio chunk using Deepgram API.

        Args:
            chunk_data (bytes): Raw binary data of the audio chunk

        Returns:
            tuple[str, str]: Transcript text and detected language

        Raises:
            httpx.HTTPError: If transcription fails after retries
            RuntimeError: If response cannot be parsed
        """
        payload = {'buffer': chunk_data}

        langfuse_context.update_current_observation(
            name="transcription_deepgram",
            start_time=datetime.now(),
        )

        response = None
        try:
            response = self.deepgram.listen.rest.v("1").transcribe_file(
                payload, self.transcription_options,
                timeout=httpx.Timeout(self.chunk_size * 60, connect=10.0)
            )

            transcript = response['results']['channels'][0]['alternatives'][0]['paragraphs']['transcript']
            transcript = transcript.replace("\n\n", "\n").strip()
            language = response['results']['channels'][0]['detected_language']
            cost = DEEPGRAM_COSTS[self.transcription_model_deepgram] * response['metadata']['duration']

            langfuse_context.update_current_observation(
                end_time=datetime.now(),
                input={"chunk_size_bytes": len(chunk_data), "chunk_size_seconds": response['metadata']['duration']},
                output={"transcript_chunk_size": len(transcript), "language": language},
                model=f'deepgram-{self.transcription_model_deepgram}',
                usage={'total': response['metadata']['duration'], 'unit': 'SECONDS', 'totalCost': cost}
            )
            return transcript, language

        except IndexError as e:
            langfuse_context.update_current_observation(status_message=str(e), level="ERROR")
            raise RuntimeError(f'Could not parse transcription response: {response}') from e
        except httpx.HTTPStatusError as e:
            langfuse_context.update_current_observation(status_message=str(e), level="ERROR")
            raise httpx.HTTPError("Failed to transcribe chunk after multiple retries.")

    @observe(as_type="generation")
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=2, exp_base=2, min=5.0),
        stop=stop_after_attempt(5),
        retry=retry_if_exception(lambda e: isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429)
    )
    def transcribe_chunk_with_groq(self, chunk_data: bytes) -> tuple[str, str]:
        """
        Transcribe a single audio chunk using Groq API.

        Args:
            chunk_data (bytes): Raw binary data of the audio chunk

        Returns:
            tuple[str, str]: Transcript text and detected language

        Raises:
            httpx.HTTPError: If transcription fails after retries
        """
        langfuse_context.update_current_observation(
            name="transcription_groq",
            start_time=datetime.now(),
        )

        try:
            response = self.groq.audio.transcriptions.create(
                file=('recording_chunk.wav', chunk_data),
                model=self.transcription_model_groq,
                response_format="verbose_json",
            )
            transcript = '\n'.join([f"Speaker X: {phrase['text']}" for phrase in response.segments])
            language = response.language

            langfuse_context.update_current_observation(
                end_time=datetime.now(),
                input={"chunk_size_bytes": len(chunk_data), "chunk_size_seconds": response.duration},
                output={"transcript_chunk_size": len(transcript), "language": language},
                model=f'groq-{self.transcription_model_groq}',
                usage={
                    'total': response.duration,
                    'unit': 'SECONDS',
                    'totalCost': GROQ_COSTS[self.transcription_model_groq] * response.duration
                }
            )

            return transcript, language

        except httpx.HTTPStatusError as e:
            langfuse_context.update_current_observation(status_message=str(e), level="ERROR")
            raise httpx.HTTPError("Failed to transcribe chunk after multiple retries.")

    @observe(as_type="generation", capture_output=False, capture_input=False)
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=2, exp_base=2, min=5.0),
        stop=stop_after_attempt(5),
        retry=retry_if_exception(vertexai_retry_logic)
    )
    def diarize_transcript(self, transcript: str) -> str:
        """
        Apply speaker diarization to transcript using Vertex AI.

        Args:
            transcript (str): Transcript to diarize

        Returns:
            str: Diarized transcript with speaker labels
        """
        # Prepare prompt and response format
        if self.diarization_prompt.is_fallback:
            config_kwargs = DIARIZATION_CONFIG
        else:
            config_kwargs = {'langfuse_prompt': self.diarization_prompt}
            config_kwargs.update(self.diarization_prompt.config)

        response = self.vertexai.models.generate_content(
            model=config_kwargs['model'],
            contents=f"This is the list of transcribed phrases:\n{transcript}",
            config=types.GenerateContentConfig(
                system_instruction=self.diarization_prompt.prompt,
                temperature=config_kwargs['temperature'],
            ),
        )

        # Send observation data to Langfuse
        langfuse_context.update_current_observation(
            name="diarization_vertexai",
            prompt=self.diarization_prompt,
            model=config_kwargs['model'],
            usage={
                "promptTokens": response.usage_metadata.prompt_token_count,
                "completionTokens": response.usage_metadata.candidates_token_count,
                "totalTokens": response.usage_metadata.total_token_count
            }
        )
        return response.candidates[0].content.parts[0].text