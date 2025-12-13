import json
import litellm
import tiktoken
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context
from django.conf import settings
from tellme.call_miner.utils.period_utils import period_bounds
from tellme.call_processing.utils.llm_configs import SUMMARIZER_PROMPTS, SUMMARIZER_CONFIGS
from tellme.call_processing.utils.litellm_config import setup_litellm, get_meta_summarization_config, get_provider_from_model
from tellme.call_processing.utils.transcript_cleaner import clean_transcript


# Model-specific token limits (max context window for each model)
MODEL_TOKEN_LIMITS = {
    # --- OpenAI GPT-4 Family (Standard) ---
    "openai/gpt-4-turbo": 128000,
    "openai/gpt-4o": 128000,
    "openai/gpt-4o-mini": 128000,

    # --- OpenAI o-Series (Reasoning) ---
    "openai/o1": 128000,
    "openai/o1-mini": 128000,
    "openai/o3-mini": 200000,

    # --- OpenAI GPT-5 Family (Flagship) ---
    "openai/gpt-5": 400000,
    "openai/gpt-5-mini": 400000,
    "openai/gpt-5-nano": 400000,

    # --- Google Gemini 3 Family (Newest / Preview) ---
    # Released Nov 2025. Currently in Preview.
    # Note: Initial context is 1M, distinct from the 2M limit of 1.5 Pro.
    "vertex_ai/gemini-3-pro-preview": 1048576,

    # --- Google Gemini 2.5 Family (Current Stable) ---
    # The production standard as of late 2025.
    "vertex_ai/gemini-2.5-pro": 1048576,
    "vertex_ai/gemini-2.5-flash": 1048576,
    "vertex_ai/gemini-2.5-flash-lite": 1048576, # High throughput, lower cost

    # --- Google Gemini Previous Generations ---
    # Kept for legacy compatibility; 1.5 Pro still offers the largest context (2M).
    "vertex_ai/gemini-2.0-flash-001": 1048576,
    "vertex_ai/gemini-1.5-pro": 2097152,        # Still the context king (2M)
    "vertex_ai/gemini-1.5-flash": 1048576,
}

# Conservative safety margin (use 80% of max tokens)
SAFETY_MARGIN = 0.8

PROMPT_MAPPING = {
    "<class 'tellme.call_miner.models.Topic'>": "summary_mining",
    "<class 'tellme.call_miner.models.Customer'>": "customer_summary",
    "<class 'tellme.call_miner.models.Agent'>": "agent_summary",
}


