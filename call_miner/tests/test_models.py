import pytest
import pytz
from datetime import timedelta, datetime
from django.db import IntegrityError

from call_miner.models import (
    Organization,
    Topic,
    Customer,
    Conversation,
    Employee,
    Analyst,
    Agent,
)


@pytest.fixture(autouse=True)
def register_signals():
    """
    Fixture to ensure signals are registered during tests.
    """
    from call_miner.models import Topic, Agent, Customer, Conversation
    Topic.register_signals(Conversation, related_field='topics')
    Agent.register_signals(Conversation, related_field='agent')
    Customer.register_signals(Conversation, related_field='customer')


@pytest.fixture
def analyst(organization, user):
    return Analyst.objects.create(organization=organization, user=user)


@pytest.fixture
def agent(user, organization):
    return Agent.objects.create(user=user, organization=organization)


@pytest.fixture
def manager(another_user, organization):
    return Agent.objects.create(user=another_user, organization=organization)


@pytest.fixture
def another_topic_same_organization(organization):
    return Topic.objects.create(name="Another Topic", description="Another Description", organization=organization)


@pytest.fixture
def another_conversation_same_organization(agent, customer, another_topic_same_organization):
    another_conv = Conversation.objects.create(
        path="Another Test Call",
        date=datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC) + timedelta(days=1),
        duration=45,
        transcript="<agent>: How can I help you? <customer>: I have an issue.",
        sentiment=0.6,
        summary="Another Summary",
        title='Another Test Title',
        customer=customer,
        agent=agent,
        input_tokens=5,
        output_tokens=15
    )
    another_conv.topics.add(another_topic_same_organization)
    return another_conv


@pytest.mark.django_db
class TestMetaSummaryAbstractModel:
    def test_meta_summary_creation(self, topic, conversation, mocker):
        """
        Test that get_or_create_summary method creates a summary for the Topic.
        """
        mock_condense = mocker.patch('call_miner.models.condense_summaries', return_value="Mocked Summary")
        topic.get_or_create_summary()
        mock_condense.assert_called_once_with([conversation.summary])
        assert topic.summary == "Mocked Summary"
        assert topic.summary_call_count == 1
        assert topic.summary_date == conversation.date

    def test_meta_summary_no_update_when_deviation_not_significant(self, topic, conversation, mocker):
        """
        Test that get_or_create_summary does not update the summary if deviation is not significant.
        """
        topic.summary_call_count = 1
        topic.summary = "Existing Summary"
        topic.summary_date = conversation.date
        topic.save()

        mock_condense = mocker.patch('call_miner.models.condense_summaries')
        topic.get_or_create_summary()
        mock_condense.assert_not_called()
        assert topic.summary == "Existing Summary"

    def test_is_deviation_significant(self, topic):
        """
        Test the is_deviation_significant method for various scenarios.
        """
        topic.summary_call_count = 100
        topic.save()
        assert topic.is_deviation_significant(111) is True
        assert topic.is_deviation_significant(89) is True
        assert topic.is_deviation_significant(110) is False
        assert topic.is_deviation_significant(90) is False
        assert topic.is_deviation_significant(100) is False
        topic.summary_call_count = 0
        topic.save()
        assert topic.is_deviation_significant(1) is True
        assert topic.is_deviation_significant(0) is False

    def test_get_or_create_summary_no_conversations(self, topic, mocker):
        """
        Test that get_or_create_summary does nothing when there are no conversations.
        """
        mock_condense = mocker.patch('call_miner.models.condense_summaries', return_value=None)
        topic.get_or_create_summary()
        assert not mock_condense.called
        assert topic.summary is None


