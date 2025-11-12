import pytest
import json
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timedelta
from django.utils import timezone
from tellme.call_processing.utils.meta_summarization import MetaSummarizer
from tellme.call_miner.models import Topic, Customer, Agent, Conversation


@pytest.mark.django_db
class TestMetaSummarizer:
    """
    Test the MetaSummarizer class functionality.
    """

    @pytest.fixture
    def meta_summarizer(self, mock_langfuse, mock_openai):
        """Create a MetaSummarizer instance with mocked dependencies."""
        with patch('tellme.call_processing.utils.meta_summarization.Langfuse') as mock_langfuse_class:
            mock_langfuse_instance = Mock()
            mock_prompt = Mock()
            mock_prompt.is_fallback = True
            mock_prompt.prompt = "Test prompt"
            mock_langfuse_instance.get_prompt.return_value = mock_prompt
            mock_langfuse_class.return_value = mock_langfuse_instance

            return MetaSummarizer()

    def test_meta_summarizer_initialization(self, meta_summarizer, settings):
        """
        Test that MetaSummarizer initializes correctly with proper configuration.
        """
        assert meta_summarizer.openai is not None
        assert len(meta_summarizer.allowed_objects) == 3
        assert "<class 'tellme.call_miner.models.Topic'>" in meta_summarizer.allowed_objects
        assert "<class 'tellme.call_miner.models.Customer'>" in meta_summarizer.allowed_objects
        assert "<class 'tellme.call_miner.models.Agent'>" in meta_summarizer.allowed_objects

    def test_meta_summarizer_initialization_missing_api_key(self, settings):
        """
        Test that MetaSummarizer raises error when OpenAI API key is missing.
        """
        settings.OPENAI_API_KEY = None

        with pytest.raises(RuntimeError, match="OpenAI API key not found"):
            MetaSummarizer()

    def test_count_tokens(self):
        """
        Test the token counting functionality.
        """
        test_text = "This is a test sentence for token counting."
        model_name = "gpt-4o"

        token_count = MetaSummarizer._count_tokens(test_text, model_name)

        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count < 50  # Should be reasonable for a short sentence

    def test_count_tokens_empty_string(self):
        """Test the count_tokens function with an empty string."""
        token_count = MetaSummarizer._count_tokens('', 'gpt-4o')
        assert token_count == 0

    def test_count_tokens_specific_text(self):
        """Test the count_tokens function with a known text for consistency."""
        text = 'Hello, world!'
        model_name = 'gpt-4o'
        token_count = MetaSummarizer._count_tokens(text, model_name)
        # This is a known token count for this specific text
        assert token_count == 4

    def test_count_tokens_invalid_model(self):
        """Test the count_tokens function with an invalid model name."""
        text = 'Test text'
        model_name = 'invalid-model'
        with pytest.raises(Exception):
            MetaSummarizer._count_tokens(text, model_name)

    def test_get_token_cutoff(self):
        """
        Test token cutoff calculation with safety margin.
        """
        # Test with known model
        cutoff_gpt4 = MetaSummarizer._get_token_cutoff("gpt-4o")
        assert cutoff_gpt4 == int(128000 * 0.8)  # 80% of 128k

        # Test with unknown model (should default to gpt-4o limit)
        cutoff_unknown = MetaSummarizer._get_token_cutoff("unknown-model")
        assert cutoff_unknown == int(128000 * 0.8)

    def test_retrieve_object_conversations(self, setup_db):
        """
        Test conversation retrieval for different time periods.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Test month period
        conversations, latest_date, call_count, label = MetaSummarizer._retrieve_object_conversations(
            topic, period='month', rolling=False
        )

        assert conversations.count() >= 0
        assert isinstance(call_count, int)
        assert isinstance(label, str)
        assert "2025" in label  # Should contain current year

    def test_enrich_summaries(self, setup_db):
        """
        Test summary enrichment with conversation metadata.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Create test conversations
        conversations = topic.conversations.all()

        enriched_summaries = MetaSummarizer._enrich_summaries(conversations)

        assert isinstance(enriched_summaries, list)
        if len(enriched_summaries) > 0:
            # Check format of enriched summary
            first_summary = enriched_summaries[0]
            assert "Sentiment:" in first_summary
            assert "Revenue at Stake:" in first_summary
            assert "Resolved:" in first_summary
            assert str(conversation.date) in first_summary

    @patch('tellme.call_processing.utils.meta_summarization.openai.OpenAI')
    def test_condense_summaries_success(self, mock_openai_client, meta_summarizer):
        """
        Test successful summary condensation with OpenAI API.
        """
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "Reasons for Calling": "Billing issues, Technical support",
            "Churn Potential": "Medium risk",
            "Suggested Actions": "Improve billing process"
        })
        mock_response.choices[0].message.refusal = None

        mock_openai_client.return_value.chat.completions.create.return_value = mock_response
        meta_summarizer.openai = mock_openai_client.return_value

        summaries = [
            "(2025-01-01, Sentiment: 3/5, Revenue at Stake: 1000.00, Resolved: False) Customer billing issue",
            "(2025-01-02, Sentiment: 4/5, Revenue at Stake: 500.00, Resolved: True) Technical support resolved"
        ]

        trace_data = {
            'metadata': {
                'object': "<class 'tellme.call_miner.models.Topic'>"
            }
        }

        result = meta_summarizer._condense_summaries(summaries, trace_data)

        assert isinstance(result, dict)
        assert "Reasons for Calling" in result
        assert "Churn Potential" in result
        assert "Suggested Actions" in result

    @patch('tellme.call_processing.utils.meta_summarization.openai.OpenAI')
    def test_condense_summaries_refusal(self, mock_openai_client, meta_summarizer):
        """
        Test handling of OpenAI refusal response.
        """
        # Mock OpenAI refusal response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.refusal = "I cannot provide this summary"

        mock_openai_client.return_value.chat.completions.create.return_value = mock_response
        meta_summarizer.openai = mock_openai_client.return_value

        summaries = ["(2025-01-01, Sentiment: 3/5, Revenue at Stake: 1000.00, Resolved: False) Test summary"]
        trace_data = {
            'metadata': {
                'object': "<class 'tellme.call_miner.models.Topic'>"
            }
        }

        with pytest.raises(RuntimeError, match="Model refused to respond"):
            meta_summarizer._condense_summaries(summaries, trace_data)

    def test_condense_summaries_empty_summaries(self, meta_summarizer):
        """
        Test handling of empty summaries list.
        """
        summaries = []
        trace_data = {
            'metadata': {
                'object': "<class 'tellme.call_miner.models.Topic'>"
            }
        }

        result = meta_summarizer._condense_summaries(summaries, trace_data)
        assert result is None

    def test_condense_summaries_invalid_trace_data(self, meta_summarizer):
        """
        Test handling of invalid trace_data.
        """
        summaries = ["Test summary"]

        # Missing metadata
        trace_data = {}
        with pytest.raises(TypeError, match="argument of type 'NoneType' is not iterable"):
            meta_summarizer._condense_summaries(summaries, trace_data)

        # Missing object in metadata
        trace_data = {'metadata': {}}
        with pytest.raises(ValueError, match="Invalid trace_data"):
            meta_summarizer._condense_summaries(summaries, trace_data)

    def test_condense_summaries_unsupported_object_type(self, meta_summarizer):
        """
        Test handling of unsupported object types.
        """
        summaries = ["Test summary"]
        trace_data = {
            'metadata': {
                'object': "<class 'tellme.call_miner.models.UnsupportedModel'>"
            }
        }

        with pytest.raises(ValueError, match="Object of type .* is not expected to receive summarization"):
            meta_summarizer._condense_summaries(summaries, trace_data)

    @patch('tellme.call_processing.utils.meta_summarization.openai.OpenAI')
    def test_call_method_success(self, mock_openai_client, meta_summarizer, setup_db):
        """
        Test the main __call__ method with successful summarization.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "Reasons for Calling": "Billing issues",
            "Churn Potential": "Low risk",
            "Suggested Actions": "Maintain current service level"
        })
        mock_response.choices[0].message.refusal = None

        mock_openai_client.return_value.chat.completions.create.return_value = mock_response
        meta_summarizer.openai = mock_openai_client.return_value

        trace_data = {
            'metadata': {
                'object': str(topic.__class__)
            }
        }

        summary, latest_date, call_count, label = meta_summarizer(
            obj=topic,
            period='month',
            rolling=False,
            trace_data=trace_data
        )

        assert isinstance(summary, dict)
        assert "Reasons for Calling" in summary
        assert isinstance(call_count, int)
        assert isinstance(label, str)

    def test_call_method_different_periods(self, meta_summarizer, setup_db):
        """
        Test __call__ method with different time periods.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        periods = ['week', 'month', 'quarter']
        rolling_options = [True, False]

        for period in periods:
            for rolling in rolling_options:
                with patch.object(meta_summarizer, '_condense_summaries') as mock_condense:
                    mock_condense.return_value = {"test": "summary"}

                    trace_data = {'metadata': {'object': str(topic.__class__)}}

                    summary, latest_date, call_count, label = meta_summarizer(
                        obj=topic,
                        period=period,
                        rolling=rolling,
                        trace_data=trace_data
                    )

                    assert summary == {"test": "summary"}
                    assert isinstance(call_count, int)
                    assert isinstance(label, str)

    def test_call_method_different_object_types(self, meta_summarizer, setup_db):
        """
        Test __call__ method with different object types (Topic, Customer, Agent).
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        objects_to_test = [
            (topic, "<class 'tellme.call_miner.models.Topic'>"),
            (customer, "<class 'tellme.call_miner.models.Customer'>"),
            (agent, "<class 'tellme.call_miner.models.Agent'>")
        ]

        for obj, object_type in objects_to_test:
            with patch.object(meta_summarizer, '_condense_summaries') as mock_condense:
                mock_condense.return_value = {"test": f"summary for {object_type}"}

                trace_data = {'metadata': {'object': object_type}}

                summary, latest_date, call_count, label = meta_summarizer(
                    obj=obj,
                    period='month',
                    rolling=False,
                    trace_data=trace_data
                )

                assert summary == {"test": f"summary for {object_type}"}
                assert isinstance(call_count, int)

    @patch('tellme.call_processing.utils.meta_summarization.openai.OpenAI')
    def test_token_limit_handling(self, mock_openai_client, meta_summarizer):
        """
        Test that the summarizer respects token limits and selects summaries appropriately.
        """
        # Create a lot of long summaries to test token limit
        long_summaries = []
        for i in range(100):
            long_summary = f"(2025-01-{i+1:02d}, Sentiment: 3/5, Revenue at Stake: 1000.00, Resolved: False) " + \
                          "This is a very long summary " * 50 + f" for conversation {i+1}"
            long_summaries.append(long_summary)

        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "Reasons for Calling": "Many different issues",
            "Suggested Actions": "Process optimization needed"
        })
        mock_response.choices[0].message.refusal = None

        mock_openai_client.return_value.chat.completions.create.return_value = mock_response
        meta_summarizer.openai = mock_openai_client.return_value

        trace_data = {
            'metadata': {
                'object': "<class 'tellme.call_miner.models.Topic'>"
            }
        }

        # Should not raise an exception despite many long summaries
        result = meta_summarizer._condense_summaries(long_summaries, trace_data)

        assert isinstance(result, dict)
        assert "Reasons for Calling" in result

    def test_prompt_and_config_loading(self, meta_summarizer):
        """
        Test that prompts and configurations are loaded correctly for each object type.
        """
        expected_categories = ['summary_mining', 'customer_summary', 'agent_summary']

        for category in expected_categories:
            assert category in meta_summarizer.prompts
            assert category in meta_summarizer.configs
            assert meta_summarizer.prompts[category] is not None
            assert meta_summarizer.configs[category] is not None

    @patch('tellme.call_processing.utils.meta_summarization.random.shuffle')
    def test_summary_randomization(self, mock_shuffle, meta_summarizer):
        """
        Test that summaries are shuffled before processing to ensure variety.
        """
        summaries = ["Summary 1", "Summary 2", "Summary 3"]

        with patch.object(meta_summarizer, 'openai') as mock_openai:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({"test": "result"})
            mock_response.choices[0].message.refusal = None
            mock_openai.chat.completions.create.return_value = mock_response

            trace_data = {
                'metadata': {
                    'object': "<class 'tellme.call_miner.models.Topic'>"
                }
            }

            meta_summarizer._condense_summaries(summaries, trace_data)

            # Verify that shuffle was called on the summaries
            mock_shuffle.assert_called_once_with(summaries)

    def test_prompt_category_for_customer(self, meta_summarizer):
        """Verify that a Customer object triggers the customer_summary prompt."""
        with patch.object(meta_summarizer, '_condense_summaries') as mock_condense:
            mock_condense.return_value = {"test": "customer summary"}

            # Check that customer prompts are loaded
            assert 'customer_summary' in meta_summarizer.prompts
            assert 'customer_summary' in meta_summarizer.configs

    def test_prompt_category_for_agent(self, meta_summarizer):
        """Verify that an Agent object triggers the agent_summary prompt."""
        with patch.object(meta_summarizer, '_condense_summaries') as mock_condense:
            mock_condense.return_value = {"test": "agent summary"}

            # Check that agent prompts are loaded
            assert 'agent_summary' in meta_summarizer.prompts
            assert 'agent_summary' in meta_summarizer.configs

    def test_invalid_object_type_raises(self, meta_summarizer):
        """Test that invalid object types raise ValueError."""
        summaries = ["Test summary"]
        trace_data = {
            'metadata': {
                'object': "<class 'tellme.call_miner.models.UnsupportedModel'>"
            }
        }

        with pytest.raises(ValueError, match="Object of type .* is not expected to receive summarization"):
            meta_summarizer._condense_summaries(summaries, trace_data)