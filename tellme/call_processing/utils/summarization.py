"""
Summarization utilities for call processing.

This module provides functions for creating summaries of conversations,
including the logic moved from call_miner.utils.summary_mining.
"""

import time
import json
import logging
import random
from langfuse import openai, Langfuse
import tiktoken
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from tellme.call_processing.utils.summarization_prompts import SUMMARIZER_PROMPTS, PROMPT_CONFIGS
from tellme.call_miner.utils.period_utils import period_bounds
from tellme.call_miner.models import PeriodSummary


logger = logging.getLogger("django")
openai.api_key = settings.OPENAI_API_KEY

# Model-specific token limits (max context window for each model)
MODEL_TOKEN_LIMITS = {
    # GPT-4 Family
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-turbo": 128000,
    "gpt-4o": 128000,
    "gpt-4o-mini": 128000,

    # GPT-5 Family
    "gpt-5-main": 400000,        # Unified, fast model
    "gpt-5-main-mini": 400000,   # Fast, high-throughput mini version
    "gpt-5-thinking": 400000,    # Reasoning model (multi-step, in-depth)
    "gpt-5-thinking-mini": 400000, # Reasoning mini version
    "gpt-5-thinking-nano": 400000, # Reasoning nano version
}

# Conservative safety margin (use 80% of max tokens)
SAFETY_MARGIN = 0.8

PROMPT_MAPPING = {
    "<class 'tellme.call_miner.models.Topic'>": "summary_mining",
    "<class 'tellme.call_miner.models.Customer'>": "customer_summary",
    "<class 'tellme.call_miner.models.Agent'>": "agent_summary",
}


def count_tokens(text: str, model_name: str) -> int:
    """
    Counts the number of tokens in the given text using tiktoken for the specified model.

    Args:
        text (str): The input text to tokenize.
        model_name (str): The name of the model to use for tokenization.

    Returns:
        int: The number of tokens in the text.
    """
    encoding = tiktoken.encoding_for_model(model_name)
    tokens = encoding.encode(text)
    return len(tokens)


def get_token_cutoff(model_name: str) -> int:
    """
    Get the appropriate token cutoff for a given model with safety margin applied.

    Args:
        model_name (str): The model name

    Returns:
        int: Token cutoff with safety margin applied (80% of max context window)
    """
    max_tokens = MODEL_TOKEN_LIMITS.get(model_name, 128000)  # Default to gpt-4o limit
    return int(max_tokens * SAFETY_MARGIN)


def condense_summaries(summaries: list[str], trace_data: dict):
    """
    Condenses a list of conversation summaries into a meta-summary that highlights recurring issues.

    Args:
        summaries (list[str]): A list of summaries from conversations between customer care agents and customers.
        trace_data (dict): A dictionary containing data to store in the corresponding Langfuse trace

    Returns:
        tuple: A tuple containing the meta-summary response, the number of input tokens, the number of output tokens,
        and the elapsed time of the API call.
    """
    logger.info("Meta-summary Generation")
    logger.info(f"Received {len(summaries)} summaries to condense.")

    client = openai.OpenAI()

    # Retrieve object class based on trace data
    metadata = trace_data.get('metadata')
    if 'object' not in metadata:
        raise ValueError(f'Invalid trace_data. Could not extract object type from metadata field {metadata}.')
    else:
        object_type = metadata.get('object')

    # Determine prompts and configs to use based on object_type
    if object_type not in PROMPT_MAPPING:
        raise ValueError(f'Object of type {object_type} is not expected to receive summarization.')
    else:
        prompt_category = PROMPT_MAPPING[object_type]

    # Prompt with Fallback
    # Perhaps in the future it is necessary to add the organization_type as an input, to load different summarizer
    # prompts according to the company. For example, different questions might be relevant to marketing compared to
    # sales teams.
    prompt = Langfuse().get_prompt(
        prompt_category,
        label=[k for k in ['development', 'staging', 'production'] if settings.TELLME_ENV in k][0],
        fallback=SUMMARIZER_PROMPTS[prompt_category]
    )
    if prompt.is_fallback:
        config_kwargs = PROMPT_CONFIGS[prompt_category]
    else:
        config_kwargs = {'langfuse_prompt': prompt}
        config_kwargs.update(prompt.config)

    # Get model-specific token cutoff
    token_cutoff = get_token_cutoff(config_kwargs['model'])
    logger.info(f"Using token cutoff of {token_cutoff} for model {config_kwargs['model']}")

    # Randomly select summaries to the point of reaching the token cutoff
    selected_text = ''
    random.shuffle(summaries)
    for i, summ in enumerate(summaries):
        new_part = f'Conversation #{i + 1}: {summ}'
        potential_payload = f'{prompt.prompt}\n\n{selected_text}\n\n{new_part}'
        if count_tokens(potential_payload, config_kwargs['model']) >= token_cutoff and i > 0:
            logger.info(f'Generating meta-summary with only {i + 1} most recent conversations.')
            break
        else:
            if i == 0:
                selected_text = new_part
            else:
                selected_text = f'{selected_text}\n\n{new_part}'

    if len(selected_text) > 0:
        try:
            # Call the API to obtain the meta-summary
            before = time.time()
            logger.info("Making API call to OpenAI.")
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt.prompt},
                    {"role": "user", "content": selected_text}
                ],
                **config_kwargs,
                **trace_data
            )
            after = time.time()
            logger.info(f"API call duration: {after - before} seconds")

            response = completion.choices[0].message
            input_tokens = completion.usage.prompt_tokens
            output_tokens = completion.usage.completion_tokens

            if response.refusal:
                raise RuntimeError(f'Model refused to respond. Refusal: {response.refusal}')
            else:
                logger.info("API call successful.")
                logger.info(f"Input tokens used: {input_tokens}")
                logger.info(f"Output tokens generated: {output_tokens}")
                return json.loads(response.content)

        except Exception as e:
            logger.error(f"An error occurred during the API call to OpenAI. {e}", exc_info=True)
            raise
    else:
        return None