@pytest.mark.django_db
class TestConversationStatsAbstractModel:
    def test_conversation_stats_empty(self, topic):
        """
        Test that the conversation stats are correctly updated when there are no conversations.
        """
        topic.update_conversation_stats()
        assert topic.conversation_count == 0
        assert topic.first_conversation_date is None
        assert topic.last_conversation_date is None

    def test_conversation_stats_single_conversation(self, topic, conversation):
        """
        Test that the conversation stats are correctly updated when there is one conversation.
        """
        topic.update_conversation_stats()
        topic.refresh_from_db()
        assert topic.conversation_count == 1
        assert topic.first_conversation_date == conversation.date
        assert topic.last_conversation_date == conversation.date

    def test_conversation_stats_multiple_conversations(self, topic, conversation,
                                                       another_conversation_same_organization):
        """
        Test that the conversation stats are correctly updated when there are multiple conversations.
        """
        another_conversation_same_organization.topics.add(topic)
        topic.update_conversation_stats()
        topic.refresh_from_db()
        expected_first_date = min(conversation.date, another_conversation_same_organization.date)
        expected_last_date = max(conversation.date, another_conversation_same_organization.date)
        assert topic.conversation_count == 2
        assert topic.first_conversation_date == expected_first_date
        assert topic.last_conversation_date == expected_last_date

    def test_conversation_stats_updates_on_delete(self, topic, conversation):
        """
        Test that the conversation stats are updated when a conversation is deleted.
        """
        conversation.delete()
        topic.refresh_from_db()
        assert topic.conversation_count == 0
        assert topic.first_conversation_date is None
        assert topic.last_conversation_date is None

    def test_agent_conversation_stats(self, agent, conversation):
        """
        Test that conversation stats are updated for an agent.
        """
        agent.update_conversation_stats()
        agent.refresh_from_db()
        assert agent.conversation_count == 1
        assert agent.first_conversation_date == conversation.date
        assert agent.last_conversation_date == conversation.date

    def test_agent_conversation_stats_multiple_conversations(self, agent, conversation,
                                                             another_conversation_same_organization):
        """
        Test that conversation stats are correctly updated for an agent with multiple conversations.
        """
        another_conversation_same_organization.agent = agent
        another_conversation_same_organization.save()
        agent.update_conversation_stats()
        agent.refresh_from_db()
        expected_first_date = min(conversation.date, another_conversation_same_organization.date)
        expected_last_date = max(conversation.date, another_conversation_same_organization.date)
        assert agent.conversation_count == 2
        assert agent.first_conversation_date == expected_first_date
        assert agent.last_conversation_date == expected_last_date

    def test_agent_conversation_stats_after_delete(self, agent, conversation):
        """
        Test that conversation stats are updated for an agent after conversation deletion.
        """
        conversation.delete()
        agent.refresh_from_db()
        assert agent.conversation_count == 0
        assert agent.first_conversation_date is None
        assert agent.last_conversation_date is None

    def test_customer_conversation_stats(self, customer, conversation):
        """
        Test that conversation stats are updated for a customer.
        """
        customer.update_conversation_stats()
        customer.refresh_from_db()
        assert customer.conversation_count == 1
        assert customer.first_conversation_date == conversation.date
        assert customer.last_conversation_date == conversation.date

    def test_customer_conversation_stats_multiple_conversations(self, customer, conversation,
                                                                another_conversation_same_organization):
        """
        Test that conversation stats are correctly updated for a customer with multiple conversations.
        """
        another_conversation_same_organization.customer = customer
        another_conversation_same_organization.save()
        customer.update_conversation_stats()
        customer.refresh_from_db()
        expected_first_date = min(conversation.date, another_conversation_same_organization.date)
        expected_last_date = max(conversation.date, another_conversation_same_organization.date)
        assert customer.conversation_count == 2
        assert customer.first_conversation_date == expected_first_date
        assert customer.last_conversation_date == expected_last_date

    def test_customer_conversation_stats_after_delete(self, customer, conversation):
        """
        Test that conversation stats are updated for a customer after conversation deletion.
        """
        conversation.delete()
        customer.refresh_from_db()
        assert customer.conversation_count == 0
        assert customer.first_conversation_date is None
        assert customer.last_conversation_date is None


