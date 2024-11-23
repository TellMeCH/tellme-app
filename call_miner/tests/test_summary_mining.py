import pytest
from unittest.mock import patch, MagicMock
from call_miner.utils.summary_mining import count_tokens, condense_summaries, SummarizerResponse


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
    mock_message.content = '{"summary": "Mocked meta-summary"}'

    # Set the choices to return the mock message
    mock_completion.choices = [MagicMock(message=mock_message)]

    # Mock the parse method to return the mock completion
    mock_client_instance.chat.completions.create.return_value = mock_completion

    summaries = [
        'Customer called about issue A.',
        'Customer reported problem B.',
        'Customer inquired about service C.',
    ]
    response = condense_summaries(summaries, {})

    assert response == 'Mocked meta-summary'
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
        condense_summaries(summaries, {})
    assert 'API error' in str(exc_info.value)


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
    mock_message.content = '{"summary": "Mocked meta-summary"}'

    # Set the choices to return the mock message
    mock_completion.choices = [MagicMock(message=mock_message)]

    # Mock the parse method to return the mock completion
    mock_client_instance.chat.completions.create.return_value = mock_completion

    summaries = ['a' * 100000] * 13
    response = condense_summaries(summaries,{})
    assert response == 'Mocked meta-summary'
    mock_client_instance.chat.completions.create.assert_called_once()


def test_condense_summaries_no_summaries():
    """
    Test the condense_summaries function with an empty list of summaries.

    Verifies that the function returns the appropriate message for no summaries.
    """
    summaries = []
    response = condense_summaries(summaries,{})
    assert response == "No conversations to summarize. Check back later once new calls have been recorded."
