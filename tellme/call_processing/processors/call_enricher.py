"""
CallEnricher handles AI-powered call analysis and enrichment.

This module contains all enrichment-related functionality including:
- Multi-step enrichment pipeline
- Speaker identification and customer info extraction
- Topic analysis, summarization, and sentiment assessment
"""

import json
import litellm
from django.conf import settings
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context

from tellme.call_processing.utils.llm_configs import ENRICHMENT_PIPELINE
from tellme.call_processing.utils.litellm_config import setup_litellm, get_enrichment_config
from tellme.call_processing.utils import db_handler
from .utils import create_customer_id


class CallEnricher:
    """
    Handles AI-powered call analysis and enrichment for call processing.

    This class manages the multi-step enrichment pipeline that includes
    speaker identification, topic analysis, summarization, and sentiment assessment.
    """

    def __init__(self):
        """
        Initialize the CallEnricher with LiteLLM configuration.

        Raises:
            RuntimeError: If required API keys are not found
        """
        # Setup LiteLLM with Langfuse integration and retry settings
        setup_litellm()

        # Validate required API keys
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            raise RuntimeError("OpenAI API key not found. Please set the OPENAI_API_KEY setting value.")

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

    @observe()
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
        input_tokens, output_tokens = None, None
        enriched_response = {}

        if enrichment_method not in ['openai', 'vertexai']:
            raise ValueError(f'Provided enrichment_method is not supported ({enrichment_method})')

        # Retrieve relevant topic data for compilation
        compile_data = {
            "topics_string": db_handler.obtain_active_topics(organization_id),
            "suggested_string": db_handler.obtain_suggested_topics(organization_id),
            "organization_language": db_handler.retrieve_organization_language(organization_id)
        }

        # Process each enrichment step
        for i, step in enumerate(ENRICHMENT_PIPELINE):
            # Choose appropriate transcript
            conversation = redacted_transcript if step['uses_redacted'] else transcript

            # Prepare prompt with compilation data
            relevant_data = {key: compile_data[key] for key in step['to_compile'] if key in compile_data}
            system_message = self.enrichment_prompts[i].compile(**relevant_data)

            # Get LiteLLM fallback configuration
            litellm_config = get_enrichment_config(enrichment_method, step['name'], self.enrichment_prompts[i])

            # Execute with LiteLLM fallbacks (retries are handled by LiteLLM)
            response, input_tokens, output_tokens = self._enrich_with_litellm(
                conversation, system_message, litellm_config, i
            )

            # Apply speaker label replacement if this step identified speakers
            if ('agent_speaker_labels' in response) and ('customer_speaker_labels' in response):
                response = self._replace_speaker_labels(redacted_transcript, response)
                redacted_transcript = response['transcript']

            # Accumulate results
            enriched_response.update(response)

        # Generate customer ID from extracted info and remove sensitive data
        if 'customer_info' in enriched_response:
            hashed_id, first_name, last_name, birth_date = create_customer_id(
                enriched_response['customer_info']['full_name'],
                enriched_response['customer_info']['birth_date'],
                enriched_response['customer_info'].get('postcode', ''),
                enriched_response['customer_info'].get('loyalty_number', '')
            )
            enriched_response['customer_id'] = hashed_id
            enriched_response['customer_first_name'] = first_name
            enriched_response['customer_last_name'] = last_name
            enriched_response['customer_birth_date'] = birth_date
            enriched_response['customer_postcode'] = enriched_response['customer_info'].get('postcode', '')
            enriched_response['customer_loyalty_number'] = enriched_response['customer_info'].get('loyalty_number', '')
            del enriched_response['customer_info']

        return enriched_response, input_tokens, output_tokens

    @observe(as_type="generation")
    def _enrich_with_litellm(self, transcript: str, system_message: str,
                           litellm_config: dict, step: int) -> tuple[dict, int, int]:
        """
        Execute enrichment using LiteLLM with automatic fallbacks and retries.

        Args:
            transcript (str): Transcript to analyze
            system_message (str): System prompt for the AI model
            litellm_config (dict): LiteLLM configuration with fallback models
            step (int): Current enrichment step number

        Returns:
            tuple[dict, int, int]: Parsed JSON response, input tokens, output tokens
        """
        # Set metadata for Langfuse and LiteLLM
        metadata = {
            "step_name": ENRICHMENT_PIPELINE[step]['name'],
            "step_number": step,
            "langfuse_prompt": self.enrichment_prompts[step]
        }

        # Execute with LiteLLM (handles retries and fallbacks automatically)
        completion = litellm.completion(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Here is the call transcript:\n{transcript}"}
            ],
            metadata=metadata,
            **litellm_config
        )

        # Update observation with the actual model used and prompt
        model_used = completion.model  # LiteLLM provides the actual model used
        provider = model_used.split('/')[0] if '/' in model_used else 'unknown'

        langfuse_context.update_current_observation(
            name=f"enrichment_{provider}_{ENRICHMENT_PIPELINE[step]['name']}",
            prompt=self.enrichment_prompts[step],
            model=model_used
        )

        response = completion.choices[0].message
        input_tokens = completion.usage.prompt_tokens
        output_tokens = completion.usage.completion_tokens
        return json.loads(response.content), input_tokens, output_tokens


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