@pytest.mark.django_db
class TestConversationTrendMixin:
    def test_conversations_scope_organization(self, organization, agent, customer, conversation):
        """
        Test that the conversations_scope method retrieves all conversations for an organization.
        """
        assert conversation in organization.conversations_scope

    def test_conversations_scope_agent_manager(self, organization, agent, manager, customer, conversation):
        """
        Test that the conversations_scope method retrieves all conversations for a manager and their team.
        """
        agent.manager = manager
        agent.save()
        assert conversation in manager.conversations_scope
        assert conversation in agent.conversations_scope

    def test_conversations_scope_agent_non_manager(self, agent, conversation):
        """
        Test that the conversations_scope method retrieves only the agent's own conversations if they are not a manager.
        """
        assert conversation in agent.conversations_scope

    def test_conversations_scope_direct_relationship(self, customer, conversation):
        """
        Test that the conversations_scope method retrieves the conversations directly related to a customer.
        """
        assert conversation in customer.conversations_scope

    def test_get_conversation_trend_invalid_period(self, topic):
        """
        Tests the required input format for get_conversation_trend.
        """
        with pytest.raises(ValueError):
            topic.get_conversation_trend('invalid_period')

    def test_get_conversation_trend_empty(self, topic):
        """
        Test that get_conversation_trend returns an empty list when there are no conversations.
        """
        trend = list(topic.get_conversation_trend('daily'))
        assert len(trend) == 0

    def test_get_conversation_trend_single_conversation(self, topic, conversation):
        """
        Test that get_conversation_trend returns the correct trend for a single conversation.
        """
        trend = list(topic.get_conversation_trend('daily'))
        assert len(trend) == 1
        assert trend[0]['count'] == 1

    def test_get_conversation_trend_multiple_conversations(self, topic, conversation,
                                                           another_conversation_same_organization):
        """
        Test that get_conversation_trend returns the correct trend for multiple conversations on different dates.
        """
        another_conversation_same_organization.topics.add(topic)
        trend = list(topic.get_conversation_trend('daily'))
        assert len(trend) == 2

    def test_get_conversation_trend_per_topic_invalid_period(self, topic):
        """
        Tests the required input format for get_conversation_trend_per_topic.
        """
        with pytest.raises(ValueError):
            topic.get_conversation_trend_per_topic('invalid_period')

    def test_get_conversation_trend_per_topic_empty(self, customer):
        """
        Test that get_conversation_trend_per_topic returns an empty list when there are no conversations.
        """
        trend = list(customer.get_conversation_trend_per_topic('daily'))
        assert len(trend) == 0

    def test_get_conversation_trend_per_topic_single_conversation(self, customer, conversation, topic):
        """
        Test that get_conversation_trend_per_topic returns the correct trend for a single conversation.
        """
        trend = list(customer.get_conversation_trend_per_topic('daily'))
        assert len(trend) == 1
        assert trend[0]['count'] == 1
        assert trend[0]['topic'] == topic.name

    def test_get_conversation_trend_per_topic_multiple_conversations(self, customer, conversation,
                                                                     another_conversation_same_organization,
                                                                     another_topic_same_organization):
        """
        Test that get_conversation_trend_per_topic returns the correct trend for multiple conversations with different
        topics.
        """
        another_conversation_same_organization.topics.add(another_topic_same_organization)
        trend = list(customer.get_conversation_trend_per_topic('daily'))
        assert len(trend) == 2

    def test_get_avg_for_periods_invalid_field(self, topic):
        """
        Tests the required input format for get_avg_for_periods.
        """
        with pytest.raises(ValueError):
            topic.get_avg_for_periods('invalid_field', 'daily')

    def test_get_avg_for_periods_invalid_period(self, topic):
        with pytest.raises(ValueError):
            topic.get_avg_for_periods('duration', 'invalid_period')

    def test_get_avg_duration_empty(self, topic):
        """
        Test that get_avg_duration returns empty results when there are no conversations.
        """
        avg_duration = list(topic.get_avg_for_periods('duration', 'daily'))
        assert len(avg_duration) == 0

    def test_get_avg_duration_single_conversation(self, topic, conversation):
        """
        Test that get_avg_duration returns the correct average duration for a single conversation.
        """
        avg_duration = list(topic.get_avg_for_periods('duration', 'daily'))
        assert len(avg_duration) == 1
        assert avg_duration[0]['avg_value'] == conversation.duration

    def test_get_daily_avg_duration_multiple_conversations(self, topic, conversation,
                                                           another_conversation_same_organization):
        """
        Test that get_avg_duration returns the correct average daily duration for multiple conversations over different
        days.
        """
        another_conversation_same_organization.topics.add(topic)
        avg_duration = list(topic.get_avg_for_periods('duration', 'daily'))
        assert len(avg_duration) == 2

    def test_get_weekly_avg_duration_multiple_conversations(self, topic, conversation,
                                                            another_conversation_same_organization):
        """
        Test that get_avg_duration returns the correct average weekly duration for multiple conversations over different
        days.
        """
        another_conversation_same_organization.topics.add(topic)
        avg_duration = list(topic.get_avg_for_periods('duration', 'weekly'))
        assert len(avg_duration) == 1

    def test_get_monthly_avg_duration_multiple_conversations(self, topic, conversation,
                                                             another_conversation_same_organization):
        """
        Test that get_avg_duration returns the correct average monthly duration for multiple conversations over
        different days.
        """
        another_conversation_same_organization.topics.add(topic)
        avg_duration = list(topic.get_avg_for_periods('duration', 'monthly'))
        assert len(avg_duration) == 1

    def test_get_avg_sentiment_empty(self, topic):
        """
        Test that get_avg_sentiment returns empty results when there are no conversations.
        """
        avg_sentiment = list(topic.get_avg_for_periods('sentiment', 'daily'))
        assert len(avg_sentiment) == 0

    def test_get_avg_sentiment_single_conversation(self, topic, conversation):
        """
        Test that get_avg_sentiment returns the correct average sentiment for a single conversation.
        """
        avg_sentiment = list(topic.get_avg_for_periods('sentiment', 'monthly'))
        assert len(avg_sentiment) == 1
        assert avg_sentiment[0]['avg_value'] == conversation.sentiment

    def test_get_daily_avg_sentiment_multiple_conversations(self, topic, conversation,
                                                            another_conversation_same_organization):
        """
        Test that get_avg_sentiment returns the correct daily average sentiment for multiple conversations over
        different days.
        """
        another_conversation_same_organization.topics.add(topic)
        avg_sentiment = list(topic.get_avg_for_periods('sentiment', 'daily'))
        assert len(avg_sentiment) == 2

    def test_get_weekly_avg_sentiment_multiple_conversations(self, topic, conversation,
                                                             another_conversation_same_organization):
        """
        Test that get_avg_sentiment returns the correct weekly average sentiment for multiple conversations over
        different days.
        """
        another_conversation_same_organization.topics.add(topic)
        avg_sentiment = list(topic.get_avg_for_periods('sentiment', 'weekly'))
        assert len(avg_sentiment) == 1

    def test_get_monthly_avg_sentiment_multiple_conversations(self, topic, conversation,
                                                              another_conversation_same_organization):
        """
        Test that get_avg_sentiment returns the correct monthly average sentiment for multiple conversations over
        different days.
        """
        another_conversation_same_organization.topics.add(topic)
        avg_sentiment = list(topic.get_avg_for_periods('sentiment', 'monthly'))
        assert len(avg_sentiment) == 1