class MetaSummarizer:
    """
    Object in charge of carrying out the meta-summarization of object call summaries
    """
    def __init__(self):
        # Setup LiteLLM with Langfuse integration and retry settings
        setup_litellm()

        # Validate required API keys
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            raise RuntimeError("OpenAI API key not found. Please set the OPENAI_API_KEY setting value.")

        self.allowed_objects = PROMPT_MAPPING.keys()

        # Load prompts from Langfuse with fallback and generate LiteLLM configs
        # Perhaps in the future it is necessary to add the organization_type as an input, to load different summarizer
        # prompts according to the company. For example, different questions might be relevant to marketing compared to
        # sales teams.
        self.prompts, self.configs = {}, {}
        for object_type, prompt_category in PROMPT_MAPPING.items():
            prompt = Langfuse().get_prompt(
                prompt_category,
                label=[k for k in ['development', 'staging', 'production'] if settings.TELLME_ENV in k][0],
                fallback=SUMMARIZER_PROMPTS[prompt_category]
            )
            self.prompts[prompt_category] = prompt

            # Generate LiteLLM config for this category
            self.configs[prompt_category] = get_meta_summarization_config(prompt, prompt_category)

    @staticmethod
    def _count_tokens(text: str, model_name: str) -> int:
        """
        Counts the number of tokens in the given text using tiktoken for the specified model.

        Args:
            text (str): The input text to tokenize.
            model_name (str): The model name (with or without provider prefix like "openai/").

        Returns:
            int: The number of tokens in the text.
        """
        # Strip provider prefix for tiktoken (it only understands base model names)
        base_model_name = model_name.split('/')[-1] if '/' in model_name else model_name
        encoding = tiktoken.encoding_for_model(base_model_name)
        tokens = encoding.encode(text)
        return len(tokens)

    @staticmethod
    def _get_token_cutoff(model_name: str) -> int:
        """
        Get the appropriate token cutoff for a given model with safety margin applied.

        Args:
            model_name (str): The model name

        Returns:
            int: Token cutoff with safety margin applied (80% of max context window)
        """
        max_tokens = MODEL_TOKEN_LIMITS.get(model_name, 128000)  # Default to gpt-4o limit
        return int(max_tokens * SAFETY_MARGIN)

    @staticmethod
    def _retrieve_object_conversations(obj, period: str = 'month', rolling: bool = False):
        """
        Extract all the object's related conversations, as well as their summaries, for the specified time period.
        Args:
            obj: The object (Topic, Customer, or Agent) to create summary for
            period (str): Period of conversations to focus on. One of 'week', 'month', 'quarter', or 'eternity'
            rolling (bool): Indicates whether to compute the summary on a rolling window basis or not

        Returns:
            tuple: (conversations, latest_date, call_count, label)
        """
        start, end, label = period_bounds(period, rolling)

        # Extract all conversations in the relevant time period
        conversations = obj.conversations.filter(date__gte=start, date__lt=end).order_by("-date")

        latest_date = getattr(obj, 'last_conversation_date', None)
        if latest_date is None:
            latest_date = conversations.values_list("date", flat=True).first()

        return conversations, latest_date, conversations.count(), label

    @staticmethod
    def _enrich_items(conversations):
        """
        Enriches conversation summaries and transcripts with key contextual metadata for enhanced AI analysis.

        This method transforms both summaries and transcripts into enriched versions that include
        critical business context such as sentiment scores, revenue implications, and resolution
        status. This enriched format provides LLM models with the necessary context to make
        informed analytical decisions about customer satisfaction, churn risk, and business impact.

        The enrichment follows the pattern:
        "({date}, Sentiment: {sentiment}/5, Revenue at Stake: {revenue}, Resolved: {resolved}) {content}"

        Args:
            conversations: QuerySet of Conversation objects to enrich.
                Each conversation should have date, sentiment, revenue_at_stake, resolved,
                summary, and transcript attributes.

        Returns:
            tuple: (enriched_summaries, enriched_transcripts)
                - enriched_summaries: List of enriched summary strings
                - enriched_transcripts: List of enriched transcript strings
                Each string contains the original content prefixed with contextual metadata.

        Example:
            Input conversations with summaries like "Customer complained about billing error"
            Output summary: "(2025-01-12, Sentiment: 2/5, Revenue at Stake: 1500.00, Resolved: False)
                    Customer complained about billing error"
            Output transcript: "(2025-01-12, Sentiment: 2/5, Revenue at Stake: 1500.00, Resolved: False)
                    <agent>: How can I help you today? <customer>: I have a billing error..."
        """
        enriched_template = "({date}, Sentiment: {sentiment}/5, Revenue at Stake: {revenue}, Resolved: {resolved}) {content}"

        enriched_summaries = []
        enriched_transcripts = []
        for conv in conversations:
            # Enrich summary
            enriched_summaries.append(
                enriched_template.format(
                    date=conv.date,
                    sentiment=conv.sentiment,
                    revenue=conv.revenue_at_stake,
                    resolved=conv.resolved,
                    content=conv.summary
                )
            )
            # Enrich transcript (apply cleaning before enrichment)
            cleaned_transcript = clean_transcript(conv.transcript)
            enriched_transcripts.append(
                enriched_template.format(
                    date=conv.date,
                    sentiment=conv.sentiment,
                    revenue=conv.revenue_at_stake,
                    resolved=conv.resolved,
                    content=cleaned_transcript
                )
            )
        return enriched_summaries, enriched_transcripts

    def _count_items_within_limit(self, items: list[str], prompt: str, model_name: str, token_cutoff: int) -> tuple[int, str]:
        """
        Count how many items fit within the token limit and build the selected text.

        This method iterates through items once, building the selected text while counting
        how many items can be included before hitting the token limit.

        Args:
            items (list[str]): List of enriched items (summaries or transcripts)
            prompt (str): The system prompt to be included in token counting
            model_name (str): The model name for token counting
            token_cutoff (int): Maximum number of tokens allowed

        Returns:
            tuple[int, str]: (count of items that fit, selected text ready for LLM)
        """
        selected_text = ''
        count = 0
        for i, item in enumerate(items):
            new_part = f'Conversation #{i + 1}: {item}'
            potential_payload = f'{prompt}\n\n{selected_text}\n\n{new_part}'
            counted_tokens = self._count_tokens(potential_payload, model_name)
            if counted_tokens >= token_cutoff and i > 0:
                break
            else:
                if i == 0:
                    selected_text = new_part
                else:
                    selected_text = f'{selected_text}\n\n{new_part}'
                count += 1
        return count, selected_text

    @staticmethod
    def _clean_escaped_newlines(data):
        """
        Recursively replace escaped newlines (\\n) with actual newlines (\n) in the response.

        LLMs sometimes return escaped newlines in their JSON responses when they should be
        actual newlines. This method cleans up the response by recursively processing
        dictionaries, lists, and strings.

        Args:
            data: The data to clean (dict, list, str, or other)

        Returns:
            Cleaned data with escaped newlines replaced
        """
        if isinstance(data, dict):
            return {key: MetaSummarizer._clean_escaped_newlines(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [MetaSummarizer._clean_escaped_newlines(item) for item in data]
        elif isinstance(data, str):
            return data.replace('\\n', '\n')
        else:
            return data

    @staticmethod
    def _unwrap_schema_response(data):
        """
        Unwrap JSON Schema metadata from LLM responses if present.

        Some LLM responses incorrectly include JSON Schema structure with
        "type": "object" and "properties" wrappers. This method detects and
        unwraps such responses to return only the actual data.

        Args:
            data: The response data (dict)

        Returns:
            Unwrapped data with schema metadata removed if present

        Example:
            Input:  {"type": "object", "properties": {"Churn Potential": "...", ...}}
            Output: {"Churn Potential": "...", ...}
        """
        if not isinstance(data, dict):
            return data

        # Check if this is a schema-wrapped response
        if "type" in data and data["type"] == "object" and "properties" in data:
            # Return the properties directly
            return data["properties"]

        return data

    @observe(as_type="generation")
    def _condense_items(self, enriched_summaries: list[str], enriched_transcripts: list[str], trace_data: dict):
        """
        Condenses a list of conversation summaries or transcripts into a meta-summary.

        This method intelligently chooses between using summaries or transcripts based on which
        allows more conversations to be included within the token limit. Transcripts are preferred
        when they enable including the same or more conversations than summaries.

        Uses LiteLLM with OpenAI as primary and Gemini as fallback.
        trace_data is passed to Langfuse for observability.

        Args:
            enriched_summaries (list[str]): Enriched summaries from conversations
            enriched_transcripts (list[str]): Enriched transcripts from conversations
            trace_data (dict): A dictionary containing data to store in the corresponding Langfuse trace

        Returns:
            dict: Meta-summary response (JSON object)
        """
        # Extract object type from trace_data
        metadata = trace_data.get('metadata', {})
        if 'object' not in metadata:
            raise ValueError(f'Invalid trace_data. Could not extract object type from metadata field {metadata}.')

        object_type = metadata.get('object')
        if object_type not in PROMPT_MAPPING:
            raise ValueError(f'Object of type {object_type} is not expected to receive summarization.')

        prompt_category = PROMPT_MAPPING[object_type]
        prompt = self.prompts[prompt_category]
        config_kwargs = self.configs[prompt_category]

        # Extract model name with provider prefix (e.g., "openai/gpt-4o-mini")
        model_name = config_kwargs["model"]
        token_cutoff = self._get_token_cutoff(model_name)

        # Count how many items of each type fit within the token limit and build selected text
        transcript_count, transcript_text = self._count_items_within_limit(
            enriched_transcripts, prompt.prompt, model_name, token_cutoff
        )
        summary_count, summary_text = self._count_items_within_limit(
            enriched_summaries, prompt.prompt, model_name, token_cutoff
        )

        # Choose transcripts if they include same or more conversations
        # Otherwise use summaries (more concise, includes more conversations)
        if transcript_count >= summary_count:
            selected_text = transcript_text
            item_type = "transcripts"
        else:
            selected_text = summary_text
            item_type = "summaries"

        # Add metadata about selection
        metadata['item_type_used'] = item_type
        metadata['transcript_count_possible'] = transcript_count
        metadata['summary_count_possible'] = summary_count

        if len(selected_text) > 0:
            # Update trace with metadata from views.py
            langfuse_context.update_current_trace(
                name=trace_data.get('name', 'get_summary_data'),
                tags=trace_data.get('tags', []),
                metadata=metadata
            )

            # Call LiteLLM with automatic fallbacks and retries
            completion = litellm.completion(
                messages=[
                    {"role": "system", "content": prompt.prompt},
                    {"role": "user", "content": selected_text}
                ],
                **config_kwargs
            )

            # Update Langfuse observation with completion details
            model_used = completion.model

            langfuse_context.update_current_observation(
                model=model_used,
                prompt=prompt,
                usage={
                    "promptTokens": completion.usage.prompt_tokens,
                    "completionTokens": completion.usage.completion_tokens,
                    "totalTokens": completion.usage.total_tokens
                },
                **trace_data
            )

            response = completion.choices[0].message

            # Check for refusal (OpenAI-specific attribute)
            refusal = getattr(response, 'refusal', None)
            if refusal:
                raise RuntimeError(f'Model refused to respond. Refusal: {refusal}')

            # Parse JSON response, unwrap schema if present, and clean up escaped newlines
            result = json.loads(response.content)
            result = self._unwrap_schema_response(result)
            return self._clean_escaped_newlines(result)
        else:
            return None

    def __call__(self, obj, period: str = 'month', rolling: bool = False, trace_data: dict = None):
        """
        Extract all the object's related conversations, as well as their summaries and transcripts,
        for the specified time period. Intelligently choose between summaries and transcripts based on
        which allows more conversations to be included, then condense into a new meta-summary.

        Args:
            obj: The object (Topic, Customer, or Agent) to create summary for
            period (str): Period of conversations to focus on. One of 'week', 'month', 'quarter', or 'eternity'
            rolling (bool): Indicates whether to compute the summary on a rolling window basis or not
            trace_data (dict): A dictionary containing data to store in the corresponding Langfuse trace

        Returns:
            tuple: (summary, latest_date, call_count, label)
        """
        trace_data = trace_data or {}

        conversations, latest_date, call_count, label = self._retrieve_object_conversations(obj, period, rolling)

        enriched_summaries, enriched_transcripts = self._enrich_items(conversations)

        new_summary = self._condense_items(enriched_summaries, enriched_transcripts, trace_data)

        return new_summary, latest_date, call_count, label