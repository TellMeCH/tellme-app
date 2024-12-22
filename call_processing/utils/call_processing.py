import time
import hashlib
import json
from datetime import datetime
from io import BytesIO
from django.conf import settings
import deepgram
import httpx
from pydub import AudioSegment
from langfuse import openai
from openai.lib._parsing._completions import type_to_response_format_param
from pydantic import BaseModel
from langfuse.decorators import observe, langfuse_context
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception, retry_if_exception_type
from call_miner.models import Topic

DEEPGRAM_COSTS = {  # A dictionary of transcription costs in dollars per second
    'whisper-medium': 0.00007,
    'whisper-large': 0.00008
}


class EnrichmentResponse(BaseModel):
    """
    A Pydantic model that represents the response structure from the OpenAI API.
    Contains:
        - agent_speaker_labels: A list of speaker label strings that identify the agent in the conversation
        - customer_speaker_labels: A list of speaker label strings that identify the customer in the conversation
        - topics: A list of topic strings that classify the conversation.
        - summary: A string summarizing the key points of the conversation.
        - title: A string that represents the content of the call
        - sentiment: An integer that represents the overall sentiment of the call
    """
    agent_speaker_labels: list[str]
    customer_speaker_labels: list[str]
    topics: list[str]
    summary: str
    title: str
    sentiment: int