@pytest.mark.django_db
class TestOrganization:
    def test_organization_creation(self, organization):
        """
        Test that an Organization instance is created with the correct name.
        """
        assert organization.name == "Test Organization"

    def test_organization_name_uniqueness(self):
        """
        Test that creating an Organization with a duplicate name raises an IntegrityError.
        """
        Organization.objects.create(name="Unique Organization")
        with pytest.raises(IntegrityError):
            Organization.objects.create(name="Unique Organization")

    def test_organization_str(self, organization):
        """
        Test that the string representation of an Organization is its name.
        """
        assert str(organization) == "Test Organization"

    def test_organization_verbose_name_plural(self):
        """
        Test that the verbose name plural for Organization is "Organizations".
        """
        assert Organization._meta.verbose_name_plural == "Organizations"

    def test_organization_inherits_conversation_trends(self, organization):
        """
        Test that Organizations have the functionalities inherited from ConversationTrendMixin.
        """
        assert hasattr(organization, 'get_conversation_trend')
        assert hasattr(organization, 'get_conversation_trend_per_topic')
        assert hasattr(organization, 'get_avg_for_periods')


@pytest.mark.django_db
class TestTopic:
    def test_topic_creation(self, topic, organization):
        """
        Test that a Topic instance is created with the correct attributes.
        """
        assert topic.name == "Test Topic"
        assert topic.description == "A test topic"
        assert topic.organization == organization
        assert str(topic) == "Test Topic"

    def test_topic_unique_together(self, topic, organization):
        """
        Test that creating a Topic with a duplicate name in the same organization raises an IntegrityError.
        """
        with pytest.raises(IntegrityError):
            Topic.objects.create(name="Test Topic", description="Another Description", organization=organization)

    def test_topic_inherits_metasummary_model(self, topic):
        """
        Test that Topics have the functionalities inherited from MetaSummaryAbstractModel.
        """
        assert hasattr(topic, 'get_or_create_summary')
        assert hasattr(topic, 'is_deviation_significant')

    def test_topic_inherits_conversation_stats_model(self, topic):
        """
        Test that Topics have the functionalities inherited from ConversationStatsAbstractModel.
        """
        assert hasattr(topic, 'update_conversation_stats')

    def test_topic_inherits_conversation_trends(self, topic):
        """
        Test that Topics have the functionalities inherited from ConversationTrendMixin.
        """
        assert hasattr(topic, 'get_conversation_trend')
        assert hasattr(topic, 'get_conversation_trend_per_topic')
        assert hasattr(topic, 'get_avg_for_periods')


