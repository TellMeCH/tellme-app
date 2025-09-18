import json
import pytest
from unittest.mock import patch, MagicMock
from apps.call_miner.utils.summary_mining import count_tokens, condense_summaries
from apps.call_miner.utils.fallback_prompt import PROMPT_CONFIGS


def _build_openai_stub():
    """
    Returns an OpenAI() stub whose chat.completions.create() gives a minimal,
    well-formed response object (with usage + choices) so that condense_summaries
    can run end-to-end without talking to the real API.
    """
    mock_client = MagicMock()

    mock_completion = MagicMock()
    mock_completion.usage.prompt_tokens = 10
    mock_completion.usage.completion_tokens = 5

    mock_msg = MagicMock()
    mock_msg.refusal = False
    mock_msg.content = json.dumps({"dummy": "ok"})

    mock_completion.choices = [MagicMock(message=mock_msg)]
    mock_client.chat.completions.create.return_value = mock_completion
    return mock_client


def test_count_tokens_empty_string():
    """
    Test the count_tokens function with an empty string.

    Ensures that counting tokens in an empty string returns zero.
    """
    text = ''
    model_name = 'gpt-3.5-turbo'
    token_count = count_tokens(text, model_name)
    assert token_count == 0


def test_count_tokens_simple_text():
    """
    Test the count_tokens function with a simple text input.

    Verifies that the token count matches the expected number of tokens
    for a basic sentence.
    """
    text = 'Hello, world!'
    model_name = 'gpt-3.5-turbo'
    token_count = count_tokens(text, model_name)
    expected_token_count = 4
    assert token_count == expected_token_count


def test_count_tokens_invalid_model():
    """
    Test the count_tokens function with an invalid model name.

    Expects the function to raise an exception due to the invalid model.
    """
    text = 'Test text'
    model_name = 'invalid-model'
    with pytest.raises(Exception):
        count_tokens(text, model_name)


@patch('call_miner.utils.summary_mining.openai.OpenAI')
def test_condense_summaries_success(mock_openai):
    """
    Test the condense_summaries function for successful execution.

    Mocks the OpenAI API to return a predefined meta-summary.
    Verifies that the function returns the expected meta-summary
    and that the API is called exactly once.
    """

    mock_client_instance = mock_openai.return_value

    # Create a mock for the completion object
    mock_completion = MagicMock()
    # Mock the usage attributes
    mock_completion.usage.prompt_tokens = 150
    mock_completion.usage.completion_tokens = 50

    # Create a mock message object
    mock_message = MagicMock()
    mock_message.refusal = False  # Simulate that the model did not refuse
    mock_message.content = '{"Reasons for Calling": "Billing issues and account setup inquiries are common."}'

    # Set the choices to return the mock message
    mock_completion.choices = [MagicMock(message=mock_message)]

    # Mock the parse method to return the mock completion
    mock_client_instance.chat.completions.create.return_value = mock_completion

    summaries = [
        'Customer called about issue A.',
        'Customer reported problem B.',
        'Customer inquired about service C.',
    ]
    response = condense_summaries(summaries, {'metadata': {'object': "<class 'call_miner.models.Topic'>"}})

    assert response == {'Reasons for Calling': 'Billing issues and account setup inquiries are common.'}
    mock_client_instance.chat.completions.create.assert_called_once()


@patch('call_miner.utils.summary_mining.openai.OpenAI')
def test_condense_summaries_api_exception(mock_openai):
    """
    Test the condense_summaries function's handling of API exceptions.

    Simulates an API error and verifies that the function raises an exception
    with the appropriate error message.
    """
    mock_client_instance = mock_openai.return_value
    mock_client_instance.chat.completions.create.side_effect = Exception('API error')

    summaries = ['Customer called about issue A.']
    with pytest.raises(Exception) as exc_info:
        condense_summaries(summaries, {'metadata': {'object': "<class 'call_miner.models.Topic'>"}})
    assert 'API error' in str(exc_info.value)


def test_condense_summaries_no_summaries():
    """
    Test the condense_summaries function with an empty list of summaries.

    Verifies that the function returns the appropriate message for no summaries.
    """
    summaries = []
    response = condense_summaries(summaries, {'metadata': {'object': "<class 'call_miner.models.Topic'>"}})
    assert response is None


