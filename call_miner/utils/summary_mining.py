import time
import logging
import openai
import tiktoken
from django.conf import settings
from pydantic import BaseModel


logger = logging.getLogger(__name__)

SUMMARIZER_PROMPT = """
You are an assistant for the customer care center of a company.
Below are summaries of conversations between customer care agents and customers.
In two or three sentences, summarize what the recurring issues appearing in these calls are.
These recurring issues should help the company identify ways to improve its customer experience.
"""
MODEL_NAME = 'gpt-4o-mini'
TOKEN_CUTOFF = 120000

openai.api_key = settings.OPENAI_API_KEY


class SummarizerResponse(BaseModel):
    """
    A Pydantic model that represents the response structure from the OpenAI API.
    Contains:
        - summary: A string summarizing the provided conversation summaries.
    """
    summary: str


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


def condense_summaries(summaries: list[str]):
    """
    Condenses a list of conversation summaries into a meta-summary that highlights recurring issues.

    Args:
        summaries (list[str]): A list of summaries from conversations between customer care agents and customers.

    Returns:
        tuple: A tuple containing the meta-summary response, the number of input tokens, the number of output tokens,
        and the elapsed time of the API call.
    """
    logger.info("Meta-summary Generation")
    logger.info(f"Received {len(summaries)} summaries to condense.")

    client = openai.OpenAI()

    # Select all summaries to the point of reaching the token cutoff
    selected_text = ''
    for i, summ in enumerate(summaries):
        new_part = f'Conversation #{i + 1}: {summ}'
        potential_payload = f'{SUMMARIZER_PROMPT}\n\n{selected_text}\n\n{new_part}'
        if count_tokens(potential_payload, MODEL_NAME) >= TOKEN_CUTOFF and i > 0:
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
            completion = client.beta.chat.completions.parse(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SUMMARIZER_PROMPT},
                    {"role": "user", "content": selected_text}
                ],
                response_format=SummarizerResponse
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
                result = response.parsed
                return result.summary

        except Exception as e:
            logger.error(f"An error occurred during the API call to OpenAI. {e}", exc_info=True)
            raise
    else:
        return "No conversations to summarize. Check back later once new calls have been recorded."