def needs_refresh(summary_obj, conversations_queryset, rolling: bool, window_start, deviation_threshold: int = 10):
    """
    Decide whether the summary should be recalculated based on conversation volume changes.

    In period based mode, if the conversation count has changed significantly, a refresh is triggered
    In rolling mode, if enough new conversations have been added or the previous summary is too old,
    a refresh is triggered.

    Parameters:
        summary_obj: PeriodSummary object, The existing summary object to compare against.
        conversations_queryset: QuerySet, All conversations within the target time window.
        rolling: bool, Whether the summary is for a rolling window (uses new conversations after last_call_at).
        window_start: datetime, Date bound of the time window used to obtain relevant conversations
        deviation_threshold: int, Percentage threshold for refresh (default 10%)

    Returns:
    (needs_refresh, current_count): tuple[bool, int]
        - True if a summary refresh is needed, False otherwise.
        - The current number of relevant conversations.
    """
    current = conversations_queryset.count()
    previous = summary_obj.call_count
    if previous == 0:
        return current > 0, current
    if not rolling:
        deviation = abs(current - previous) * 100 / previous
    else:
        old_latest_call = summary_obj.last_call_at
        if window_start > old_latest_call:
            deviation = deviation_threshold + 1
        else:
            new_call_count = conversations_queryset.filter(date__gt=old_latest_call).count()
            deviation = new_call_count * 100 / previous
    return deviation > deviation_threshold, current


def enrich_summaries(conversations_queryset):
    """
    Enriches conversation summaries with key contextual metadata for enhanced AI analysis.

    This method transforms basic conversation summaries into enriched versions that include
    critical business context such as sentiment scores, revenue implications, and resolution
    status. This enriched format provides LLM models with the necessary context to make
    informed analytical decisions about customer satisfaction, churn risk, and business impact.

    The enrichment follows the pattern:
    "({date}, Sentiment: {sentiment}/5, Revenue at Stake: {revenue}, Resolved: {resolved}) {summary}"

    Args:
        conversations_queryset: QuerySet of Conversation objects to enrich.
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
    for conv in conversations_queryset:
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

# TODO: This method will be pieced out. One part for call_miner, the rest to call processing pipeline
def create_or_update_summary(obj, period: str = 'month', rolling: bool = False, trace_data: dict | None = None):
    """
    Extract all the object's related conversations, as well as their summaries, for the specified time period.
    If enough new summaries have been produced, condense them into a new meta-summary for the object.

    Args:
        obj: The object (Topic, Customer, or Agent) to create summary for
        period (str): Period of conversations to focus on. One of 'week', 'month', or 'quarter'
        rolling (bool): Indicates whether to compute the summary on a rolling window basis or not
        trace_data (dict): A dictionary containing data to store in the corresponding Langfuse trace

    Returns:
        tuple: (summary, latest_date, call_count, label)
    """

    trace_data = trace_data or {}
    start, end, label = period_bounds(period, rolling)

    # Extract all conversations in the relevant time period
    conversations = obj.conversations.filter(date__gte=start, date__lt=end)
    if not conversations.exists():
        return None, None, 0, label

    # Check if the object has an attribute 'last_conversation_date' from ConversationStatsAbstractModel
    latest_date = getattr(obj, 'last_conversation_date', None)
    if latest_date is None:
        latest_date = obj.conversations.order_by("-date").values_list("date", flat=True).first()

    # Fetch existing PeriodSummary (if it exists)
    content_type = ContentType.objects.get_for_model(obj.__class__)
    summary_obj, created = PeriodSummary.objects.select_for_update().get_or_create(
        content_type=content_type,
        object_id=obj.pk,
        period_type=period,
        period_label=label,
        defaults=dict(
            summary={},
            last_call_at=latest_date,
            call_count=0,
        )
    )

    # Examine whether re-calculating a summary is needed
    refresh_needed, call_count = needs_refresh(summary_obj, conversations, rolling, start)

    # If no refresh is needed, return existing summary
    if not created and not refresh_needed:
        return summary_obj.summary, latest_date, call_count, label

    # Otherwise, perform the summarization anew
    enriched_summaries = enrich_summaries(conversations)

    new_summary = condense_summaries(enriched_summaries, trace_data=trace_data)

    summary_obj.summary = new_summary
    summary_obj.call_count = call_count
    summary_obj.last_call_at = latest_date
    summary_obj.save(update_fields=["summary", "call_count", "last_call_at"])

    return new_summary, latest_date, call_count, label