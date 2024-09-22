import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth.models import User
from call_miner.models import Organization, Topic, Customer, Conversation, Employee, Analyst, Agent
from django.utils import timezone


@pytest.fixture
def organization():
    return Organization.objects.create(name="Test Organization")


@pytest.fixture
def user(organization):
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def employee(organization, user):
    return Employee.objects.create(organization=organization, user=user)


@pytest.fixture
def analyst(organization, user):
    return Analyst.objects.create(organization=organization, user=user)


@pytest.fixture
def agent(user, organization):
    return Agent.objects.create(user=user, organization=organization)


@pytest.fixture
def customer(organization):
    return Customer.objects.create(name="Test Customer", organization=organization)


@pytest.fixture
def topic(organization):
    return Topic.objects.create(name="Test Topic", description="Test Description", organization=organization)


@pytest.fixture
def conversation(agent, customer, topic):
    conv = Conversation.objects.create(
        path="Test Call",
        date=timezone.now(),
        duration=60,
        transcript="Test transcript",
        sentiment=0.5,
        summary="Test Summary",
        title='Test Title',
        customer=customer,
        agent=agent,
        input_tokens=10,
        output_tokens=20
    )
    conv.topics.add(topic)
    return conv


@pytest.mark.django_db
class TestOrganization:
    def test_organization_creation(self, organization):
        """
        Test that an Organization instance is created with the correct name.
        """
        assert organization.name == "Test Organization"

    def test_organization_name_uniqueness(self, organization):
        """
        Test that creating an Organization with a duplicate name raises an IntegrityError.
        """
        with pytest.raises(IntegrityError):
            Organization.objects.create(name="Test Organization")

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


@pytest.mark.django_db
class TestTopic:
    def test_topic_creation(self, topic, organization):
        """
        Test that a Topic instance is created with the correct attributes.
        """
        assert topic.name == "Test Topic"
        assert topic.description == "Test Description"
        assert topic.organization == organization
        assert str(topic) == "Test Topic"

    def test_topic_unique_together(self, topic, organization):
        """
        Test that creating a Topic with a duplicate name in the same organization raises an IntegrityError.
        """
        with pytest.raises(IntegrityError):
            Topic.objects.create(name="Test Topic", description="Another Description", organization=organization)

    def test_topic_meta_summary_creation(self, topic, conversation, mocker):
        """
        Test that get_or_create_summary method creates a summary for the Topic.
        """
        mocker.patch('call_miner.models.condense_summaries', return_value="Mocked Summary")
        topic.get_or_create_summary()
        assert topic.summary == "Mocked Summary"
        assert topic.summary_call_count == 1
        assert topic.summary_date == conversation.date

    def test_topic_get_conversation_trend(self, topic, conversation):
        """
        Test that get_conversation_trend method returns the correct trend data for the Topic.
        """
        trend = topic.get_conversation_trend()
        assert len(trend) == 1
        assert trend[0]['count'] == 1

    def test_topic_is_deviation_significant(self, topic):
        """
        Test the is_deviation_significant method for various scenarios.
        """
        topic.summary_call_count = 100
        topic.save()
        assert topic.is_deviation_significant(111)
        assert topic.is_deviation_significant(89)
        assert not topic.is_deviation_significant(110)
        assert not topic.is_deviation_significant(90)
        assert not topic.is_deviation_significant(100)
        topic.summary_call_count = 0
        topic.save()
        assert topic.is_deviation_significant(1)
        assert topic.is_deviation_significant(0)


@pytest.mark.django_db
class TestEmployee:
    def test_employee_creation(self, employee, organization, user):
        """
        Test that an Employee instance is created with the correct attributes.
        """
        assert employee.organization == organization
        assert employee.user == user
        assert str(employee) == user.username

    def test_employee_unique_together(self, employee, organization):
        """
        Test that creating an Employee with a duplicate user in the same organization raises an IntegrityError.
        """
        with pytest.raises(IntegrityError):
            new_user = User.objects.create_user(username="testuser", password="newpass")
            Employee.objects.create(user=new_user, organization=organization)


@pytest.mark.django_db
class TestAnalyst:
    def test_analyst_creation(self, analyst, organization, user):
        """
        Test that an Analyst instance is created with the correct attributes.
        """
        assert analyst.organization == organization
        assert analyst.user == user
        assert str(analyst) == user.username

    def test_analyst_unique_together(self, analyst, organization):
        """
        Test that creating an Employee with a duplicate user in the same organization raises an IntegrityError.
        """
        with pytest.raises(IntegrityError):
            new_user = User.objects.create_user(username="testuser", password="newpass")
            Analyst.objects.create(user=new_user, organization=organization)


