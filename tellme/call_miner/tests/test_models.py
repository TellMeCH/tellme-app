import pytest
import pytz
import zoneinfo
from datetime import timedelta, datetime
from unittest.mock import patch
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType
from tellme.call_miner.models import (
    Organization,
    Topic,
    Customer,
    Conversation,
    Employee,
    Analyst,
    Agent,
    PeriodSummary
)
from tellme.call_miner.utils.period_utils import period_bounds


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
    utc = zoneinfo.ZoneInfo("UTC")
    conv_date = (
            datetime.now(tz=utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            - timedelta(days=15)
    )
    weekday = conv_date.weekday()
    if weekday > 2:
        another_date = conv_date - timedelta(days=2)
    else:
        another_date = conv_date + timedelta(days=2)
    another_conv = Conversation.objects.create(
        path="Another Test Call",
        date=another_date,
        duration=45,
        transcript="<agent>: How can I help you? <customer>: I have an issue.",
        sentiment=0.6,
        starting_sentiment=1.0,
        ending_sentiment=2.0,
        summary="Another Summary",
        title='Another Test Title',
        customer=customer,
        agent=agent,
        input_tokens=5,
        output_tokens=15,
        revenue_at_stake=399.95
    )
    another_conv.topics.add(another_topic_same_organization)
    return another_conv


@pytest.mark.django_db
class TestMetaSummaryAbstractModel:
    """Test the async-aware MetaSummaryAbstractModel behavior."""

    def test_get_or_create_summary_returns_existing_summary(self, topic, conversation_today):
        """
        Test that get_or_create_summary returns existing PeriodSummary when one exists.
        """
        # Create existing PeriodSummary
        start, end, label = period_bounds('month', False)
        content_type = ContentType.objects.get_for_model(topic.__class__)
        existing_summary = {
            'Reasons for Calling': 'Existing billing issues',
            'Churn Potential': 'Low risk'
        }

        PeriodSummary.objects.create(
            content_type=content_type,
            object_id=topic.id,
            period_type='month',
            period_label=label,
            summary=existing_summary,
            last_call_at=conversation_today.date,
            call_count=1
        )

        # Call get_or_create_summary
        summary, date, count, period_label, status = topic.get_or_create_summary('month', False)

        # Verify existing summary is returned
        assert summary == existing_summary
        assert date == conversation_today.date
        assert count == 1
        assert period_label == label
        assert status == 'ready'

    def test_get_or_create_summary_creates_task_when_no_summary(self, topic, conversation_today):
        """
        Test that get_or_create_summary triggers async task creation when no PeriodSummary exists.
        """
        # Ensure no existing PeriodSummary exists
        assert not PeriodSummary.objects.filter(
            content_type=ContentType.objects.get_for_model(topic.__class__),
            object_id=topic.id
        ).exists()

        # Mock the instance method
        with patch.object(topic, 'check_and_create_summarization_task') as mock_task_creation:
            # Call get_or_create_summary
            summary, date, count, period_label, status = topic.get_or_create_summary('month', False)

            # Verify task was triggered and placeholder returned
            assert status == 'generating'
            assert summary == {}  # placeholder summary
            assert count == 1  # conversation count
            assert date == conversation_today.date  # latest conversation date

            # Verify async task creation was called with updated signature
            mock_task_creation.assert_called_once_with(
                period='month',
                rolling=False
            )

        # Verify PeriodSummary was created with placeholder data
        period_summary = PeriodSummary.objects.get(
            content_type=ContentType.objects.get_for_model(topic.__class__),
            object_id=topic.id,
            period_type='month'
        )
        assert period_summary.summary == {}
        assert period_summary.call_count == 1

    def test_get_or_create_summary_no_conversations(self, topic):
        """
        Test that get_or_create_summary returns None data when there are no conversations.
        """
        # Ensure no conversations exist
        assert topic.conversations.count() == 0

        # Call get_or_create_summary
        summary, date, count, period_label, status = topic.get_or_create_summary('month', False)

        # Verify None data is returned
        assert summary is None
        assert date is None
        assert count == 0
        assert period_label is not None  # Label should still be generated
        assert status == 'no conversations found'
        # No status since we exit early

    def test_different_object_types_use_correct_mapping(self, customer, agent, conversation_today):
        """
        Test that different object types (Customer, Agent) use correct object type mapping
        when triggering summarization tasks.
        """
        # Link conversations to test objects
        conversation_today.customer = customer
        conversation_today.agent = agent
        conversation_today.save()

        # Test Customer
        with patch.object(customer, 'check_and_create_summarization_task') as mock_customer:
            customer.get_or_create_summary('quarter', True)
            mock_customer.assert_called_with(period='quarter', rolling=True)

        # Test Agent
        with patch.object(agent, 'check_and_create_summarization_task') as mock_agent:
            agent.get_or_create_summary('month', False)
            mock_agent.assert_called_with(period='month', rolling=False)

    @patch('tellme.call_miner.models.create_summarization_task')
    def test_does_not_create_task_when_summary_exists(self, mock_create_task, topic, conversation_today):
        """Test that no task is created when a summary already exists."""
        # Link conversation to topic for period calculations
        conversation_today.topics.add(topic)

        # Create an existing PeriodSummary for the current period
        from tellme.call_miner.utils.period_utils import period_bounds
        start, end, label = period_bounds('month', True)

        content_type = ContentType.objects.get_for_model(topic)
        PeriodSummary.objects.create(
            content_type=content_type,
            object_id=topic.id,
            period_type='month',
            period_label=label,
            summary={'test': 'summary'},
            last_call_at=conversation_today.date,
            call_count=1
        )

        # Call the function
        result = topic.check_and_create_summarization_task(
            period='month', rolling=True
        )

        # Verify no task was created (should return None when refresh not needed)
        assert result is None
        mock_create_task.assert_not_called()

    @patch('tellme.call_miner.models.create_summarization_task')
    def test_creates_task_for_different_parameters(self, mock_create_task, topic, conversation_today):
        """Test that tasks are created for different period/rolling combinations."""
        # Link conversation to topic
        conversation_today.topics.add(topic)

        # Create an existing PeriodSummary for month/rolling=True
        from tellme.call_miner.utils.period_utils import period_bounds
        start, end, label = period_bounds('month', True)

        content_type = ContentType.objects.get_for_model(topic)
        PeriodSummary.objects.create(
            content_type=content_type,
            object_id=topic.id,
            period_type='month',
            period_label=label,
            summary={'test': 'summary'},
            last_call_at=conversation_today.date,
            call_count=1
        )

        mock_create_task.return_value = "different-task-id"

        # Call with different rolling parameter - should create task
        result = topic.check_and_create_summarization_task(
            period='month', rolling=False
        )

        # Verify task was created for the different parameters
        assert result == "different-task-id"
        mock_create_task.assert_called_once_with(
            object_id=topic.id,
            object_type='topic',
            summary_period='month',
            summary_rolling_period=False
        )

    @patch('tellme.call_miner.models.create_summarization_task')
    def test_handles_exceptions_gracefully(self, mock_create_task, topic, conversation_today):
        """Test that exceptions are handled gracefully and don't break the flow."""
        # Link conversation to topic
        conversation_today.topics.add(topic)

        # Mock create_summarization_task to raise an exception
        mock_create_task.side_effect = Exception("Task creation failed")

        # Call the function - should not raise exception
        result = topic.check_and_create_summarization_task(
            period='month', rolling=True
        )

        # Should return None when exception occurs
        assert result is None


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
            topic.get_trend('invalid_period')

    def test_get_conversation_trend_empty(self, topic):
        """
        Test that get_trend returns an empty list when there are no conversations.
        """
        trend = list(topic.get_trend('daily'))
        assert len(trend) == 0

    def test_get_conversation_trend_single_conversation(self, topic, conversation):
        """
        Test that get_trend returns the correct trend for a single conversation.
        """
        trend = list(topic.get_trend('daily'))
        assert len(trend) == 1
        assert trend[0]['count'] == 1

    def test_get_conversation_trend_multiple_conversations(self, topic, conversation,
                                                           another_conversation_same_organization):
        """
        Test that get_trend returns the correct trend for multiple conversations on different dates.
        """
        another_conversation_same_organization.topics.add(topic)
        trend = list(topic.get_trend('daily'))
        assert len(trend) == 2

    def test_get_conversation_trend_per_topic_invalid_period(self, topic):
        """
        Tests the required input format for get_trend.
        """
        with pytest.raises(ValueError):
            topic.get_trend('invalid_period', per_topic=True)

    def test_get_conversation_trend_per_topic_empty(self, customer):
        """
        Test that get_trend per topic returns an empty list when there are no conversations.
        """
        trend = list(customer.get_trend('daily', per_topic=True))
        assert len(trend) == 0

    def test_get_conversation_trend_per_topic_single_conversation(self, customer, conversation, topic):
        """
        Test that get_trend per topic returns the correct trend for a single conversation.
        """
        trend = list(customer.get_trend('daily', per_topic=True))
        assert len(trend) == 1
        assert trend[0]['count'] == 1
        assert trend[0]['topic_name'] == topic.name

    def test_get_conversation_trend_per_topic_multiple_conversations(self, customer, conversation,
                                                                     another_conversation_same_organization,
                                                                     another_topic_same_organization):
        """
        Test that get_trend per topic returns the correct trend for multiple conversations with different
        topics.
        """
        another_conversation_same_organization.topics.add(another_topic_same_organization)
        trend = list(customer.get_trend('daily', per_topic=True))
        assert len(trend) == 2

    def test_get_avg_for_periods_invalid_field(self, topic):
        """
        Tests the required input format for get_trend with an invalid field.
        """
        with pytest.raises(ValueError):
            topic.get_trend(field='invalid_field', period='daily')

    def test_get_avg_for_periods_invalid_period(self, topic):
        """
        Tests the required input format for get_trend with an invalid period.
        """
        with pytest.raises(ValueError):
            topic.get_trend(field='duration', period='invalid_period')

    def test_get_avg_duration_empty(self, topic):
        """
        Test that get_trend for duration returns empty results when there are no conversations.
        """
        avg_duration = list(topic.get_trend(field='duration', period='daily'))
        assert len(avg_duration) == 0

    def test_get_avg_duration_single_conversation(self, topic, conversation):
        """
        Test that get_trend for duration returns the correct average duration for a single conversation.
        """
        avg_duration = list(topic.get_trend(field='duration', period='daily'))
        assert len(avg_duration) == 1
        assert avg_duration[0]['avg_duration'] == conversation.duration

    def test_get_daily_avg_duration_multiple_conversations(self, topic, conversation,
                                                           another_conversation_same_organization):
        """
        Test that get_trend for duration returns the correct average daily duration for multiple conversations over
        different days.
        """
        another_conversation_same_organization.topics.add(topic)
        avg_duration = list(topic.get_trend(field='duration', period='daily'))
        assert len(avg_duration) == 2

    def test_get_weekly_avg_duration_multiple_conversations(self, topic, conversation,
                                                            another_conversation_same_organization):
        """
        Test that get_trend for duration returns the correct average weekly duration for multiple conversations over
        different days.
        """
        another_conversation_same_organization.topics.add(topic)
        avg_duration = list(topic.get_trend(field='duration', period='weekly'))
        assert len(avg_duration) == 1

    def test_get_monthly_avg_duration_multiple_conversations(self, topic, conversation,
                                                             another_conversation_same_organization):
        """
        Test that get_trend for duration returns the correct average monthly duration for multiple conversations over
        different days.
        """
        another_conversation_same_organization.topics.add(topic)
        avg_duration = list(topic.get_trend(field='duration', period='monthly'))
        assert len(avg_duration) == 1

    def test_get_avg_sentiment_empty(self, topic):
        """
        Test that get_trend for sentiment returns empty results when there are no conversations.
        """
        avg_sentiment = list(topic.get_trend(field='sentiment', period='daily'))
        assert len(avg_sentiment) == 0

    def test_get_avg_sentiment_single_conversation(self, topic, conversation):
        """
        Test that get_trend for sentiment returns the correct average sentiment for a single conversation.
        """
        avg_sentiment = list(topic.get_trend(field='sentiment', period='daily'))
        assert len(avg_sentiment) == 1
        assert avg_sentiment[0]['avg_sentiment'] == conversation.sentiment

    def test_get_daily_avg_sentiment_multiple_conversations(self, topic, conversation,
                                                            another_conversation_same_organization):
        """
        Test that get_trend for sentiment returns the correct daily average sentiment for multiple conversations over
        different days.
        """
        another_conversation_same_organization.topics.add(topic)
        avg_sentiment = list(topic.get_trend(field='sentiment', period='daily'))
        assert len(avg_sentiment) == 2

    def test_get_weekly_avg_sentiment_multiple_conversations(self, topic, conversation,
                                                             another_conversation_same_organization):
        """
        Test that get_trend for sentiment returns the correct weekly average sentiment for multiple conversations over
        different days.
        """
        another_conversation_same_organization.topics.add(topic)
        avg_sentiment = list(topic.get_trend(field='sentiment', period='weekly'))
        assert len(avg_sentiment) == 1

    def test_get_monthly_avg_sentiment_multiple_conversations(self, topic, conversation,
                                                              another_conversation_same_organization):
        """
        Test that get_trend for sentiment returns the correct monthly average sentiment for multiple conversations over
        different days.
        """
        another_conversation_same_organization.topics.add(topic)
        avg_sentiment = list(topic.get_trend(field='sentiment', period='monthly'))
        assert len(avg_sentiment) == 1

    def test_get_total_revenue_empty(self, topic):
        """
        Test that get_trend for revenue returns empty results when there are no conversations.
        """
        total_revenue = list(topic.get_trend(field='revenue', period='daily'))
        assert len(total_revenue) == 0

    def test_get_total_revenue_single_conversation(self, topic, conversation):
        """
        Test that get_trend for revenue returns the correct total revenue for a single conversation.
        """
        total_revenue = list(topic.get_trend(field='revenue', period='daily'))
        assert len(total_revenue) == 1
        assert total_revenue[0]['total_revenue'] == conversation.revenue_at_stake

    def test_get_daily_total_revenue_multiple_conversations(self, topic, conversation,
                                                         another_conversation_same_organization):
        """
        Test that get_trend for revenue returns the correct total daily revenue for multiple conversations over
        different days.
        """
        another_conversation_same_organization.topics.add(topic)
        total_revenue = list(topic.get_trend(field='revenue', period='daily'))
        assert len(total_revenue) == 2

    def test_get_weekly_total_revenue_multiple_conversations(self, topic, conversation,
                                                          another_conversation_same_organization):
        """
        Test that get_trend for revenue returns the correct total weekly revenue for multiple conversations over
        different days.
        """
        another_conversation_same_organization.topics.add(topic)
        total_revenue = list(topic.get_trend(field='revenue', period='weekly'))
        assert len(total_revenue) == 1

    def test_get_monthly_total_revenue_multiple_conversations(self, topic, conversation,
                                                           another_conversation_same_organization):
        """
        Test that get_trend for revenue returns the correct total monthly revenue for multiple conversations over
        different days.
        """
        another_conversation_same_organization.topics.add(topic)
        total_revenue = list(topic.get_trend(field='revenue', period='monthly'))
        assert len(total_revenue) == 1


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
        assert hasattr(organization, 'get_trend')


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
        assert hasattr(topic, 'check_and_create_summarization_task')

    def test_topic_inherits_conversation_stats_model(self, topic):
        """
        Test that Topics have the functionalities inherited from ConversationStatsAbstractModel.
        """
        assert hasattr(topic, 'update_conversation_stats')

    def test_topic_inherits_conversation_trends(self, topic):
        """
        Test that Topics have the functionalities inherited from ConversationTrendMixin.
        """
        assert hasattr(topic, 'get_trend')


@pytest.mark.django_db
class TestAnalyst:
    def test_analyst_creation(self, analyst, organization, user):
        """
        Test that an Analyst instance is created with the correct attributes.
        """
        assert analyst.organization == organization
        assert analyst.user == user
        assert str(analyst) == f"{user.email} - {organization.name} - Analyst"

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
        assert hasattr(agent, 'check_and_create_summarization_task')

    def test_agent_inherits_conversation_stats_model(self, agent):
        """
        Test that Agents have the functionalities inherited from ConversationStatsAbstractModel.
        """
        assert hasattr(agent, 'update_conversation_stats')

    def test_agent_inherits_conversation_trends(self, agent):
        """
        Test that Agents have the functionalities inherited from ConversationTrendMixin.
        """
        assert hasattr(agent, 'get_trend')


@pytest.mark.django_db
class TestCustomer:
    def test_customer_creation(self, customer, organization):
        """
        Test that a Customer instance is created with the correct attributes.
        """
        assert customer.external_id == "02ac34b094eed76ca56ffc826db3f9a4d7b3d8f337beefc33c342b0035fea0dd"
        assert customer.organization == organization

    def test_customer_str(self, customer, organization):
        """
        Test that the string representation of a Customer is its name.
        """
        assert str(customer) == f"Customer [external_id={customer.external_id} | org={organization.id}]"

    def test_customer_unique_together(self, customer, organization):
        """
        Test that creating a Customer with a duplicate name in the same organization raises an IntegrityError.
        """
        with pytest.raises(IntegrityError):
            Customer.objects.create(
                external_id="02ac34b094eed76ca56ffc826db3f9a4d7b3d8f337beefc33c342b0035fea0dd",
                organization=organization
            )

    def test_customer_inherits_metasummary_model(self, customer):
        """
        Test that Customers have the functionalities inherited from MetaSummaryAbstractModel.
        """
        assert hasattr(customer, 'get_or_create_summary')
        assert hasattr(customer, 'check_and_create_summarization_task')

    def test_customer_inherits_conversation_stats_model(self, customer):
        """
        Test that Customers have the functionalities inherited from ConversationStatsAbstractModel.
        """
        assert hasattr(customer, 'update_conversation_stats')

    def test_customer_inherits_conversation_trends(self, customer):
        """
        Test that Customers have the functionalities inherited from ConversationTrendMixin.
        """
        assert hasattr(customer, 'get_trend')


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
        other_customer = Customer.objects.create(external_id="Other Customer", organization=other_org)

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

    def test_get_avg_starting_sentiment_single_conversation(self, topic, conversation):
        """
        Test that get_trend for starting_sentiment returns the correct average starting sentiment for a single conversation.
        """
        avg_starting_sentiment = list(topic.get_trend(field='starting_sentiment', period='daily'))
        assert len(avg_starting_sentiment) == 1
        assert avg_starting_sentiment[0]['avg_starting_sentiment'] == conversation.starting_sentiment

    def test_get_avg_ending_sentiment_single_conversation(self, topic, conversation):
        """
        Test that get_trend for ending_sentiment returns the correct average ending sentiment for a single conversation.
        """
        avg_ending_sentiment = list(topic.get_trend(field='ending_sentiment', period='daily'))
        assert len(avg_ending_sentiment) == 1
        assert avg_ending_sentiment[0]['avg_ending_sentiment'] == conversation.ending_sentiment

    def test_get_avg_starting_ending_sentiment_multiple_conversations(self, topic, conversation,
                                                                      another_conversation_same_organization):
        """
        Test that get_trend for starting/ending sentiment returns correct averages for multiple conversations.
        """
        another_conversation_same_organization.topics.add(topic)

        # Test starting sentiment average
        avg_starting_sentiment = list(topic.get_trend(field='starting_sentiment', period='weekly'))
        assert len(avg_starting_sentiment) == 1
        expected_starting_avg = (conversation.starting_sentiment + another_conversation_same_organization.starting_sentiment) / 2
        assert avg_starting_sentiment[0]['avg_starting_sentiment'] == expected_starting_avg

        # Test ending sentiment average
        avg_ending_sentiment = list(topic.get_trend(field='ending_sentiment', period='weekly'))
        assert len(avg_ending_sentiment) == 1
        expected_ending_avg = (conversation.ending_sentiment + another_conversation_same_organization.ending_sentiment) / 2
        assert avg_ending_sentiment[0]['avg_ending_sentiment'] == expected_ending_avg


