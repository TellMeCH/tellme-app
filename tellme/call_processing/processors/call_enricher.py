"""
CallEnricher handles AI-powered call analysis and enrichment.

This module contains all enrichment-related functionality including:
- Multi-step enrichment pipeline
- Speaker identification and customer info extraction
- Topic analysis, summarization, and sentiment assessment
"""

import json
import copy
import httpx
from django.conf import settings
from google import genai
from langfuse import openai, Langfuse
from google.genai import types, errors
from langfuse.decorators import observe, langfuse_context
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception, retry_if_exception_type

from tellme.call_processing.utils.llm_configs import ENRICHMENT_PIPELINE
from tellme.call_processing.utils import db_handler
from .utils import vertexai_retry_logic, create_customer_id


class CallEnricher:
    """
    Handles AI-powered call analysis and enrichment for call processing.

    This class manages the multi-step enrichment pipeline that includes
    speaker identification, topic analysis, summarization, and sentiment assessment.
    """

    def __init__(self, max_retries=5, base_delay=5.0, backoff_factor=2):
        """
        Initialize the CallEnricher with necessary clients and configuration.

        Args:
            max_retries (int): Maximum retry attempts
            base_delay (float): Base delay for exponential backoff
            backoff_factor (int): Backoff multiplier

        Raises:
            RuntimeError: If required API keys are not found
        """
        # Initialize OpenAI client
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            raise RuntimeError("OpenAI API key not found. Please set the OPENAI_API_KEY setting value.")
        else:
            openai.api_key = settings.OPENAI_API_KEY
        self.openai = openai.OpenAI()

        # Initialize Vertex AI client
        self.vertexai = genai.Client(vertexai=True, project=settings.GOOGLE_CLOUD_PROJECT, location='us-central1')

        # Initialize enrichment prompts
        self.enrichment_prompts = []
        enrichment_steps = len(ENRICHMENT_PIPELINE)
        for i in range(enrichment_steps):
            prompt = Langfuse().get_prompt(
                f'enrichment_{i}',
                label=[k for k in ['development', 'staging', 'production'] if settings.TELLME_ENV in k][0],
                fallback=ENRICHMENT_PIPELINE[i]['prompt']
            )
            self.enrichment_prompts.append(prompt)

        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor

    @observe(capture_input=False)
    def enrich_recording(self, transcript: str, redacted_transcript: str,
                        enrichment_method: str, organization_id: int) -> tuple[dict, int, int]:
        """
        Produce structured analytics for the call through multi-step enrichment.

        This method processes the call transcript through multiple AI-powered steps:
        1. Speaker identification and customer info extraction (on original transcript)
        2. Topic analysis, summarization, and sentiment assessment (on redacted transcript)

        Args:
            transcript (str): Original transcript text
            redacted_transcript (str): PII-redacted transcript text
            enrichment_method (str): AI provider to use ('openai' or 'vertexai')
            organization_id (int): Organization ID for topic retrieval

        Returns:
            tuple[dict, int, int]: Enrichment results, input tokens, output tokens

        Raises:
            ValueError: If enrichment method is not supported
            RuntimeError: If fallback enrichment also fails
        """
        go_to_fallback = False
        input_tokens, output_tokens = None, None
        enriched_response = {}
        fallback_exceptions = (ValueError, httpx.HTTPError, errors.ClientError)
        methods = {
            'openai': self.enrich_recording_with_openai,
            'vertexai': self.enrich_recording_with_vertexai
        }

        if enrichment_method not in methods:
            raise ValueError(f'Provided enrichment_method is not supported ({enrichment_method})')

        fallback_name = [m for m in methods.keys() if m != enrichment_method][0]

        # Retrieve relevant topic data for compilation
        compile_data = {
            "topics_string": db_handler.obtain_active_topics(organization_id),
            "suggested_string": db_handler.obtain_suggested_topics(organization_id)
        }

        # Process each enrichment step
        for i, step in enumerate(ENRICHMENT_PIPELINE):
            # Choose appropriate transcript
            conversation = redacted_transcript if step['uses_redacted'] else transcript

            # Prepare prompt with compilation data
            relevant_data = {key: compile_data[key] for key in step['to_compile'] if key in compile_data}
            system_message = self.enrichment_prompts[i].compile(**relevant_data)

            # Determine configuration source
            if self.enrichment_prompts[i].is_fallback:
                enrichment_config = step['config']
            else:
                enrichment_config = {'langfuse_prompt': self.enrichment_prompts[i]}
                enrichment_config.update(self.enrichment_prompts[i].config)

            # Configure for each provider
            configs = {}
            for method_name in methods.keys():
                configs[method_name] = copy.deepcopy(enrichment_config)
                configs[method_name]['model'] = configs[method_name]['model'][method_name]

                if method_name == 'openai':
                    # OpenAI requires additionalProperties: false on all object schemas
                    self._add_additional_properties_false(
                        configs[method_name]['response_format']['json_schema']['schema']
                    )

            # Execute primary method
            response = None
            try:
                response, input_tokens, output_tokens = methods[enrichment_method](
                    conversation, system_message, configs[enrichment_method], i
                )
            except fallback_exceptions:
                go_to_fallback = True

            # Execute fallback method if needed
            if go_to_fallback:
                try:
                    response, input_tokens, output_tokens = methods[fallback_name](
                        conversation, system_message, configs[fallback_name], i
                    )
                except Exception as e:
                    raise RuntimeError(f'Fallback enrichment method {fallback_name} failed: {e}')

            # Apply speaker label replacement if this step identified speakers
            if ('agent_speaker_labels' in response) and ('customer_speaker_labels' in response):
                response = self._replace_speaker_labels(redacted_transcript, response)
                redacted_transcript = response['transcript']

            # Accumulate results
            enriched_response.update(response)

        # Generate customer ID from extracted info and remove sensitive data
        if 'customer_info' in enriched_response:
            enriched_response['customer_id'] = create_customer_id(
                enriched_response['customer_info']['full_name'],
                enriched_response['customer_info']['birth_date']
            )
            del enriched_response['customer_info']

        return enriched_response, input_tokens, output_tokens

    @observe(as_type="generation", capture_input=False, capture_output=False)
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=2, exp_base=2, min=5.0),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(httpx.HTTPError)
    )
    def enrich_recording_with_openai(self, transcript: str, system_message: str,
                                   config: dict, step: int) -> tuple[dict, int, int]:
        """
        Call OpenAI Chat Completions endpoint in JSON schema mode.

        Args:
            transcript (str): Transcript to analyze
            system_message (str): System prompt for the AI model
            config (dict): OpenAI configuration including model and response format
            step (int): Current enrichment step number

        Returns:
            tuple[dict, int, int]: Parsed JSON response, input tokens, output tokens
        """
        langfuse_context.update_current_observation(
            name="enrichment_openai",
            prompt=self.enrichment_prompts[step]
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

    @observe(as_type="generation", capture_input=False, capture_output=False)
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=2, exp_base=2, min=5.0),
        stop=stop_after_attempt(5),
        retry=retry_if_exception(vertexai_retry_logic)
    )
    def enrich_recording_with_vertexai(self, transcript: str, system_message: str,
                                     config: dict, step: int) -> tuple[dict, int, int]:
        """
        Call Vertex AI (Gemini) in structured output mode.

        Args:
            transcript (str): Transcript to analyze
            system_message (str): System prompt for the AI model
            config (dict): Vertex AI configuration including model and response format
            step (int): Current enrichment step number

        Returns:
            tuple[dict, int, int]: Parsed JSON response, input tokens, output tokens
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
            prompt=self.enrichment_prompts[step],
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

    def _add_additional_properties_false(self, schema):
        """
        Recursively add 'additionalProperties': false to all object schemas.
        OpenAI's structured output requires this for strict mode.

        Args:
            schema: JSON schema object to modify
        """
        if isinstance(schema, dict):
            # If this is an object schema, add additionalProperties: false
            if schema.get('type') == 'object' and 'properties' in schema:
                schema['additionalProperties'] = False

            # Recursively process all values
            for key, value in schema.items():
                if isinstance(value, (dict, list)):
                    self._add_additional_properties_false(value)
        elif isinstance(schema, list):
            # Recursively process list items
            for item in schema:
                if isinstance(item, (dict, list)):
                    self._add_additional_properties_false(item)

        return schema

    @staticmethod
    def _replace_speaker_labels(transcript: str, data: dict) -> dict:
        """
        Apply identified speaker roles to the diarized transcript.

        Args:
            transcript (str): Original transcript with speaker labels
            data (dict): Response data containing speaker label mappings

        Returns:
            dict: Updated data with transcript containing <agent>/<customer> labels
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