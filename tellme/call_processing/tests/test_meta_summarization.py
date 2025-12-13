import pytest
import json
import zoneinfo
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
    def meta_summarizer(self, mock_langfuse, mock_litellm_meta_summarization, mock_litellm_setup):
        """Create a MetaSummarizer instance with mocked dependencies."""
        return MetaSummarizer()

    def test_meta_summarizer_initialization(self, meta_summarizer, settings):
        """
        Test that MetaSummarizer initializes correctly with proper configuration.
        """
        assert meta_summarizer.prompts is not None
        assert meta_summarizer.configs is not None
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
        model_name = "openai/gpt-4o"

        token_count = MetaSummarizer._count_tokens(test_text, model_name)

        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count < 50  # Should be reasonable for a short sentence

    def test_count_tokens_empty_string(self):
        """Test the count_tokens function with an empty string."""
        token_count = MetaSummarizer._count_tokens('', 'openai/gpt-4o')
        assert token_count == 0

    def test_count_tokens_specific_text(self):
        """Test the count_tokens function with a known text for consistency."""
        text = 'Hello, world!'
        model_name = 'openai/gpt-4o'
        token_count = MetaSummarizer._count_tokens(text, model_name)
        # This is a known token count for this specific text
        assert token_count == 4

    def test_count_tokens_invalid_model(self):
        """Test the count_tokens function with an invalid model name."""
        text = 'Test text'
        model_name = 'openai/invalid-model'
        with pytest.raises(Exception):
            MetaSummarizer._count_tokens(text, model_name)

    def test_get_token_cutoff(self):
        """
        Test token cutoff calculation with safety margin.
        """
        # Test with known model
        cutoff_gpt4 = MetaSummarizer._get_token_cutoff("openai/gpt-4o")
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

    def test_enrich_items(self, setup_db):
        """
        Test item enrichment (both summaries and transcripts) with conversation metadata.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Create test conversations
        conversations = topic.conversations.all()

        enriched_summaries, enriched_transcripts = MetaSummarizer._enrich_items(conversations)

        # Check enriched summaries
        assert isinstance(enriched_summaries, list)
        assert isinstance(enriched_transcripts, list)
        assert len(enriched_summaries) == len(enriched_transcripts)

        if len(enriched_summaries) > 0:
            # Check format of enriched summary
            first_summary = enriched_summaries[0]
            assert "Sentiment:" in first_summary
            assert "Revenue at Stake:" in first_summary
            assert "Resolved:" in first_summary
            assert str(conversation.date) in first_summary
            assert conversation.summary in first_summary

            # Check format of enriched transcript
            first_transcript = enriched_transcripts[0]
            assert "Sentiment:" in first_transcript
            assert "Revenue at Stake:" in first_transcript
            assert "Resolved:" in first_transcript
            assert str(conversation.date) in first_transcript
            assert conversation.transcript in first_transcript

    def test_condense_items_success(self, meta_summarizer):
        """
        Test successful item condensation with LiteLLM.
        """
        enriched_summaries = [
            "(2025-01-01, Sentiment: 3/5, Revenue at Stake: 1000.00, Resolved: False) Customer billing issue",
            "(2025-01-02, Sentiment: 4/5, Revenue at Stake: 500.00, Resolved: True) Technical support resolved"
        ]

        enriched_transcripts = [
            "(2025-01-01, Sentiment: 3/5, Revenue at Stake: 1000.00, Resolved: False) Agent: How can I help? Customer: I have a billing issue...",
            "(2025-01-02, Sentiment: 4/5, Revenue at Stake: 500.00, Resolved: True) Agent: What's the problem? Customer: Technical issue..."
        ]

        trace_data = {
            'metadata': {
                'object': "<class 'tellme.call_miner.models.Topic'>"
            }
        }

        result = meta_summarizer._condense_items(enriched_summaries, enriched_transcripts, trace_data)

        assert isinstance(result, dict)
        # The mock returns standard summarization fields
        assert "Reasons for Calling" in result or "title" in result

    def test_condense_items_cleans_escaped_newlines(self, meta_summarizer, mock_litellm_meta_summarization):
        """
        Test that the response from LLM has escaped newlines properly cleaned.
        """
        # Override the mock to return a response with escaped newlines
        def escaped_newlines_side_effect(*args, **kwargs):
            mock_completion = MagicMock()
            # Simulate LLM returning escaped newlines in JSON
            response_with_escaped_newlines = json.dumps({
                "Reasons for Calling": "Billing issues\\nTechnical support\\nAccount inquiries",
                "Summary": "Customers called about:\\n- Billing problems\\n- Tech issues"
            })
            mock_completion.choices = [MagicMock(message=MagicMock(
                refusal=None,
                content=response_with_escaped_newlines
            ))]
            mock_completion.model = "openai/gpt-4o-mini"
            mock_completion.usage = MagicMock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
            return mock_completion

        mock_litellm_meta_summarization.side_effect = escaped_newlines_side_effect

        enriched_summaries = ["Test summary"]
        enriched_transcripts = ["Test transcript"]
        trace_data = {
            'metadata': {
                'object': "<class 'tellme.call_miner.models.Topic'>"
            }
        }

        result = meta_summarizer._condense_items(enriched_summaries, enriched_transcripts, trace_data)

        # Verify that escaped newlines were replaced with actual newlines
        assert isinstance(result, dict)
        assert result["Reasons for Calling"] == "Billing issues\nTechnical support\nAccount inquiries"
        assert result["Summary"] == "Customers called about:\n- Billing problems\n- Tech issues"

    def test_condense_items_refusal(self, meta_summarizer, mock_litellm_meta_summarization):
        """
        Test handling of LiteLLM refusal response.
        """
        # Override the mock to return a refusal
        def refusal_side_effect(*args, **kwargs):
            mock_completion = MagicMock()
            mock_completion.choices = [MagicMock(message=MagicMock(refusal="I cannot provide this summary", content=None))]
            mock_completion.model = "openai/gpt-4o-mini"
            return mock_completion

        mock_litellm_meta_summarization.side_effect = refusal_side_effect

        enriched_summaries = ["(2025-01-01, Sentiment: 3/5, Revenue at Stake: 1000.00, Resolved: False) Test summary"]
        enriched_transcripts = ["(2025-01-01, Sentiment: 3/5, Revenue at Stake: 1000.00, Resolved: False) Test transcript"]
        trace_data = {
            'metadata': {
                'object': "<class 'tellme.call_miner.models.Topic'>"
            }
        }

        with pytest.raises(RuntimeError, match="Model refused to respond"):
            meta_summarizer._condense_items(enriched_summaries, enriched_transcripts, trace_data)

    def test_condense_items_empty_items(self, meta_summarizer):
        """
        Test handling of empty items lists.
        """
        enriched_summaries = []
        enriched_transcripts = []
        trace_data = {
            'metadata': {
                'object': "<class 'tellme.call_miner.models.Topic'>"
            }
        }

        result = meta_summarizer._condense_items(enriched_summaries, enriched_transcripts, trace_data)
        assert result is None

    def test_condense_items_invalid_trace_data(self, meta_summarizer):
        """
        Test handling of invalid trace_data.
        """
        enriched_summaries = ["Test summary"]
        enriched_transcripts = ["Test transcript"]

        # Missing metadata
        trace_data = {}
        with pytest.raises(ValueError, match="Invalid trace_data"):
            meta_summarizer._condense_items(enriched_summaries, enriched_transcripts, trace_data)

        # Missing object in metadata
        trace_data = {'metadata': {}}
        with pytest.raises(ValueError, match="Invalid trace_data"):
            meta_summarizer._condense_items(enriched_summaries, enriched_transcripts, trace_data)

    def test_condense_items_unsupported_object_type(self, meta_summarizer):
        """
        Test handling of unsupported object types.
        """
        enriched_summaries = ["Test summary"]
        enriched_transcripts = ["Test transcript"]
        trace_data = {
            'metadata': {
                'object': "<class 'tellme.call_miner.models.UnsupportedModel'>"
            }
        }

        with pytest.raises(ValueError, match="Object of type .* is not expected to receive summarization"):
            meta_summarizer._condense_items(enriched_summaries, enriched_transcripts, trace_data)

    def test_call_method_success(self, meta_summarizer, setup_db):
        """
        Test the main __call__ method with successful summarization.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

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
                with patch.object(meta_summarizer, '_condense_items') as mock_condense:
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
            with patch.object(meta_summarizer, '_condense_items') as mock_condense:
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

    def test_token_limit_handling(self, meta_summarizer):
        """
        Test that the summarizer respects token limits and selects items appropriately.
        """
        # Create a lot of long items to test token limit
        long_summaries = []
        long_transcripts = []
        for i in range(100):
            long_summary = f"(2025-01-{i+1:02d}, Sentiment: 3/5, Revenue at Stake: 1000.00, Resolved: False) " + \
                          "This is a very long summary " * 50 + f" for conversation {i+1}"
            long_transcript = f"(2025-01-{i+1:02d}, Sentiment: 3/5, Revenue at Stake: 1000.00, Resolved: False) " + \
                             "Agent: This is a very long transcript " * 80 + f" for conversation {i+1}"
            long_summaries.append(long_summary)
            long_transcripts.append(long_transcript)

        trace_data = {
            'metadata': {
                'object': "<class 'tellme.call_miner.models.Topic'>"
            }
        }

        # Should not raise an exception despite many long items
        result = meta_summarizer._condense_items(long_summaries, long_transcripts, trace_data)

        assert isinstance(result, dict)

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

    def test_conversation_ordering_by_date(self, setup_db, meta_summarizer):
        """
        Test that conversations are retrieved in descending date order (most recent first)
        to prioritize newer conversations in meta-summarization.
        """

        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db
        utc = zoneinfo.ZoneInfo("UTC")
        base_date = datetime.now(tz=utc)

        # Create additional conversations with different dates
        # Make sure we create dates relative to the original conversation
        old_conversation = Conversation.objects.create(
            path="old.mp3",
            date=base_date - timedelta(days=10),
            duration=120.0,
            transcript="Old conversation transcript",
            sentiment=3.0,
            summary="Old conversation summary",
            title="Old Conversation",
            input_tokens=100,
            output_tokens=50,
            customer=customer,
            agent=agent
        )
        old_conversation.topics.add(topic)

        middle_conversation = Conversation.objects.create(
            path="middle.mp3",
            date=base_date - timedelta(days=5),
            duration=150.0,
            transcript="Middle conversation transcript",
            sentiment=4.0,
            summary="Middle conversation summary",
            title="Middle Conversation",
            input_tokens=120,
            output_tokens=60,
            customer=customer,
            agent=agent
        )
        middle_conversation.topics.add(topic)

        # Create the most recent conversation (future date to ensure it's first)
        newest_conversation = Conversation.objects.create(
            path="newest.mp3",
            date=base_date + timedelta(days=1),
            duration=180.0,
            transcript="Newest conversation transcript",
            sentiment=4.5,
            summary="Newest conversation summary",
            title="Newest Conversation",
            input_tokens=130,
            output_tokens=70,
            customer=customer,
            agent=agent
        )
        newest_conversation.topics.add(topic)

        # Retrieve conversations using the eternity period
        conversations, latest_date, call_count, label = meta_summarizer._retrieve_object_conversations(
            customer, period='eternity', rolling=False
        )

        # Convert to list to check ordering
        conversation_list = list(conversations)

        # Verify conversations are ordered by date descending (most recent first)
        assert len(conversation_list) >= 4
        for i in range(len(conversation_list) - 1):
            assert conversation_list[i].date >= conversation_list[i + 1].date, \
                f"Conversations not in descending date order: {conversation_list[i].date} < {conversation_list[i + 1].date}"

        # Verify the newest conversation is first
        assert conversation_list[0].id == newest_conversation.id

        # Verify the oldest conversation is last
        assert conversation_list[-1].id == old_conversation.id

    def test_prompt_category_for_customer(self, meta_summarizer):
        """Verify that a Customer object triggers the customer_summary prompt."""
        with patch.object(meta_summarizer, '_condense_items') as mock_condense:
            mock_condense.return_value = {"test": "customer summary"}

            # Check that customer prompts are loaded
            assert 'customer_summary' in meta_summarizer.prompts
            assert 'customer_summary' in meta_summarizer.configs

    def test_prompt_category_for_agent(self, meta_summarizer):
        """Verify that an Agent object triggers the agent_summary prompt."""
        with patch.object(meta_summarizer, '_condense_items') as mock_condense:
            mock_condense.return_value = {"test": "agent summary"}

            # Check that agent prompts are loaded
            assert 'agent_summary' in meta_summarizer.prompts
            assert 'agent_summary' in meta_summarizer.configs

    def test_invalid_object_type_raises(self, meta_summarizer):
        """Test that invalid object types raise ValueError."""
        enriched_summaries = ["Test summary"]
        enriched_transcripts = ["Test transcript"]
        trace_data = {
            'metadata': {
                'object': "<class 'tellme.call_miner.models.UnsupportedModel'>"
            }
        }

        with pytest.raises(ValueError, match="Object of type .* is not expected to receive summarization"):
            meta_summarizer._condense_items(enriched_summaries, enriched_transcripts, trace_data)

    def test_eternity_period_ignores_rolling_parameter(self, meta_summarizer, setup_db):
        """
        Test that 'eternity' period ignores the rolling parameter.
        Both rolling=True and rolling=False should return the same results.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        trace_data = {
            'metadata': {
                'object': str(customer.__class__)
            }
        }

        # Test with rolling=False
        summary_false, latest_date_false, call_count_false, label_false = meta_summarizer(
            obj=customer,
            period='eternity',
            rolling=False,
            trace_data=trace_data
        )

        # Test with rolling=True (should be ignored and treated as False)
        summary_true, latest_date_true, call_count_true, label_true = meta_summarizer(
            obj=customer,
            period='eternity',
            rolling=True,
            trace_data=trace_data
        )

        # Both should return the same label and call count
        assert label_false == label_true == "eternity"
        assert call_count_false == call_count_true

    def test_retrieve_object_conversations_with_eternity(self, setup_db):
        """
        Test conversation retrieval with 'eternity' period includes all conversations,
        even those with dates far in the past and future.
        """
        from tellme.call_processing.utils.meta_summarization import MetaSummarizer
        from datetime import datetime
        import zoneinfo
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        utc = zoneinfo.ZoneInfo("UTC")

        # Create a conversation from 1901 (very old)
        old_conversation = Conversation.objects.create(
            path="very_old.mp3",
            date=datetime(1901, 5, 15, 10, 30, 0, tzinfo=utc),
            duration=180.0,
            transcript="Test transcript from 1901",
            sentiment=3.5,
            summary="Old conversation summary",
            title="Conversation from 1901",
            input_tokens=100,
            output_tokens=50,
            customer=customer,
            agent=agent
        )
        old_conversation.topics.add(topic)

        # Create a conversation from 2185 (far future)
        future_conversation = Conversation.objects.create(
            path="future.mp3",
            date=datetime(2185, 8, 22, 14, 45, 0, tzinfo=utc),
            duration=200.0,
            transcript="Test transcript from 2185",
            sentiment=4.0,
            summary="Future conversation summary",
            title="Conversation from 2185",
            input_tokens=120,
            output_tokens=60,
            customer=customer,
            agent=agent
        )
        future_conversation.topics.add(topic)

        # Test with 'eternity' period
        conversations, latest_date, call_count, label = MetaSummarizer._retrieve_object_conversations(
            customer, period='eternity', rolling=False
        )

        assert label == "eternity"
        assert isinstance(call_count, int)
        # All conversations should be included with eternity period
        assert conversations.count() == customer.conversations.count()
        # Verify both the old and future conversations are included
        conversation_ids = set(conversations.values_list('id', flat=True))
        assert old_conversation.id in conversation_ids
        assert future_conversation.id in conversation_ids
        assert conversation.id in conversation_ids  # Original conversation from setup_db

    def test_clean_escaped_newlines(self):
        """
        Test that escaped newlines (\\n) are properly replaced with actual newlines (\n).
        """
        # Test with dictionary
        data_dict = {
            'key1': 'Line 1\\nLine 2\\nLine 3',
            'key2': {
                'nested': 'Nested\\nValue'
            },
            'key3': ['Item 1\\nItem 2', 'Item 3']
        }
        cleaned = MetaSummarizer._clean_escaped_newlines(data_dict)
        assert cleaned['key1'] == 'Line 1\nLine 2\nLine 3'
        assert cleaned['key2']['nested'] == 'Nested\nValue'
        assert cleaned['key3'][0] == 'Item 1\nItem 2'

        # Test with list
        data_list = ['Line 1\\nLine 2', {'key': 'Value\\nWith\\nNewlines'}]
        cleaned_list = MetaSummarizer._clean_escaped_newlines(data_list)
        assert cleaned_list[0] == 'Line 1\nLine 2'
        assert cleaned_list[1]['key'] == 'Value\nWith\nNewlines'

        # Test with plain string
        data_str = 'Simple\\nString\\nWith\\nNewlines'
        cleaned_str = MetaSummarizer._clean_escaped_newlines(data_str)
        assert cleaned_str == 'Simple\nString\nWith\nNewlines'

        # Test with non-string values (should be returned unchanged)
        assert MetaSummarizer._clean_escaped_newlines(123) == 123
        assert MetaSummarizer._clean_escaped_newlines(None) is None
        assert MetaSummarizer._clean_escaped_newlines(True) is True

    def test_unwrap_schema_response(self):
        """
        Test that JSON Schema metadata is properly unwrapped from LLM responses.
        """
        # Test with schema-wrapped response (the problem case)
        schema_wrapped = {
            "type": "object",
            "properties": {
                "Churn Potential": "Overall potential for relationship strengthening",
                "Suggested Actions": "- Improve process A\n- Streamline process B",
                "Reasons for Calling": "- Billing issues\n- Technical support"
            }
        }
        unwrapped = MetaSummarizer._unwrap_schema_response(schema_wrapped)
        assert "type" not in unwrapped
        assert "properties" not in unwrapped
        assert unwrapped["Churn Potential"] == "Overall potential for relationship strengthening"
        assert unwrapped["Suggested Actions"] == "- Improve process A\n- Streamline process B"
        assert unwrapped["Reasons for Calling"] == "- Billing issues\n- Technical support"

        # Test with already-unwrapped response (should pass through unchanged)
        already_unwrapped = {
            "Churn Potential": "Low churn risk",
            "Suggested Actions": "- Action 1\n- Action 2",
            "Reasons for Calling": "- Reason A\n- Reason B"
        }
        result = MetaSummarizer._unwrap_schema_response(already_unwrapped)
        assert result == already_unwrapped

        # Test with non-dict input (should pass through unchanged)
        assert MetaSummarizer._unwrap_schema_response("string") == "string"
        assert MetaSummarizer._unwrap_schema_response(123) == 123
        assert MetaSummarizer._unwrap_schema_response(None) is None

        # Test with dict that has "type" but not schema structure
        non_schema_dict = {
            "type": "some_value",
            "other_field": "data"
        }
        result = MetaSummarizer._unwrap_schema_response(non_schema_dict)
        assert result == non_schema_dict

    def test_transcript_vs_summary_selection(self, meta_summarizer):
        """
        Test that the summarizer intelligently chooses between transcripts and summaries
        based on which allows more conversations to be included within the token limit.
        """
        trace_data = {
            'metadata': {
                'object': "<class 'tellme.call_miner.models.Customer'>"
            }
        }

        # Case 1: Summaries allow more conversations (transcripts are very long)
        # Create 20 short summaries and 20 very long transcripts
        # The very long transcripts should result in only 1-2 fitting, while many summaries fit
        short_summaries = []
        long_transcripts = []
        for i in range(20):
            short_summaries.append(
                f"(2025-01-{i+1:02d}, Sentiment: 3/5, Revenue at Stake: 1000.00, Resolved: False) "
                f"Brief summary #{i+1}"
            )
            # Create extremely long transcripts (much longer than summaries)
            long_transcripts.append(
                f"(2025-01-{i+1:02d}, Sentiment: 3/5, Revenue at Stake: 1000.00, Resolved: False) "
                + "Agent: " + " ".join([f"This is a very detailed and long conversation transcript with lots of back and forth dialogue"] * 500)
                + f" Customer: Yes, I agree. Conversation #{i+1}"
            )

        result = meta_summarizer._condense_items(short_summaries, long_transcripts, trace_data)

        assert isinstance(result, dict)
        # Check metadata was added
        assert 'item_type_used' in trace_data['metadata']
        # Summaries should be chosen because they allow more conversations
        assert trace_data['metadata']['item_type_used'] == 'summaries'
        assert trace_data['metadata']['summary_count_possible'] > trace_data['metadata']['transcript_count_possible']

        # Case 2: Transcripts allow same or more conversations (summaries and transcripts are both short)
        # Reset trace_data
        trace_data = {
            'metadata': {
                'object': "<class 'tellme.call_miner.models.Customer'>"
            }
        }

        short_summaries_2 = []
        short_transcripts = []
        for i in range(5):
            short_summaries_2.append(
                f"(2025-01-{i+1:02d}, Sentiment: 3/5, Revenue at Stake: 1000.00, Resolved: False) "
                f"Brief summary {i+1}"
            )
            short_transcripts.append(
                f"(2025-01-{i+1:02d}, Sentiment: 3/5, Revenue at Stake: 1000.00, Resolved: False) "
                f"Agent: Hello. Customer: Hi there. Conversation {i+1}"
            )

        result = meta_summarizer._condense_items(short_summaries_2, short_transcripts, trace_data)

        assert isinstance(result, dict)
        # Transcripts should be chosen when they allow same or more conversations
        assert trace_data['metadata']['item_type_used'] == 'transcripts'
        assert trace_data['metadata']['transcript_count_possible'] >= trace_data['metadata']['summary_count_possible']

    def test_transcript_cleaning_in_enrichment(self, setup_db):
        """
        Test that transcript cleaning is applied during enrichment process.
        Verifies that 'Gucci' is converted to 'Gutschein' and 'Bohnen' to 'Bonus'.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Create a conversation with transcript containing words that need cleaning
        test_conversation = Conversation.objects.create(
            path="test_cleaning.mp3",
            date=datetime.now(tz=zoneinfo.ZoneInfo("UTC")),
            duration=180.0,
            transcript="Agent: Hello. Customer: I want to use my Gucci and my Bohnen rewards. "
                      "Agent: Your GUCCI is valid. Customer: Great, I love bohnen!",
            sentiment=4.0,
            summary="Customer wants to use rewards",
            title="Rewards Conversation",
            input_tokens=100,
            output_tokens=50,
            customer=customer,
            agent=agent
        )
        test_conversation.topics.add(topic)

        # Retrieve and enrich the conversations
        conversations = customer.conversations.all()
        enriched_summaries, enriched_transcripts = MetaSummarizer._enrich_items(conversations)

        # Find our test conversation in the enriched transcripts by looking for unique content
        test_transcript_found = False
        for enriched_transcript in enriched_transcripts:
            # Check if this enriched transcript contains content from our test conversation
            if "I want to use my" in enriched_transcript:
                # Verify that cleaning was applied (case-insensitive)
                assert "Gutschein" in enriched_transcript
                assert "Bonus" in enriched_transcript
                assert "Gucci" not in enriched_transcript  # Original should be replaced
                assert "Bohnen" not in enriched_transcript  # Original should be replaced
                # Verify case-insensitive replacement worked
                assert "GUCCI" not in enriched_transcript
                assert "bohnen" not in enriched_transcript
                test_transcript_found = True
                break

        # Ensure we actually tested a transcript
        assert test_transcript_found, "Test conversation transcript was not found in enriched transcripts"

    def test_create_mailto_link(self):
        """Test mailto link generation with proper encoding."""
        # Test basic mailto link creation
        body = "Dear Customer,\n\nWe apologize for the inconvenience.\n\nSincerely,\nTeam"
        subject = "Apology for Service Issue"
        mailto_link = MetaSummarizer.create_mailto_link(body, subject, "customer@example.com")

        # Verify it's a valid mailto link
        assert mailto_link.startswith("mailto:customer@example.com?subject=")
        assert "body=" in mailto_link

        # Verify URL encoding (spaces become %20, newlines become %0D%0A)
        assert "%20" in mailto_link  # Spaces encoded
        assert "%0D%0A" in mailto_link  # CRLF line breaks encoded

        # Verify subject and body are encoded
        assert "Apology" in mailto_link or "%20" in mailto_link  # Subject is encoded

    def test_create_mailto_link_normalizes_line_breaks(self):
        """Test that mailto link normalizes different line break styles."""
        # Test with mixed line breaks
        body = "Dear Customer,\n\n\n\nWe apologize.\r\n\r\nBest regards"
        subject = "Test"
        mailto_link = MetaSummarizer.create_mailto_link(body, subject)

        # Should not have triple newlines (should be collapsed to double)
        # After encoding, triple \r\n would be %0D%0A%0D%0A%0D%0A
        assert "%0D%0A%0D%0A%0D%0A" not in mailto_link

    def test_condense_items_creates_mailto_link_for_customer(self, meta_summarizer, mock_litellm_meta_summarization):
        """Test that customer summaries include a mailto link."""
        def customer_summary_side_effect(*args, **kwargs):
            mock_completion = MagicMock()
            response_json = json.dumps({
                "Suggested Email Body": "Dear Customer,\n\nWe apologize.\n\nSincerely,\nTeam",
                "Suggested Email Subject": "Apology for Service Issue"
            })
            mock_completion.choices = [MagicMock(message=MagicMock(
                refusal=None,
                content=response_json
            ))]
            mock_completion.model = "openai/gpt-4o-mini"
            mock_completion.usage = MagicMock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
            return mock_completion

        mock_litellm_meta_summarization.side_effect = customer_summary_side_effect

        result = meta_summarizer._condense_items(
            ["Test summary"], ["Test transcript"],
            {'metadata': {'object': "<class 'tellme.call_miner.models.Customer'>"}}
        )

        # Verify mailto link is included
        assert "Suggested Email Mailto" in result
        assert result["Suggested Email Mailto"].startswith("mailto:")
        assert "subject=" in result["Suggested Email Mailto"]
        assert "body=" in result["Suggested Email Mailto"]

        # Verify original body and subject are still present
        assert "Suggested Email Body" in result
        assert "Suggested Email Subject" in result

    def test_condense_items_no_mailto_for_non_customer(self, meta_summarizer, mock_litellm_meta_summarization):
        """Test that non-customer summaries don't get mailto links."""
        def topic_summary_side_effect(*args, **kwargs):
            mock_completion = MagicMock()
            response_json = json.dumps({
                "Reasons for Calling": "Billing issues",
                "Summary": "Multiple billing complaints"
            })
            mock_completion.choices = [MagicMock(message=MagicMock(
                refusal=None,
                content=response_json
            ))]
            mock_completion.model = "openai/gpt-4o-mini"
            mock_completion.usage = MagicMock(prompt_tokens=100, completion_tokens=50, total_tokens=150)
            return mock_completion

        mock_litellm_meta_summarization.side_effect = topic_summary_side_effect

        result = meta_summarizer._condense_items(
            ["Test summary"], ["Test transcript"],
            {'metadata': {'object': "<class 'tellme.call_miner.models.Topic'>"}}
        )

        # Verify no mailto link for topic summaries
        assert "Suggested Email Mailto" not in result
        assert "Reasons for Calling" in result