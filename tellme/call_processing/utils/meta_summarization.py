import json
import random
import litellm
import tiktoken
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context
from django.conf import settings
from tellme.call_miner.utils.period_utils import period_bounds
from tellme.call_processing.utils.llm_configs import SUMMARIZER_PROMPTS, SUMMARIZER_CONFIGS
from tellme.call_processing.utils.litellm_config import setup_litellm, get_meta_summarization_config, get_provider_from_model


# Model-specific token limits (max context window for each model)
MODEL_TOKEN_LIMITS = {
    # OpenAI GPT-4 Family
    "openai/gpt-4": 8192,
    "openai/gpt-4-32k": 32768,
    "openai/gpt-4-turbo": 128000,
    "openai/gpt-4o": 128000,
    "openai/gpt-4o-mini": 128000,

    # OpenAI GPT-5 Family
    "openai/gpt-5-main": 400000,        # Unified, fast model
    "openai/gpt-5-main-mini": 400000,   # Fast, high-throughput mini version
    "openai/gpt-5-thinking": 400000,    # Reasoning model (multi-step, in-depth)
    "openai/gpt-5-thinking-mini": 400000, # Reasoning mini version
    "openai/gpt-5-thinking-nano": 400000, # Reasoning nano version

    # Google Gemini Family (Vertex AI)
    "vertex_ai/gemini-1.0-pro": 30720,
    "vertex_ai/gemini-1.5-pro": 1000000,
    "vertex_ai/gemini-1.5-flash": 1000000,
    "vertex_ai/gemini-2.0-flash-001": 1000000,
    "vertex_ai/gemini-2.0-flash-exp": 1000000,
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
            period (str): Period of conversations to focus on. One of 'week', 'month', or 'quarter'
            rolling (bool): Indicates whether to compute the summary on a rolling window basis or not

        Returns:
            tuple: (conversations, latest_date, call_count, label)
        """
        start, end, label = period_bounds(period, rolling)

        # Extract all conversations in the relevant time period
        conversations = obj.conversations.filter(date__gte=start, date__lt=end)

        latest_date = getattr(obj, 'last_conversation_date', None)
        if latest_date is None:
            latest_date = conversations.order_by("-date").values_list("date", flat=True).first()

        return conversations, latest_date, conversations.count(), label

    @staticmethod
    def _enrich_summaries(conversations):
        """
        Enriches conversation summaries with key contextual metadata for enhanced AI analysis.

        This method transforms basic conversation summaries into enriched versions that include
        critical business context such as sentiment scores, revenue implications, and resolution
        status. This enriched format provides LLM models with the necessary context to make
        informed analytical decisions about customer satisfaction, churn risk, and business impact.

        The enrichment follows the pattern:
        "({date}, Sentiment: {sentiment}/5, Revenue at Stake: {revenue}, Resolved: {resolved}) {summary}"

        Args:
            conversations: QuerySet of Conversation objects to enrich.
                Each conversation should have date, sentiment, revenue_at_stake, resolved, and
                summary attributes.

        Returns:
            list: List of enriched summary strings. Each string contains the original summary
                prefixed with contextual metadata in a structured format that helps AI models
                understand the business context and customer impact of each conversation.

        Example:
            Input conversations with summaries like "Customer complained about billing error"
            Output: "(2025-01-12, Sentiment: 2/5, Revenue at Stake: 1500.00, Resolved: False)
                    Customer complained about billing error"
        """
        enriched_template = "({date}, Sentiment: {sentiment}/5, Revenue at Stake: {revenue}, Resolved: {resolved}) {summary}"

        enriched_summaries = []
        for conv in conversations:
            enriched_summaries.append(
                enriched_template.format(
                    date=conv.date,
                    sentiment=conv.sentiment,
                    revenue=conv.revenue_at_stake,
                    resolved=conv.resolved,
                    summary=conv.summary
                )
            )
        return enriched_summaries

    @observe(as_type="generation")
    def _condense_summaries(self, summaries: list[str], trace_data: dict):
        """
        Condenses a list of conversation summaries into a meta-summary.

        Uses LiteLLM with OpenAI as primary and Gemini as fallback.
        trace_data is passed to Langfuse for observability.

        Args:
            summaries (list[str]): A list of summaries from conversations between customer care agents and customers.
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

        # Token-aware random selection
        selected_text = ''
        random.shuffle(summaries)
        for i, summ in enumerate(summaries):
            new_part = f'Conversation #{i + 1}: {summ}'
            potential_payload = f'{prompt.prompt}\n\n{selected_text}\n\n{new_part}'
            counted_tokens = self._count_tokens(potential_payload, model_name)
            if counted_tokens >= token_cutoff and i > 0:
                break
            else:
                if i == 0:
                    selected_text = new_part
                else:
                    selected_text = f'{selected_text}\n\n{new_part}'

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

            return json.loads(response.content)
        else:
            return None

    def __call__(self, obj, period: str = 'month', rolling: bool = False, trace_data: dict = None):
        """
        Extract all the object's related conversations, as well as their summaries, for the specified time period.
        Condense the conversation summaries into a new meta-summary for the object.

        Args:
            obj: The object (Topic, Customer, or Agent) to create summary for
            period (str): Period of conversations to focus on. One of 'week', 'month', or 'quarter'
            rolling (bool): Indicates whether to compute the summary on a rolling window basis or not
            trace_data (dict): A dictionary containing data to store in the corresponding Langfuse trace

        Returns:
            tuple: (summary, latest_date, call_count, label)
        """
        trace_data = trace_data or {}

        conversations, latest_date, call_count, label = self._retrieve_object_conversations(obj, period, rolling)

        enriched_summaries = self._enrich_summaries(conversations)

        new_summary = self._condense_summaries(enriched_summaries, trace_data)

        return new_summary, latest_date, call_count, label