@pytest.mark.django_db
class TestAnalyst:
    def test_analyst_creation(self, analyst, organization, user):
        """
        Test that an Analyst instance is created with the correct attributes.
        """
        assert analyst.organization == organization
        assert analyst.user == user
        assert str(analyst) == f"{user.username} - {organization.name} - Analyst"

    def test_analyst_unique_together(self, analyst, organization):
        """
        Test that creating an Analyst with a duplicate user in the same organization raises an IntegrityError.
        """
        with pytest.raises(IntegrityError):
            Analyst.objects.create(user=analyst.user, organization=organization)

    def test_analyst_is_employee(self, analyst):
        """
        Test that an Analyst is also an Employee.
        """
        assert isinstance(analyst, Employee)


@pytest.mark.django_db
class TestAgent:
    def test_agent_creation(self, agent, organization, user):
        """
        Test that an Agent instance is created with the correct attributes.
        """
        assert agent.organization == organization
        assert agent.user == user
        assert agent.manager is None

    def test_agent_manager_assignment(self, agent, manager, organization):
        """
        Test that an Agent can be assigned a manager from the same organization.
        """
        agent.manager = manager
        agent.save()
        assert agent.manager == manager

    def test_agent_inherits_metasummary_model(self, agent):
        """
        Test that Agents have the functionalities inherited from MetaSummaryAbstractModel.
        """
        assert hasattr(agent, 'get_or_create_summary')
        assert hasattr(agent, 'is_deviation_significant')

    def test_agent_inherits_conversation_stats_model(self, agent):
        """
        Test that Agents have the functionalities inherited from ConversationStatsAbstractModel.
        """
        assert hasattr(agent, 'update_conversation_stats')

    def test_agent_inherits_conversation_trends(self, agent):
        """
        Test that Agents have the functionalities inherited from ConversationTrendMixin.
        """
        assert hasattr(agent, 'get_conversation_trend')
        assert hasattr(agent, 'get_conversation_trend_per_topic')
        assert hasattr(agent, 'get_avg_for_periods')