@pytest.mark.django_db
class TestAgent:
    def test_agent_creation(self, agent, organization, user):
        """
        Test that an Agent instance is created with the correct attributes.
        """
        assert agent.organization == organization
        assert agent.user == user
        assert agent.manager is None

    def test_agent_manager_assignment(self, agent, organization):
        """
        Test that an Agent can be assigned a manager from the same organization.
        """
        manager = Agent.objects.create(
            user=User.objects.create_user(username="manager", password="managerpass"),
            organization=organization
        )
        agent.manager = manager
        agent.save()
        assert agent.manager == manager

    def test_agent_self_manager_assignment(self, agent):
        """
        Test that an Agent cannot be assigned as their own manager.
        """
        with pytest.raises(ValidationError):
            agent.manager = agent
            agent.save()

    def test_agent_different_organization_manager(self, agent):
        """
        Test that an Agent cannot be assigned a manager from a different organization.
        """
        other_org = Organization.objects.create(name="Other Organization")
        other_manager = Agent.objects.create(
            user=User.objects.create_user(username="other_manager", password="otherpass"),
            organization=other_org
        )
        with pytest.raises(ValueError):
            agent.manager = other_manager
            agent.save()

    def test_agent_meta_summary_creation(self, agent, conversation, mocker):
        """
        Test that get_or_create_summary method creates a summary for the Agent.
        """
        mocker.patch('call_miner.models.condense_summaries', return_value="Mocked Summary")
        agent.get_or_create_summary()
        assert agent.summary == "Mocked Summary"
        assert agent.summary_call_count == 1
        assert agent.summary_date == conversation.date

    def test_agent_get_conversation_trend(self, agent, conversation):
        """
        Test that get_conversation_trend method returns the correct trend data for the Agent.
        """
        trend = agent.get_conversation_trend()
        assert len(trend) == 1
        assert trend[0]['count'] == 1

    def test_agent_is_deviation_significant(self, agent):
        """
        Test the is_deviation_significant method for various scenarios.
        """
        agent.summary_call_count = 100
        agent.save()
        assert agent.is_deviation_significant(111)
        assert agent.is_deviation_significant(89)
        assert not agent.is_deviation_significant(110)
        assert not agent.is_deviation_significant(90)
        assert not agent.is_deviation_significant(100)
        agent.summary_call_count = 0
        agent.save()
        assert agent.is_deviation_significant(1)
        assert agent.is_deviation_significant(0)


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

    def test_customer_meta_summary_creation(self, customer, conversation, mocker):
        """
        Test that get_or_create_summary method creates a summary for the Customer.
        """
        mocker.patch('call_miner.models.condense_summaries', return_value="Mocked Summary")
        customer.get_or_create_summary()
        assert customer.summary == "Mocked Summary"
        assert customer.summary_call_count == 1
        assert customer.summary_date == conversation.date

    def test_customer_get_conversation_trend(self, customer, conversation):
        """
        Test that get_conversation_trend method returns the correct trend data for the Customer.
        """
        trend = customer.get_conversation_trend()
        assert len(trend) == 1
        assert trend[0]['count'] == 1

    def test_customer_is_deviation_significant(self, customer):
        """
        Test the is_deviation_significant method for various scenarios.
        """
        customer.summary_call_count = 100
        customer.save()
        assert customer.is_deviation_significant(111)
        assert customer.is_deviation_significant(89)
        assert not customer.is_deviation_significant(110)
        assert not customer.is_deviation_significant(90)
        assert not customer.is_deviation_significant(100)
        customer.summary_call_count = 0
        customer.save()
        assert customer.is_deviation_significant(1)
        assert customer.is_deviation_significant(0)


