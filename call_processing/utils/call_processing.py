import time
import hashlib
import json
import copy
from datetime import datetime
from io import BytesIO
from django.conf import settings
import deepgram
import groq
import httpx
import google.cloud.dlp
from google import genai
from google.genai import types, errors
from pydub import AudioSegment
from langfuse import openai, Langfuse
from langfuse.decorators import observe, langfuse_context
from deepgram.clients.common.v1.errors import DeepgramApiError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception, retry_if_exception_type
from call_processing.utils.llm_configs import (
    TRANSCRIPTION_METHOD_CHOICES, DIARIZATION_PROMPT, DIARIZATION_CONFIG, ENRICHMENT_PROMPT, ENRICHMENT_CONFIG
)
from call_processing.utils import gcs_utils, db_handler

# Transcription costs in dollars per second
DEEPGRAM_COSTS = {
    'whisper-medium': 0.00007,
    'whisper-large': 0.00008
}
GROQ_COSTS = {
    'whisper-large-v3': 0.111 / 3600,
    'whisper-large-v3-turbo': 0.04 / 3600
}


class CallProcessingPipeline:
    """
    Orchestrates the end-to-end processing of a call recording from audio ingestion all the way to an enriched, 
    redacted, speaker-labeled transcript with analytics.

    High-level workflow:
    1. Chunking: split recording into `CHUNK_SIZE`-minute blocks.  
    2. Transcription: Deepgram (primary) ➔ Groq (fallback).  
    3. Language check: ensure all chunks share the same detected language.  
    4. Optional diarization: Gemini if the model did not diarize natively.  
    5. Redaction: Google Cloud DLP removes PII.  
    6. Enrichment: OpenAI or Gemini adds summary, topics, sentiment, …  
    7. Post-processing: replace original speaker labels with `<agent>` /
       `<customer>` tokens.  
    8. Observability: every network call is traced with Langfuse.

    Attributes:
    CHUNK_SIZE : float
        Length of each audio chunk, in minutes.
    TRANSCRIPTION_MODEL_NAME_DEEPGRAM : str
        Model used when transcribing with Deepgram.
    TRANSCRIPTION_MODEL_NAME_GROQ : str
        Model used when transcribing with Groq.
    API_MAX_RETRIES : int
        Max retry attempts for any network call in the pipeline.
    API_BASE_DELAY : float
        Initial back-off delay (seconds) for retry logic.
    API_BACKOFF_FACTOR : int
        Multiplier for exponential back-off.
    DLP_ENTITY_TYPES : list[str]
        Sensitive entities that should be redacted via DLP.
    """
    CHUNK_SIZE: float = 5
    TRANSCRIPTION_MODEL_NAME_DEEPGRAM: str = 'whisper-medium'
    TRANSCRIPTION_MODEL_NAME_GROQ: str = 'whisper-large-v3'
    API_MAX_RETRIES: int = 5
    API_BASE_DELAY: float = 5.0
    API_BACKOFF_FACTOR: int = 2
    DLP_ENTITY_TYPES: list[str] = ["EMAIL_ADDRESS", "PERSON_NAME", "PHONE_NUMBER", "CREDIT_CARD_NUMBER", "LOCATION", "IBAN_CODE", "PASSPORT"]

    def __init__(self) -> None:
        """
        Initializes the pipeline by setting up the Deepgram client and transcription options, the Groq client, as well
        as the Open AI client and prompt.

        Raises:
            ValueError: If the DEEPGRAM_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY is not set in the django settings.
        """
        # Deepgram
        if not hasattr(settings, 'DEEPGRAM_API_KEY') or not settings.DEEPGRAM_API_KEY:
            raise RuntimeError("Deepgram API key not found. Please set the DEEPGRAM_API_KEY setting value.")
        self.deepgram = deepgram.DeepgramClient(settings.DEEPGRAM_API_KEY)
        self.transcription_options = deepgram.PrerecordedOptions(
            model=self.TRANSCRIPTION_MODEL_NAME_DEEPGRAM,
            smart_format=True,
            detect_language=True,
            punctuate=True,
            diarize=True,
        )

        # Groq
        if not hasattr(settings, 'GROQ_API_KEY') or not settings.GROQ_API_KEY:
            raise RuntimeError("Groq API key not found. Please set the OPENAI_API_KEY setting value.")
        self.groq = groq.Groq(api_key=settings.GROQ_API_KEY)

        # VertexAI
        self.vertexai = genai.Client(vertexai=True, project=settings.GOOGLE_CLOUD_PROJECT, location='us-central1')

        # OpenAI
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            raise RuntimeError("OpenAI API key not found. Please set the OPENAI_API_KEY setting value.")
        else:
            openai.api_key = settings.OPENAI_API_KEY
        self.openai = openai.OpenAI()

        # Prompts with Fallback
        self.diarization_prompt = Langfuse().get_prompt(
            'call_diarization',
            label=[k for k in ['development', 'staging', 'production'] if settings.TELLME_ENV in k][0],
            fallback=DIARIZATION_PROMPT
        )
        self.enrichment_prompt = Langfuse().get_prompt(
            'call_enrichment',
            label=[k for k in ['development', 'staging', 'production'] if settings.TELLME_ENV in k][0],
            fallback=ENRICHMENT_PROMPT
        )

        # Configuration for DLP
        self.dlp_client = google.cloud.dlp_v2.DlpServiceClient()
        self.dlp_config = {
            "parent": f"projects/{settings.GOOGLE_CLOUD_PROJECT}/locations/global",
            "deidentify_config": {
                "info_type_transformations": {
                    "transformations": [
                        {"primitive_transformation": {"replace_with_info_type_config": {}}}
                    ]
                }
            },
            "inspect_config": {"info_types": [{"name": info_type} for info_type in self.DLP_ENTITY_TYPES]}
        }

    @observe()
    def __call__(
            self,
            file_name: str,
            organization_id: int,
            customer_id: str,
            agent_id: int,
            timestamp: datetime,
            transcription_method: str = 'deepgram',
            enrichment_method: str = 'openai'
    ) -> dict:
        """
        Executes the full call processing pipeline for a given audio file and call metadata.

        This method orchestrates the end-to-end pipeline, including:
          - Transcription of the audio file using Deepgram or Groq (as a fallback),
          - Diarization of the transcript if not natively included,
          - Redaction of sensitive information via Google DLP,
          - Enrichment of the transcript with call summary, topics, sentiment, etc., using OpenAI,
          - Replacement of speaker labels with standardized role markers,
          - Logging and traceability through Langfuse.

        Decorated with @observe(), it creates a top-level Langfuse trace.

        Args:
            file_name (str): GCS path to the audio file or folder containing call recordings.
            organization_id (int): ID of the organization initiating the call.
            customer_id (str): Unique identifier for the customer involved in the call.
            agent_id (int): Unique identifier for the agent handling the call.
            timestamp (datetime): The timestamp indicating when the call took place.
            transcription_method (str): Indicates what transcription method to use
            enrichment_method (str): Indicates what method to use for call summarization and topic modelling

        Returns:
            dict: A dictionary containing the complete enriched result, including:
                - 'transcript' (str): Final (redacted + diarized) call transcript.
                - 'language' (str): Detected primary spoken language.
                - 'duration' (float): Call duration in seconds.
                - 'agent_speaker_labels' (list): Original speaker labels assigned to the agent.
                - 'customer_speaker_labels' (list): Original speaker labels assigned to the customer.
                - 'topics' (list): List of detected topics relevant to the call.
                - 'summary' (str): AI-generated summary of the conversation.
                - 'call_title' (str): AI-generated call title.
                - 'sentiment' (str): Overall sentiment classification of the conversation.
                - 'input_tokens' (int): Number of tokens used in the enrichment prompt.
                - 'output_tokens' (int): Number of tokens generated by the enrichment model.
                - Plus all original call metadata (file_name, organization_id, customer_id, agent_id, timestamp).

        Raises:
            ValueError: If the transcription output is empty or an API key is missing.
            Warning: If detected language changes between audio chunks.
            Exception: If fallback transcription also fails.
        """

        if transcription_method not in [method[0] for method in TRANSCRIPTION_METHOD_CHOICES]:
            raise ValueError(f'Invalid Transcription Method ({transcription_method})')

        file_metadata = {
            "file_name": file_name,
            "organization_id": organization_id,
            "customer_id": customer_id,
            "agent_id": agent_id,
            "timestamp": timestamp
        }
        langfuse_context.update_current_trace(
            name="Call Processing",
            user_id='Cloud Task Manager',
            session_id=self.define_session_id(file_metadata),
            tags=[settings.TELLME_ENV],
            metadata=file_metadata
        )

        # Transcribe the audio file
        transcript, language, total_duration = self.transcribe(file_name, transcription_method)

        if len(transcript) == 0:
            raise RuntimeError('Call Processing: Produced transcript is empty.')

        # Redact sensitive information
        transcript = self.redact_transcript(transcript)

        # Obtain additional information from the transcript
        enriched_data, input_tokens, output_tokens = self.enrich_recording(
            transcript,
            enrichment_method,
            file_metadata['organization_id']
        )

        # Replace speaker labels
        enriched_data = self.replace_speaker_labels(transcript, enriched_data)

        enriched_data['language'] = language
        enriched_data['input_tokens'] = input_tokens
        enriched_data['output_tokens'] = output_tokens
        enriched_data['duration'] = total_duration
        enriched_data.update(file_metadata)
        return enriched_data

    @staticmethod
    def define_session_id(file_metadata: dict[str, str]) -> str:
        """
        Define a unique session ID to propagate through all processing traces, based on the file metadata and current
        time.

        Args:
            file_metadata (dict[str, str]): Contains file metadata

        Returns:
            str: Session ID of the processing routine
        """
        current_epoch = str(int(time.time()))
        combined_string = ''.join([str(v) for v in file_metadata.values()]) + current_epoch
        return hashlib.sha256(combined_string.encode()).hexdigest()

    @observe(capture_output=False)
    def transcribe(self, file_name: str, transcription_method: str) -> (str, str, float):
        """
        Internal method to handle the full transcription process:
        1. Checks to see whether the provided location is a directory or a file
        2. Creates a list of target paths of files to transcribe
        3. Processes each file separately, splitting it into chunks
        2. Transcribes each chunk.
        3. Checks for consistent language detection.

        Args:
            file_name (str): The audio location in GCS
            transcription_method (str): Indicates what transcription method to use

        Returns:
            Tuple[str, str, float]: The full transcript, the detected base language and the call duration in seconds.

        Raises:
            Warning: If language changes across chunks.
            ValueError: If provided transcription method is not supported
        """
        methods = {'deepgram': self.transcribe_chunk_with_deepgram, 'groq': self.transcribe_chunk_with_groq}
        fallback_exceptions = {
            'deepgram': (ValueError, httpx.HTTPError, DeepgramApiError),
            'groq': (ValueError, httpx.HTTPError)
        }

        if transcription_method not in methods:
            raise ValueError(f'Provided transcription_method is not supported ({transcription_method})')
        else:
            fallback_name = [m for m in methods.keys() if m != transcription_method][0]
            fallback_exceptions = fallback_exceptions[transcription_method]

        # Hierarchy: file > chunk
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

            for i, chunk in enumerate(recording_chunks):
                try:
                    chunk_transcript, chunk_language = methods[transcription_method](chunk)
                except fallback_exceptions:
                    base_language = None
                    full_transcript = ''
                    go_to_fallback = True
                    break
                if not full_transcript:
                    base_language = chunk_language
                    full_transcript = chunk_transcript
                else:
                    if base_language != chunk_language:
                        raise Warning(f'Detected language changed suddenly from {base_language} to {chunk_language}.')
                    full_transcript += '\n' + chunk_transcript

            if go_to_fallback:
                for i, chunk in enumerate(recording_chunks):
                    try:
                        chunk_transcript, chunk_language = methods[fallback_name](chunk)
                    except Exception as e:
                        raise RuntimeError(f'Could not proceed with fallback transcription method. Stack trace:\n{e}')
                    if not full_transcript:
                        base_language = chunk_language
                        full_transcript = chunk_transcript
                    else:
                        if base_language != chunk_language:
                            raise Warning(f'Detected language changed suddenly from {base_language} to {chunk_language}.')
                        full_transcript += '\n' + chunk_transcript

            if base_language is None:
                base_language = "unknown"

        # Lastly, apply diarization if transcription was done with groq
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

    def cut_into_chunks(self, file_data: bytes) -> (list[bytes], int):
        """
        Splits the provided audio data into CHUNK_SIZE minute segments using pydub.

        Args:
            file_data (bytes): The raw audio file data.

        Returns:
            List[bytes]: A list of chunks in bytes format.
            int: Raw audio file length in milliseconds
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
            chunk_buffer = BytesIO()
            chunk.export(chunk_buffer, format="wav")
            chunks.append(chunk_buffer.getvalue())

        return chunks, len(audio)

    @observe(as_type="generation")
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=API_BACKOFF_FACTOR, exp_base=2, min=API_BASE_DELAY),
        stop=stop_after_attempt(API_MAX_RETRIES),
        retry=retry_if_exception(
            lambda e: (isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429) or
                      (isinstance(e, DeepgramApiError) and e.status == '429')
        )
    )
    def transcribe_chunk_with_deepgram(self, chunk_data: bytes) -> (str, str):
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

        # Update Langfuse observation with input metadata
        langfuse_context.update_current_observation(
            name="transcription_deepgram",
            start_time=datetime.now(),
        )

        response = None
        try:
            response = self.deepgram.listen.rest.v("1").transcribe_file(
                payload, self.transcription_options, timeout=httpx.Timeout(self.CHUNK_SIZE * 60, connect=10.0)
            )

            transcript = response['results']['channels'][0]['alternatives'][0]['paragraphs']['transcript']
            transcript = transcript.replace("\n\n", "\n").strip()
            language = response['results']['channels'][0]['detected_language']
            cost = DEEPGRAM_COSTS[self.TRANSCRIPTION_MODEL_NAME_DEEPGRAM] * response['metadata']['duration']

            # Update observation with results
            langfuse_context.update_current_observation(
                end_time=datetime.now(),
                input={"chunk_size_bytes": len(chunk_data), "chunk_size_seconds": response['metadata']['duration']},
                output={"transcript_chunk_size": len(transcript), "language": language},
                model=f'deepgram-{self.TRANSCRIPTION_MODEL_NAME_DEEPGRAM}',
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
        wait=wait_exponential(multiplier=API_BACKOFF_FACTOR, exp_base=2, min=API_BASE_DELAY),
        stop=stop_after_attempt(API_MAX_RETRIES),
        retry=retry_if_exception(lambda e: isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429)
    )
    def transcribe_chunk_with_groq(self, chunk_data: bytes) -> (str, str):
        """
        Transcribes a single audio chunk using the Groq Speech API, with exponential backoff on 429 responses.

        Decorated with @observe() so each chunk call is a child observation under the main trace.
        This allows you to associate each chunk call to Groq with a separate observation in Langfuse.

        Args:
            chunk_data (bytes): The raw binary data of the audio chunk.

        Returns:
            Tuple[str, str]: The transcript text and detected language for this chunk.

        Raises:
            httpx.HTTPError: If transcription fails after multiple retries.
        """
        langfuse_context.update_current_observation(
            name="transcription_groq",
            start_time=datetime.now(),
        )

        try:
            response = self.groq.audio.transcriptions.create(
              file=('recording_chunk.wav', chunk_data),
              model=self.TRANSCRIPTION_MODEL_NAME_GROQ,
              response_format="verbose_json",
            )
            transcript = '\n'.join([f"Speaker X: {phrase['text']}" for phrase in response.segments])
            language = response.language

            # Update observation with results
            langfuse_context.update_current_observation(
                end_time=datetime.now(),
                input={"chunk_size_bytes": len(chunk_data), "chunk_size_seconds": response.duration},
                output={"transcript_chunk_size": len(transcript), "language": language},
                model=f'groq-{self.TRANSCRIPTION_MODEL_NAME_GROQ}',
                usage={
                    'total': response.duration,
                    'unit': 'SECONDS',
                    'totalCost': GROQ_COSTS[self.TRANSCRIPTION_MODEL_NAME_GROQ] * response.duration
                }
            )

            return transcript, language

        except httpx.HTTPStatusError as e:
            langfuse_context.update_current_observation(status_message=str(e), level="ERROR")
            raise httpx.HTTPError("Failed to transcribe chunk after multiple retries.")

    @staticmethod
    def vertexai_retry_logic(error):
        """
        Centralised predicate for tenacity retries on Vertex AI calls.

        Returns ``True`` for HTTP 429s raised by either *httpx* or the
        `google-genai` SDK, allowing the decorator to back off and retry.
        """
        case_1 = isinstance(error, httpx.HTTPStatusError) and error.response.status_code == 429
        case_2 = isinstance(error, errors.ClientError) and error.code == 429
        return case_1 or case_2

    @observe(as_type="generation")
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=API_BACKOFF_FACTOR, exp_base=2, min=API_BASE_DELAY),
        stop=stop_after_attempt(API_MAX_RETRIES),
        retry=retry_if_exception(vertexai_retry_logic)
    )
    def diarize_transcript(self, transcript: str) -> str:
        """
        Call Gemini to diarize the transcript, in case the transcription did not include this step

        Args:
            transcript (str): Call transcript from which to extract information

        Returns:
            str: Diarized transcript
        """
        # Prepare Prompt and Response Format
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

    @observe(as_type="generation")
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=API_BACKOFF_FACTOR, exp_base=2, min=API_BASE_DELAY),
        stop=stop_after_attempt(API_MAX_RETRIES),
        retry=retry_if_exception(lambda e: isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429)
    )
    def redact_transcript(self, transcript: str) -> str:
        """
        Remove sensitive information from the obtained transcript using the Google Cloud DLP API

        Args:
            transcript (str): The transcript text

        Returns:
            str: Redacted transcript
        """
        # Update Langfuse observation with input metadata
        langfuse_context.update_current_observation(
            name="redaction_google_dlp",
            start_time=datetime.now(),
        )

        current_request = self.dlp_config.copy()
        current_request["item"] = {"value": transcript}
        response = self.dlp_client.deidentify_content(request=current_request)
        redacted_transcript = response.item.value

        # Update observation with results
        langfuse_context.update_current_observation(
            end_time=datetime.now(),
            input={"transcript_size": len(transcript)},
            output={"redacted_transcript": redacted_transcript},
            model=f'dlp-service-client'
        )
        return redacted_transcript

    @observe
    def enrich_recording(self, transcript: str, enrichment_method: str, organization_id: int):
        """
        Produce structured analytics for the call (`summary`, `topics`, …).

        A schema-constrained JSON response is requested from either OpenAI (GPT-4o mini) or Gemini, with automatic
        fail-over to the other provider on retriable errors.

        Returns:
            enrichment: dict
            input_tokens: int
            output_tokens: int
        """
        # Retrieve relevant topic data
        topic_data = db_handler.obtain_active_topics(organization_id)

        # Prepare Prompt and Response Format
        system_message = self.enrichment_prompt.compile(topics_string=topic_data)
        if self.enrichment_prompt.is_fallback:
            enrichment_config = ENRICHMENT_CONFIG
        else:
            enrichment_config = {'langfuse_prompt': self.enrichment_prompt}
            enrichment_config.update(self.enrichment_prompt.config)

        fallback_exceptions = (ValueError, httpx.HTTPError, errors.ClientError)
        methods = {'openai': self.enrich_recording_with_openai, 'vertexai': self.enrich_recording_with_vertexai}

        # Define enrichment configs per provider
        configs = {}
        for meth in methods.keys():
            configs[meth] = copy.deepcopy(enrichment_config)
            configs[meth]['model'] = configs[meth]['model'][meth]

            if meth == 'openai':
                configs[meth]['response_format']['json_schema']['schema']['additionalProperties'] = False

        if enrichment_method not in methods:
            raise ValueError(f'Provided enrichment_method is not supported ({enrichment_method})')
        else:
            fallback_name = [m for m in methods.keys() if m != enrichment_method][0]

        go_to_fallback = False
        response = None
        input_tokens = None
        output_tokens = None
        try:
            response, input_tokens, output_tokens = methods[enrichment_method](
                transcript,
                system_message,
                configs[enrichment_method]
            )
        except fallback_exceptions:
            go_to_fallback = True

        if go_to_fallback:
            try:
                response, input_tokens, output_tokens = methods[fallback_name](
                    transcript,
                    system_message,
                    configs[fallback_name]
                )
            except Exception as e:
                raise RuntimeError(f'Could not proceed with fallback enrichment method {fallback_name}. Trace:\n{e}')

        return response, input_tokens, output_tokens

    @observe(as_type="generation")
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=API_BACKOFF_FACTOR, exp_base=2, min=API_BASE_DELAY),
        stop=stop_after_attempt(API_MAX_RETRIES),
        retry=retry_if_exception_type(httpx.HTTPError)
    )
    def enrich_recording_with_openai(self, transcript: str, system_message: str, config: dict) -> (dict, int, int):
        """
        Internal helper that calls the OpenAI Chat Completions endpoint in JSON schema mode.

        The function is wrapped in exponential back-off that retries on network errors and rate limits
        (`httpx.HTTPError`).
        """
        langfuse_context.update_current_observation(
            name="enrichment_openai",
            prompt=self.enrichment_prompt
        )
        completion = self.openai.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Here is the call transcript:\n{transcript}"}
            ],
            **config
        )

        response = completion.choices[0].message
        input_tokens = completion.usage.prompt_tokens
        output_tokens = completion.usage.completion_tokens
        return json.loads(response.content), input_tokens, output_tokens

    @observe(as_type="generation")
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=API_BACKOFF_FACTOR, exp_base=2, min=API_BASE_DELAY),
        stop=stop_after_attempt(API_MAX_RETRIES),
        retry=retry_if_exception(vertexai_retry_logic)
    )
    def enrich_recording_with_vertexai(self, transcript: str, system_message: str, config: dict) -> (dict, int, int):
        """
        Same enrichment as above but executed on Gemini (Vertex AI).

        The call is made in *structured output* mode by passing both `response_mime_type="application/json"` and the
        OpenAPI-compatible `response_schema` to `GenerateContentConfig`.
        """
        generation = self.vertexai.models.generate_content(
            model=config['model'],
            contents=f"Here is the call transcript:\n{transcript}",
            config=types.GenerateContentConfig(
                system_instruction=system_message,
                temperature=config['temperature'],
                response_mime_type="application/json",
                response_schema=config["response_format"]["json_schema"]["schema"]
            ),
        )

        # Send observation data to Langfuse
        langfuse_context.update_current_observation(
            name="enrichment_vertexai",
            prompt=self.enrichment_prompt,
            model=config['model'],
            usage={
                "promptTokens": generation.usage_metadata.prompt_token_count,
                "completionTokens": generation.usage_metadata.candidates_token_count,
                "totalTokens": generation.usage_metadata.total_token_count
            }
        )

        response = generation.candidates[0].content.parts[0].text
        input_tokens = generation.usage_metadata.prompt_token_count
        output_tokens = generation.usage_metadata.candidates_token_count
        return json.loads(response), input_tokens, output_tokens

    @staticmethod
    def replace_speaker_labels(transcript: str, data: dict) -> dict:
        """
        Apply the identified speaker roles to the diarized transcript, by replacing speaker labels
        """
        speaker_types = {'agent_speaker_labels': '<agent>', 'customer_speaker_labels': '<customer>'}
        for label_type, new_label in speaker_types.items():
            for old_label in data[label_type]:
                if ':' in old_label:
                    transcript = transcript.replace(old_label, new_label + ':')
                else:
                    transcript = transcript.replace(old_label, new_label)
        data['transcript'] = transcript
        return data