@pytest.mark.django_db
class TestCustomer:
    def test_customer_creation(self, customer, organization):
        """
        Test that a Customer instance is created with the correct attributes.
        """
        assert customer.name == "Test Customer"
        assert customer.organization == organization

    def test_customer_str(self, customer):
        """
        Test that the string representation of a Customer is its name.
        """
        assert str(customer) == "Test Customer"

    def test_customer_unique_together(self, customer, organization):
        """
        Test that creating a Customer with a duplicate name in the same organization raises an IntegrityError.
        """
        with pytest.raises(IntegrityError):
            Customer.objects.create(name="Test Customer", organization=organization)

    def test_customer_inherits_metasummary_model(self, customer):
        """
        Test that Customers have the functionalities inherited from MetaSummaryAbstractModel.
        """
        assert hasattr(customer, 'get_or_create_summary')
        assert hasattr(customer, 'is_deviation_significant')

    def test_customer_inherits_conversation_stats_model(self, customer):
        """
        Test that Customers have the functionalities inherited from ConversationStatsAbstractModel.
        """
        assert hasattr(customer, 'update_conversation_stats')

    def test_customer_inherits_conversation_trends(self, customer):
        """
        Test that Customers have the functionalities inherited from ConversationTrendMixin.
        """
        assert hasattr(customer, 'get_conversation_trend')
        assert hasattr(customer, 'get_conversation_trend_per_topic')
        assert hasattr(customer, 'get_avg_for_periods')


@pytest.mark.django_db
class TestConversation:
    def test_conversation_creation(self, conversation, agent, customer, topic):
        """
        Test that a Conversation instance is created with the correct attributes.
        """
        assert conversation.path == "path/to/conversation"
        assert conversation.agent == agent
        assert conversation.customer == customer
        assert topic in conversation.topics.all()
        assert conversation.input_tokens == 100
        assert conversation.output_tokens == 50

    def test_conversation_str(self, conversation):
        """
        Test that the string representation of a Conversation is its path.
        """
        assert str(conversation) == "path/to/conversation"

    def test_conversation_organization_consistency(self, agent, topic):
        """
        Test that a Conversation cannot be created with a customer from a different organization than the agent.
        """
        other_org = Organization.objects.create(name="Other Organization")
        other_customer = Customer.objects.create(name="Other Customer", organization=other_org)

        with pytest.raises(ValueError):
            Conversation.objects.create(
                path="Invalid Call",
                date=datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC),
                duration=60,
                transcript="Invalid transcript",
                sentiment=1.5,
                summary="Valid Summary",
                title="Invalid Title",
                customer=other_customer,
                agent=agent,
                input_tokens=10,
                output_tokens=20
            )

    def test_conversation_topic_organization_consistency(self, conversation, another_organization):
        """
        Test that a Topic from a different organization cannot be added to a Conversation.
        """
        external_topic = Topic.objects.create(name="External Topic", description="Desc",
                                              organization=another_organization)
        with pytest.raises(ValueError):
            conversation.topics.add(external_topic)

    def test_process_transcript(self, conversation):
        """
        Test that the process_transcript method correctly processes a valid transcript.
        """
        conversation.transcript = "<agent>: Hello, how can I help you today? <customer>: I need help with my order."
        processed_messages = conversation.process_transcript()

        expected_processed_messages = [
            {'id': 0, 'message': 'Hello, how can I help you today?', 'class': 'agent-message'},
            {'id': 1, 'message': 'I need help with my order.', 'class': 'customer-message'}
        ]

        assert processed_messages == expected_processed_messages

    def test_process_transcript_invalid_format(self, conversation):
        """
        Test that the process_transcript method handles an invalid transcript format correctly.
        """
        conversation.transcript = "This is an invalid format message."
        processed_messages = conversation.process_transcript()

        assert processed_messages == []

    def test_process_transcript_partial_labels(self, conversation):
        """
        Test that the process_transcript method correctly handles a transcript with only one speaker label.
        """
        conversation.transcript = "<agent>: Hello, how can I assist you? No customer response here."
        processed_messages = conversation.process_transcript()

        expected_processed_messages = [
            {'id': 0, 'message': 'Hello, how can I assist you? No customer response here.', 'class': 'agent-message'}
        ]

        assert processed_messages == expected_processed_messages

    def test_validate_topics_organization(self, conversation, another_organization):
        """
        Test that validate_topics_organization signal prevents adding topics from a different organization.
        """
        topic_other_org = Topic.objects.create(name="Other Topic", description="Desc",
                                               organization=another_organization)
        with pytest.raises(ValueError):
            conversation.topics.add(topic_other_org)