@pytest.mark.django_db
class TestConversation:
    def test_conversation_creation(self, conversation, agent, customer, topic):
        """
        Test that a Conversation instance is created with the correct attributes.
        """
        assert conversation.path == "Test Call"
        assert conversation.agent == agent
        assert conversation.customer == customer
        assert topic in conversation.topics.all()
        assert conversation.input_tokens == 10
        assert conversation.output_tokens == 20

    def test_conversation_str(self, conversation):
        """
        Test that the string representation of a Conversation is its path.
        """
        assert str(conversation) == "Test Call"

    def test_conversation_organization_consistency(self, agent, topic):
        """
        Test that a Conversation cannot be created with a customer from a different organization than the agent.
        """
        other_org = Organization.objects.create(name="Other Organization")
        other_customer = Customer.objects.create(name="Other Customer", organization=other_org)

        with pytest.raises(ValueError):
            Conversation.objects.create(
                path="Invalid Call", duration=60, transcript="Invalid transcript", sentiment=0.5,
                summary="Valid Summary", customer=other_customer, agent=agent, input_tokens=10, output_tokens=20
            )

    def test_conversation_topic_organization_consistency(self, conversation, organization):
        """
        Test that a Topic from a different organization cannot be added to a Conversation.
        """
        other_org = Organization.objects.create(name="Other Organization")
        other_topic = Topic.objects.create(name="Other Topic", description="Other Description", organization=other_org)

        with pytest.raises(ValueError):
            conversation.topics.add(other_topic)

    def test_process_transcript(self):
        """
        Test that the process_transcript method correctly processes a valid transcript.
        """
        transcript = "<agent>: Hello, how can I help you today? <customer>: I need help with my order."
        conversation = Conversation(
            path="Test Call", duration=60, transcript=transcript, sentiment=0.5,
            summary="Valid Summary", customer=Customer(), agent=Agent(), input_tokens=10, output_tokens=20
        )
        processed_messages = conversation.process_transcript()

        expected_processed_messages = [
            {'message': 'Hello, how can I help you today?', 'class': 'agent-message'},
            {'message': 'I need help with my order.', 'class': 'customer-message'}
        ]

        assert processed_messages == expected_processed_messages

    def test_process_transcript_invalid_format(self):
        """
        Test that the process_transcript method handles an invalid transcript format correctly.
        """
        transcript = "This is an invalid format message."
        conversation = Conversation(
            path="Test Call", duration=60, transcript=transcript, sentiment=0.5,
            summary="Valid Summary", customer=Customer(), agent=Agent(), input_tokens=10, output_tokens=20
        )
        processed_messages = conversation.process_transcript()

        assert processed_messages == []

    def test_process_transcript_partial_labels(self):
        """
        Test that the process_transcript method correctly handles a transcript with only one speaker label.
        """
        transcript = "<agent>: Hello, how can I assist you? No customer response here."
        conversation = Conversation(
            path="Test Call", duration=60, transcript=transcript, sentiment=0.5,
            summary="Valid Summary", customer=Customer(), agent=Agent(), input_tokens=10, output_tokens=20
        )
        processed_messages = conversation.process_transcript()

        expected_processed_messages = [
            {'message': 'Hello, how can I assist you? No customer response here.', 'class': 'agent-message'}
        ]

        assert processed_messages == expected_processed_messages