@patch('call_miner.utils.summary_mining.count_tokens', return_value=1)
@patch('call_miner.utils.summary_mining.openai.OpenAI')
@patch('call_miner.utils.summary_mining.Langfuse')
def test_prompt_category_for_customer(mock_langfuse, mock_openai, _mock_count_tokens):
    """
    Verifies that a Customer object triggers the **customer_summary** prompt (and nothing else).
    """
    lf_inst = mock_langfuse.return_value
    prompt_obj = MagicMock(
        prompt="<<customer prompt>>",
        is_fallback=False,
        config={"model": "gpt-4o-mini"}
    )
    lf_inst.get_prompt.return_value = prompt_obj

    mock_openai.return_value = _build_openai_stub()

    condense_summaries(
        ["dummy summary"],
        {"metadata": {"object": "<class 'call_miner.models.Customer'>"}}
    )
    lf_inst.get_prompt.assert_called_once()
    assert lf_inst.get_prompt.call_args[0][0] == "customer_summary"


@patch('call_miner.utils.summary_mining.count_tokens', return_value=1)
@patch('call_miner.utils.summary_mining.openai.OpenAI')
@patch('call_miner.utils.summary_mining.Langfuse')
def test_prompt_category_for_agent(mock_langfuse, mock_openai, _mock_count_tokens):
    """
    Verifies that an Agent object triggers the **agent_summary** prompt.
    """
    lf_inst = mock_langfuse.return_value
    prompt_obj = MagicMock(
        prompt="<<agent prompt>>",
        is_fallback=False,
        config={"model": "gpt-4o-mini"}
    )
    lf_inst.get_prompt.return_value = prompt_obj
    mock_openai.return_value = _build_openai_stub()

    condense_summaries(
        ["dummy"],
        {"metadata": {"object": "<class 'call_miner.models.Agent'>"}}
    )

    lf_inst.get_prompt.assert_called_once()
    assert lf_inst.get_prompt.call_args[0][0] == "agent_summary"


@patch('call_miner.utils.summary_mining.count_tokens', return_value=1)
@patch('call_miner.utils.summary_mining.openai.OpenAI')
@patch('call_miner.utils.summary_mining.Langfuse')
def test_fallback_config_is_used(mock_langfuse, mock_openai, _mock_count_tokens):
    """
    When Langfuse returns a *fallback* prompt, condense_summaries must fall back
    to PROMPT_CONFIGS for model / temperature / response_format.
    """
    lf_inst = mock_langfuse.return_value
    prompt_obj = MagicMock(
        prompt="<<fallback customer prompt>>",
        is_fallback=True,
    )
    lf_inst.get_prompt.return_value = prompt_obj

    mock_openai.return_value = _build_openai_stub()

    condense_summaries(
        ["dummy"],
        {"metadata": {"object": "<class 'call_miner.models.Customer'>"}}
    )

    # Inspect what went to the OpenAI stub
    _, kwargs = mock_openai.return_value.chat.completions.create.call_args
    assert kwargs["model"] == PROMPT_CONFIGS["customer_summary"]["model"]
    assert "langfuse_prompt" not in kwargs  # only used in NON-fallback paths


@patch('call_miner.utils.summary_mining.count_tokens', return_value=1)
def test_invalid_object_type_raises(_mock_count_tokens):
    """
    An unknown object type in trace_data should raise a ValueError.
    """
    with pytest.raises(ValueError):
        condense_summaries(
            ["whatever"],
            {"metadata": {"object": "<class 'call_miner.models.Unknown'>"}}
        )


@patch('call_miner.utils.summary_mining.openai.OpenAI')
def test_condense_summaries_token_cutoff(mock_openai):
    """
    Test the condense_summaries function when the token cutoff is reached.

    Provides enough summaries to exceed the TOKEN_CUTOFF limit and verifies
    that the function processes summaries up to the cutoff without errors.
    """
    mock_client_instance = mock_openai.return_value

    # Create a mock for the completion object
    mock_completion = MagicMock()
    # Mock the usage attributes
    mock_completion.usage.prompt_tokens = 120000
    mock_completion.usage.completion_tokens = 1000

    # Create a mock message object
    mock_message = MagicMock()
    mock_message.refusal = False
    mock_message.content = '{"Reasons for Calling": "Billing issues and account setup inquiries are common."}'

    # Set the choices to return the mock message
    mock_completion.choices = [MagicMock(message=mock_message)]

    # Mock the parse method to return the mock completion
    mock_client_instance.chat.completions.create.return_value = mock_completion

    summaries = ['a' * 100000] * 13
    response = condense_summaries(summaries, {'metadata': {'object': "<class 'call_miner.models.Topic'>"}})
    assert response == {'Reasons for Calling': 'Billing issues and account setup inquiries are common.'}
    mock_client_instance.chat.completions.create.assert_called_once()