import time
import json
import logging
import random
from langfuse import openai, Langfuse
import tiktoken
from django.conf import settings
from tellme.call_miner.utils.fallback_prompt import SUMMARIZER_PROMPTS, PROMPT_CONFIGS


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