@pytest.mark.django_db
class TestConversationTrendMixin:

    def test_conversations_scope_organization(self, organization, agent, customer, conversation):
        """
        Test that the conversations_scope method retrieves all conversations for an organization.
        """
        assert conversation in organization.conversations_scope

    def test_conversations_scope_agent_manager(self, organization, user, agent, customer, conversation):
        """
        Test that the conversations_scope method retrieves all conversations for a manager and their team.
        """
        manager = Agent.objects.create(
            user=User.objects.create_user(username="manager", password="managerpass"),
            organization=organization
        )
        agent.manager = manager
        agent.save()
        assert conversation in manager.conversations_scope
        assert conversation in agent.conversations_scope

    def test_conversations_scope_agent_non_manager(self, agent, customer, conversation):
        """
        Test that the conversations_scope method retrieves only the agent's own conversations if they are not a manager.
        """
        assert conversation in agent.conversations_scope

    def test_conversations_scope_direct_relationship(self, customer, conversation):
        """
        Test that the conversations_scope method retrieves the conversations directly related to a customer.
        """
        assert conversation in customer.conversations_scope

    def test_get_conversation_trend_empty(self, topic):
        """
        Test that get_conversation_trend returns an empty list when there are no conversations.
        """
        trend = topic.get_conversation_trend()
        assert trend == []

    def test_get_conversation_trend_single_conversation(self, topic, conversation):
        """
        Test that get_conversation_trend returns the correct trend for a single conversation.
        """
        trend = topic.get_conversation_trend()
        assert len(trend) == 1
        assert trend[0]['count'] == 1

    def test_get_conversation_trend_multiple_conversations(self, topic, conversation):
        """
        Test that get_conversation_trend returns the correct trend for multiple conversations on different dates.
        """
        another_conversation = Conversation.objects.create(
            path="Another Test Call",
            date=timezone.now() - timezone.timedelta(days=1),
            duration=45,
            transcript="Another test transcript",
            sentiment=0.6,
            summary="Another Summary",
            title='Another Test Title',
            customer=conversation.customer,
            agent=conversation.agent,
            input_tokens=5,
            output_tokens=15
        )
        another_conversation.topics.add(topic)
        another_conversation.save()
        trend = topic.get_conversation_trend()
        assert len(trend) == 2

    def test_get_conversation_trend_per_topic_empty(self, topic):
        """
        Test that get_conversation_trend_per_topic returns an empty list when there are no conversations.
        """
        trend = topic.get_conversation_trend_per_topic()
        assert trend == []

    def test_get_conversation_trend_per_topic_single_conversation(self, topic, conversation):
        """
        Test that get_conversation_trend_per_topic returns the correct trend for a single conversation.
        """
        trend = topic.get_conversation_trend_per_topic()
        assert len(trend) == 1
        assert trend[0]['count'] == 1
        assert trend[0]['topics__name'] == topic.name

    def test_get_conversation_trend_per_topic_multiple_conversations(self, topic, conversation):
        """
        Test that get_conversation_trend_per_topic returns the correct trend for multiple conversations with different topics.
        """
        another_topic = Topic.objects.create(
            name="Another Topic",
            description="Another Description",
            organization=topic.organization
        )
        another_conversation = Conversation.objects.create(
            path="Another Test Call",
            date=timezone.now() - timezone.timedelta(days=1),
            duration=45,
            transcript="Another test transcript",
            sentiment=0.6,
            summary="Another Summary",
            title='Another Test Title',
            customer=conversation.customer,
            agent=conversation.agent,
            input_tokens=5,
            output_tokens=15
        )
        another_conversation.topics.add(another_topic)

        trend = topic.get_conversation_trend_per_topic()
        assert len(trend) == 1

    def test_get_avg_duration_empty(self, topic):
        """
        Test that get_avg_duration returns empty results when there are no conversations.
        """
        avg_duration = topic.get_avg_duration()
        assert all(len(period) == 0 for period in avg_duration.values())

    def test_get_avg_duration_single_conversation(self, topic, conversation):
        """
        Test that get_avg_duration returns the correct average duration for a single conversation.
        """
        avg_duration = topic.get_avg_duration()
        assert len(avg_duration['daily']) == 1
        assert avg_duration['daily'][0]['avg_value'] == conversation.duration

    def test_get_avg_duration_multiple_conversations(self, topic, conversation):
        """
        Test that get_avg_duration returns the correct average duration for multiple conversations over different days.
        """
        another_conversation = Conversation.objects.create(
            path="Another Test Call",
            date=timezone.now() - timezone.timedelta(days=1),
            duration=45,
            transcript="Another test transcript",
            sentiment=0.6,
            summary="Another Summary",
            title='Another Test Title',
            customer=conversation.customer,
            agent=conversation.agent,
            input_tokens=5,
            output_tokens=15
        )
        another_conversation.topics.add(topic)
        another_conversation.save()
        avg_duration = topic.get_avg_duration()
        assert len(avg_duration['daily']) == 2

    def test_get_avg_sentiment_empty(self, topic):
        """
        Test that get_avg_sentiment returns empty results when there are no conversations.
        """
        avg_sentiment = topic.get_avg_sentiment()
        assert all(len(period) == 0 for period in avg_sentiment.values())

    def test_get_avg_sentiment_single_conversation(self, topic, conversation):
        """
        Test that get_avg_sentiment returns the correct average sentiment for a single conversation.
        """
        avg_sentiment = topic.get_avg_sentiment()
        assert len(avg_sentiment['daily']) == 1
        assert avg_sentiment['daily'][0]['avg_value'] == conversation.sentiment

    def test_get_avg_sentiment_multiple_conversations(self, topic, conversation):
        """
        Test that get_avg_sentiment returns the correct average sentiment for multiple conversations over different days.
        """
        another_conversation = Conversation.objects.create(
            path="Another Test Call",
            date=timezone.now() - timezone.timedelta(days=1),
            duration=45,
            transcript="Another test transcript",
            sentiment=0.6,
            summary="Another Summary",
            title='Another Test Title',
            customer=conversation.customer,
            agent=conversation.agent,
            input_tokens=5,
            output_tokens=15
        )
        another_conversation.topics.add(topic)
        another_conversation.save()
        avg_sentiment = topic.get_avg_sentiment()
        assert len(avg_sentiment['daily']) == 2