class CallProcessingPipeline:
    """
    A processing pipeline in charge of the transcription, diarization, and mining of call recording data.

    Steps:
    1. Splits the recording into CHUNK_SIZE minute segments.
    2. Transcribes each chunk with Deepgram.
    3. Ensures consistency in detected language across chunks.
    4. Logs the entire process in Langfuse for observability.

    Attributes:
        REQUIRED_METADATA_FIELDS (list of str): Required fields in recording metadata
        CHUNK_SIZE (float): Duration of each audio chunk in minutes.
        TRANSCRIPTION_MODEL_NAME (str): The name of the transcription model to use.
        API_MAX_RETRIES (int): Maximum retries per recording chunk when dealing with the Deepgram API
        API_BASE_DELAY (float): Base waiting time per recording chunk when dealing with the Deepgram API
        API_BACKOFF_FACTOR (int): Back-off factor per recording chunk when dealing with the Deepgram API
        ENRICHMENT_MODEL_NAME (str): Model name for enrichment step
        ENRICHMENT_PROMPT (str): System message to use during enrichment step
    """
    REQUIRED_METADATA_FIELDS: list[str] = ['file_name', 'organization', 'customer_id', 'agent_id', 'timestamp']
    CHUNK_SIZE: float = 5
    TRANSCRIPTION_MODEL_NAME: str = 'whisper-medium'
    API_MAX_RETRIES: int = 5
    API_BASE_DELAY: float = 1.0
    API_BACKOFF_FACTOR: int = 2
    ENRICHMENT_MODEL_NAME = 'gpt-4o-mini-2024-07-18'
    ENRICHMENT_PROMPT = """
        You have the task of summarizing and classifying transcribed calls between two speakers.
        One of the speakers in the call is an agent for a company, and the other speaker is a customer. 
        The different speakers are indicated by 'Speaker 0' and 'Speaker 1'.
        Follow these steps:

        1. Read through the transcribed dialogue. Identify which of the speakers is the company's agent (usually 
        'Speaker 0') and which one is the customer. For extra speaker labels (f.e. 'Speaker 2') that may be present in 
        the transcript, assume they are either the customer or the agent. Keep track of the speaker labels that 
        correspond to the agent and to the customer.
        2. Classify the dialogue into the following topics: {topics_string}. If none of these topics match, 
        simply return an empty list. Do not invent topics!
        3. Summarize the call paying attention to: the reason for the call, the topics discussed during the call, and
        the agreed upon next steps as a result of the call. Try to keep this summary to six sentences. Do not include 
        the names of customers or agents.
        4. Define a title that briefly captures the content of the call. Do not include names of customers or agents.
        5. Represent the overall call sentiment in a scale ranging from 1 to 5, where 5 is extremely positive, and 1 is
        completely hostile.
        4. The output must strictly be in a JSON format with keys "agent_speaker_labels", "customer_speaker_labels", 
        "topics", "summary", "title", and "sentiment". Do not add any text before or after the json.
    """

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
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        else:
            openai.api_key = settings.OPENAI_API_KEY
        self.openai = openai.OpenAI()

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
        for field in self.REQUIRED_METADATA_FIELDS:
            if field not in file_metadata:
                raise ValueError(f'Incorrect format for recording metadata. Missing field "{field}"')

        langfuse_context.update_current_trace(
            name="Call Processing",
            user_id='Cloud Task Manager',
            session_id=self.define_session_id(file_metadata),
            tags=[settings.TELLME_ENV],
            metadata=file_metadata
        )

        # Transcribe the audio file
        transcript, language = self.transcribe(file_data)

        if len(transcript) == 0:
            raise ValueError('Call Processing: Produced transcript is empty.')

        # Extract the active topics of the organization
        active_topics = self.obtain_active_topics(file_metadata['organization'])

        # Obtain additional information from the transcript
        enriched_data = self.enrich_recording(transcript, active_topics)

        return transcript, language

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
        combined_string = ''.join(file_metadata.values()) + current_epoch
        return hashlib.sha256(combined_string.encode()).hexdigest()

    @observe()
    def transcribe(self, file_data: bytes) -> (str, str):
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
        recording_chunks, total_duration = self.cut_into_chunks(file_data)
        langfuse_context.update_current_trace(
            metadata={
                'chunk_count': len(recording_chunks),
                'total_duration_minutes': round(total_duration / 60000, 2),
                'total_size_mbs': round(len(file_data) / 1000000, 2)
            }
        )

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
        retry=retry_if_exception(lambda e: isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429)
    )
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

        # Update Langfuse observation with input metadata
        langfuse_context.update_current_observation(
            name="Chunk Transcription with Deepgram",
            start_time=datetime.now(),
        )

        response = None
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
                input={"chunk_size_bytes": len(chunk_data), "chunk_size_seconds": response.metadata.duration},
                output={"transcript_preview": transcript[:100], "language": language},
                model=f'deepgram-{self.TRANSCRIPTION_MODEL_NAME}',
                usage={
                    'total': response.metadata.duration,
                    'unit': 'SECONDS',
                    'totalCost': DEEPGRAM_COSTS[self.TRANSCRIPTION_MODEL_NAME] * response.metadata.duration
                }
            )

            return transcript, language

        except IndexError as e:
            langfuse_context.update_current_observation(status_message=str(e), level="ERROR")
            raise ValueError(f'Could not parse transcription response: {json.dumps(response, indent=4)}') from e
        except httpx.HTTPStatusError as e:
            langfuse_context.update_current_observation(status_message=str(e), level="ERROR")
            raise httpx.HTTPError("Failed to transcribe chunk after multiple retries.")

    @staticmethod
    def obtain_active_topics(organization: int):
        """
        Query the call_miner data model to extract all active topics from the organization.

        Args:
            organization (int): ID of the organization to query

        Returns:
            str: A string enumerating the names and descriptions of all active topics
        """
        active_topics = ''
        for topic in Topic.objects.filter(organization=organization, is_active=True):
            active_topics += f'{topic.name}: {topic.description}, '
        return active_topics

    @observe()
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=API_BACKOFF_FACTOR, exp_base=2, min=API_BASE_DELAY),
        stop=stop_after_attempt(API_MAX_RETRIES),
        retry=retry_if_exception_type(httpx.HTTPError)
    )
    def enrich_recording(self, transcript: str, topic_data: str):
        """
        Call OpenAI to obtain additional information from the call transcript. Uses the topic data string to complete
        the prompt's system message.

        Args:
            transcript (str): Call transcript from which to extract information
            topic_data (str): String numerating names and descriptions of all active topics

        Returns:
            dict[str, str]: Results of enrichment, defined according to EnrichmentResponse
        """
        langfuse_context.update_current_observation(
            name="Recording Enrichment with OpenAI",
            model=self.ENRICHMENT_MODEL_NAME,
        )
        system_message = self.ENRICHMENT_PROMPT.format(topics_string=topic_data)
        completion = self.openai.chat.completions.create(
            model=self.ENRICHMENT_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Here is the call transcript:\n{transcript}"}
            ],
            response_format=type_to_response_format_param(EnrichmentResponse),
            temperature=0.2,
        )

        response = completion.choices[0].message
        return json.loads(response.content)
