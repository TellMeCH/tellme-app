import time
import hashlib
from datetime import datetime
from django.conf import settings
from langfuse.decorators import observe, langfuse_context

from tellme.call_processing.utils.llm_configs import (
    TRANSCRIPTION_METHOD_CHOICES, CUSTOMER_IDENTIFICATION_METHOD_CHOICES
)
from tellme.call_processing.processors import CallTranscriber, CallRedactor, CallEnricher, CallValuer



class CallProcessingPipeline:
    """
    Orchestrates the end-to-end processing of a call recording from audio ingestion all the way to an enriched,
    redacted, speaker-labeled transcript with analytics and revenue estimation.

    This pipeline coordinates four specialized processor modules:
    - CallTranscriber: Handles audio chunking, transcription (Deepgram/Groq), and diarization (Vertex AI)
    - CallRedactor: Manages PII redaction via Google Cloud DLP and customer ID extraction
    - CallEnricher: Performs AI-powered analysis including topic identification, summarization, and sentiment
    - CallValuer: Estimates revenue at stake by analyzing product mentions and pricing

    High-level workflow:
    1. Transcription: Convert audio to text with language detection and speaker diarization
    2. Redaction: Remove sensitive information and optionally extract customer identifiers
    3. Enrichment: Generate call analytics including summary, topics, sentiment, and speaker roles
    4. Revenue Analysis: Extract product search queries and estimate revenue at stake
    5. Observability: All network calls are traced with Langfuse for monitoring and debugging

    The pipeline is stateless and delegates all processing to the specialized modules, which handle
    their own client initialization, retry logic, and provider fallbacks.
    """


    def __init__(self):
        """
        Initializes the call processing pipeline with specialized processor modules.

        Each processor module (CallTranscriber, CallRedactor, CallEnricher, CallValuer) handles its own
        client initialization and configuration, including API keys and service setup.

        Raises:
            RuntimeError: If required API keys are not found in Django settings.
        """

        # Initialize processing modules
        self.transcriber = CallTranscriber()

        self.redacter = CallRedactor()

        self.enricher = CallEnricher()

        self.valuer = CallValuer()

    @observe()
    def __call__(
        self,
        file_name: str,
        organization_id: int,
        agent_id: int,
        timestamp: datetime,
        transcription_method: str = 'deepgram',
        enrichment_method: str = 'openai',
        customer_id: str = None,
        customer_identification_method: str = 'enrichment',
    ) -> dict:
        """
        Executes the full call processing pipeline for a given audio file and call metadata.

        This method orchestrates the end-to-end pipeline, including:
          - Transcription of the audio file using Deepgram or Groq (as a fallback),
          - Diarization of the transcript if not natively included,
          - Redaction of sensitive information via Google DLP,
          - Enrichment of the transcript with call summary, topics, sentiment, etc., using OpenAI,
          - Revenue estimation via product search and price analysis using CallValuer,
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
                - 'revenue_at_stake' (float): Estimated revenue value for products discussed in the call.
                - 'product_url' (str): URL of the product page analyzed for revenue estimation.
                - Plus all original call metadata (file_name, organization_id, customer_id, agent_id, timestamp).

        Raises:
            ValueError: If the transcription output is empty or an API key is missing.
            Warning: If detected language changes between audio chunks.
            Exception: If fallback transcription also fails.
        """

        if transcription_method not in [method[0] for method in TRANSCRIPTION_METHOD_CHOICES]:
            raise ValueError(f'Invalid Transcription Method ({transcription_method})')
        if customer_identification_method not in [method[0] for method in CUSTOMER_IDENTIFICATION_METHOD_CHOICES]:
            raise ValueError(f'Invalid Customer Identification Method ({customer_identification_method})')

        if customer_id is None:
            extract_customer_id = True
        else:
            extract_customer_id = False

        file_metadata = {
            "file_name": file_name,
            "organization_id": organization_id,
            "agent_id": agent_id,
            "timestamp": timestamp
        }
        if not extract_customer_id:
            file_metadata['customer_id'] = customer_id

        langfuse_context.update_current_trace(
            name="Call Processing",
            user_id='Cloud Task Manager',
            session_id=self.define_session_id(file_metadata),
            tags=[settings.TELLME_ENV],
            metadata=file_metadata
        )

        # Transcribe the audio file
        transcript, language, total_duration = self.transcriber.transcribe(file_name, transcription_method)

        if len(transcript) == 0:
            raise RuntimeError('Call Processing: Produced transcript is empty.')

        # Redact sensitive information
        customer_from_redaction = extract_customer_id and (customer_identification_method == 'redaction')
        redacted_transcript, customer_id = self.redacter.redact_transcript(transcript, customer_from_redaction)

        if customer_from_redaction:
            file_metadata['customer_id'] = customer_id

        # Obtain additional information from the transcript
        enriched_data, input_tokens, output_tokens = self.enricher.enrich_recording(
            transcript,
            redacted_transcript,
            enrichment_method,
            file_metadata['organization_id']
        )

        # Calculate revenue at stake
        revenue, product_url = None, None
        if 'revenue_search_query' in enriched_data:
            revenue, product_url = self.valuer(enriched_data['revenue_search_query'], file_metadata['organization_id'])

        enriched_data['language'] = language
        enriched_data['input_tokens'] = input_tokens
        enriched_data['output_tokens'] = output_tokens
        enriched_data['duration'] = total_duration
        enriched_data['revenue_at_stake'] = revenue
        enriched_data['product_url'] = product_url
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
