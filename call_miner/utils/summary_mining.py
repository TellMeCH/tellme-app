import time
import json
import logging
import random
from langfuse import openai, Langfuse
import tiktoken
from django.conf import settings
from call_miner.utils.fallback_prompt import SUMMARIZER_PROMPT, PROMPT_CONFIG


logger = logging.getLogger("django")
TOKEN_CUTOFF = 120000
openai.api_key = settings.OPENAI_API_KEY


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

    # Prompt with Fallback
    # Perhaps in the future it is necessary to add the organization_type as an input, to load different summarizer
    # prompts according to the company. For example, different questions might be relevant to marketing compared to
    # sales teams.
    prompt = Langfuse().get_prompt(
        'summary_mining',
        label=[k for k in ['development', 'staging', 'production'] if settings.TELLME_ENV in k][0],
        fallback=SUMMARIZER_PROMPT
    )
    if prompt.is_fallback:
        config_kwargs = PROMPT_CONFIG
    else:
        config_kwargs = {'langfuse_prompt': prompt}
        config_kwargs.update(prompt.config)

    # Randomly select summaries to the point of reaching the token cutoff
    selected_text = ''
    random.shuffle(summaries)
    for i, summ in enumerate(summaries):
        new_part = f'Conversation #{i + 1}: {summ}'
        potential_payload = f'{prompt.prompt}\n\n{selected_text}\n\n{new_part}'
        if count_tokens(potential_payload, config_kwargs['model']) >= TOKEN_CUTOFF and i > 0:
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
