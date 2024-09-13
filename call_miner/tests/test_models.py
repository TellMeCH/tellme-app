import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from call_miner.models import Organization, Topic, Agent, Customer, Conversation, Manager, MetaSummary
from django.contrib.contenttypes.models import ContentType


class TestCaseMixin:
    def setUp(self):
        """Shared setup method for creating base objects"""
        self.organization = Organization.objects.create(name="Test Organization")
        self.agent = Agent.objects.create(name="Test Agent", organization=self.organization)
        self.customer = Customer.objects.create(name="Test Customer", organization=self.organization)
        self.call = Conversation.objects.create(
            path="Test Call",
            duration=60,
            transcript="Test transcript",
            sentiment=0.5,
            summary="Test Summary",
            customer=self.customer,
            agent=self.agent,
            input_tokens=10,
            output_tokens=20
        )


@pytest.mark.django_db
class TestOrganization:
    def setup_method(self):
        self.organization = Organization.objects.create(name="Test Organization")

    def test_organization_creation(self):
        """Test the adequate creation of organization attributes"""
        assert self.organization.name == "Test Organization"
        assert self.organization.slug == 'test-organization'

    def test_organization_name_uniqueness(self):
        """Test the error raised when two organizations have the same name"""
        with pytest.raises(IntegrityError):
            Organization.objects.create(name="Test Organization")


@pytest.mark.django_db
class TestTopic(TestCaseMixin):
    def setup_method(self):
        self.setUp()
        self.topic = Topic.objects.create(
            name="Test Topic",
            description="Test Description",
            organization=self.organization
        )
        self.call.topics.add(self.topic)

    def test_topic_creation(self):
        """Test the adequate creation of topic attributes"""
        assert self.topic.name == "Test Topic"
        assert self.topic.description == "Test Description"
        assert self.topic.slug == 'topic-test-topic-test-organization'
        assert str(self.topic) == "Test Topic"

    def test_topic_unique_together(self):
        """Test that two topics cannot have the same name in the same organization"""
        with pytest.raises(IntegrityError):
            Topic.objects.create(name="Test Topic", description="Another Description", organization=self.organization)

    def test_topic_meta_summary_creation(self, mocker):
        """Test that the MetaSummary for the topic can be created or retrieved if it has associated calls"""
        # Mock the `condense_summaries` function
        mocker.patch('call_miner.models.condense_summaries', return_value="Mocked Summary")
        summary = self.topic.get_or_create_meta_summary()
        assert summary == "Mocked Summary"


@pytest.mark.django_db
class TestAgent(TestCaseMixin):
    def setup_method(self):
        self.setUp()

    def test_agent_organization_required(self):
        """Test that an organization is required in order to create an agent"""
        agent = Agent(name="Test Agent")
        with pytest.raises(ValidationError):
            agent.full_clean()

    def test_agent_str(self):
        """Test that the name of the agent is used in the str representation of the object"""
        assert str(self.agent) == "Test Agent"

    def test_agent_creation(self):
        """Test that the object is created when an organization is provided"""
        assert self.agent.name == "Test Agent"
        assert self.agent.slug == 'agent-test-agent-test-organization'

    def test_agent_duplicate_slugs(self):
        """Test that the slug of two agents in the same organization with the same name are not the same"""
        agent_2 = Agent.objects.create(name="Test Agent", organization=self.organization)
        assert agent_2.slug == 'agent-test-agent-test-organization-1'

    def test_agent_slugs_with_different_organizations(self):
        """
        Test the agent slugs created when multiple instances with the same name and different organization are created
        """
        org2 = Organization.objects.create(name="Test Organization 1")
        agent_2 = Agent.objects.create(name="Test Agent", organization=org2)
        assert agent_2.slug == 'agent-test-agent-test-organization-1'

        agent_3 = Agent.objects.create(name="Test Agent", organization=self.organization)
        assert agent_3.slug == 'agent-test-agent-test-organization-2'

        agent_4 = Agent.objects.create(name="Test Agent", organization=org2)
        assert agent_4.slug == 'agent-test-agent-test-organization-1-1'

    def test_agent_meta_summary_creation(self, mocker):
        """Test that the MetaSummary for the agent can be created or retrieved if it has associated calls"""
        # Mock the `condense_summaries` function
        mocker.patch('call_miner.models.condense_summaries', return_value="Mocked Summary")
        summary = self.agent.get_or_create_meta_summary()
        assert summary == "Mocked Summary"


@pytest.mark.django_db
class TestCustomer(TestCaseMixin):
    def setup_method(self):
        self.setUp()

    def test_customer_organization_required(self):
        """Test that it is necessary for a customer to have an organization to be created"""
        customer = Customer(name="Test Customer")
        with pytest.raises(ValidationError):
            customer.full_clean()

    def test_customer_creation(self):
        """Test that the object is created when an organization is provided"""
        assert self.customer.name == "Test Customer"
        assert self.customer.slug == 'customer-test-customer-test-organization'

    def test_customer_str(self):
        """Test that the name of the customer is used in the str representation of the object"""
        assert str(self.customer) == "Test Customer"

    def test_customer_duplicate_slugs(self):
        """Test that the slug of two customers in the same organization with the same name are not the same"""
        customer_2 = Customer.objects.create(name="Test Customer", organization=self.organization)
        assert customer_2.slug == 'customer-test-customer-test-organization-1'

    def test_customer_slugs_with_different_organizations(self):
        """
        Test the customer slugs created when multiple instances with the same name and different organization are created
        """
        org2 = Organization.objects.create(name="Test Organization 2")
        customer_2 = Customer.objects.create(name="Test Customer", organization=org2)
        assert customer_2.slug == 'customer-test-customer-test-organization-2'

    def test_customer_meta_summary_creation(self, mocker):
        """Test that the MetaSummary for the customer can be created or retrieved if it has associated calls"""
        # Mock the `condense_summaries` function
        mocker.patch('call_miner.models.condense_summaries', return_value="Mocked Summary")
        summary = self.customer.get_or_create_meta_summary()
        assert summary == "Mocked Summary"


@pytest.mark.django_db
class TestManager:
    def setup_method(self):
        self.organization = Organization.objects.create(name="Test Organization")
        self.manager = Manager.objects.create(name="Test Manager", organization=self.organization)

    def test_manager_creation(self):
        """Test that the object is created when an organization is provided"""
        assert self.manager.name == "Test Manager"
        assert str(self.manager) == "Test Manager"


@pytest.mark.django_db
class TestConversation(TestCaseMixin):
    def setup_method(self):
        self.setUp()
        self.topic = Topic.objects.create(name="Test Topic", description="Test Description",
                                          organization=self.organization)
        self.call.topics.add(self.topic)

    def test_call_creation(self):
        """Test that the object is created when an organization is provided"""
        assert self.call.path == "Test Call"
        assert self.topic in self.call.topics.all()

    def test_call_validation(self):
        """Test that the object is created when an organization is provided"""
        call = Conversation(path="Invalid Call", duration=60, transcript="Invalid transcript", sentiment=0.5,
                            summary="Valid Summary", customer=self.customer, agent=self.agent, input_tokens=10,
                            output_tokens=20)
        call.full_clean()

    def test_call_str(self):
        """Test that the name of the call is used in the str representation"""
        assert str(self.call) == "Test Call"

    def test_call_customer_required(self):
        """Test that the call requires a customer to be defined"""
        call = Conversation(path="Invalid Call", duration=60, transcript="Invalid transcript", sentiment=0.5,
                            summary="Valid Summary", input_tokens=10, output_tokens=20, agent=self.agent)
        with pytest.raises(ValidationError):
            call.full_clean()

    def test_call_agent_required(self):
        """Test that the call requires an agent to be defined"""
        call = Conversation(path="Invalid Call", duration=60, transcript="Invalid transcript", sentiment=0.5,
                            summary="Valid Summary", input_tokens=10, output_tokens=20, customer=self.customer)
        with pytest.raises(ValidationError):
            call.full_clean()

    def test_process_transcript(self):
        """Test that the process_transcript method correctly processes the transcript"""
        transcript = "<agent>: Hello, how can I help you today? <customer>: I need help with my order."
        call = Conversation(
            path="Test Call", duration=60, transcript=transcript, sentiment=0.5,
            summary="Valid Summary", customer=self.customer, agent=self.agent, input_tokens=10, output_tokens=20
        )
        call.process_transcript()

        expected_processed_messages = [
            {'message': 'Hello, how can I help you today?', 'class': 'agent-message'},
            {'message': 'I need help with my order.', 'class': 'customer-message'}
        ]

        assert call.processed_messages == expected_processed_messages

    def test_call_save_process_transcript(self):
        """Test that the transcript is processed and saved with processed_messages when save is called"""
        transcript = "<agent>: Hello. <customer>: Hi, I need help."
        call = Conversation(
            path="Test Call", duration=60, transcript=transcript, sentiment=0.5,
            summary="Valid Summary", customer=self.customer, agent=self.agent, input_tokens=10, output_tokens=20
        )
        call.save()

        assert call.processed_messages == [
            {'message': 'Hello.', 'class': 'agent-message'},
            {'message': 'Hi, I need help.', 'class': 'customer-message'}
        ]

    def test_process_transcript_invalid_format(self):
        """Test how process_transcript handles transcripts with no Agent or Customer labels"""
        transcript = "This is an invalid format message."
        call = Conversation(
            path="Test Call", duration=60, transcript=transcript, sentiment=0.5,
            summary="Valid Summary", customer=self.customer, agent=self.agent, input_tokens=10, output_tokens=20
        )
        call.process_transcript()

        assert call.processed_messages == []  # Ensure it handles the case with no Agent/Customer properly

    def test_process_transcript_partial_labels(self):
        """Test processing when there is only one speaker label"""
        transcript = "<agent>: Hello, how can I assist you? No customer response here."
        call = Conversation(
            path="Test Call", duration=60, transcript=transcript, sentiment=0.5,
            summary="Valid Summary", customer=self.customer, agent=self.agent, input_tokens=10, output_tokens=20
        )
        call.process_transcript()

        expected_processed_messages = [
            {'message': 'Hello, how can I assist you? No customer response here.', 'class': 'agent-message'}
        ]

        assert call.processed_messages == expected_processed_messages


@pytest.mark.django_db
class TestMetaSummary(TestCaseMixin):
    def setup_method(self):
        self.setUp()

    def test_meta_summary_creation_for_agent(self):
        """Test that a MetaSummary can be created and associated with an agent"""
        content_type = ContentType.objects.get_for_model(Agent)
        meta_summary = MetaSummary.objects.create(content_type=content_type, object_id=self.agent.id)
        assert isinstance(meta_summary, MetaSummary)

    def test_meta_summary_get_summary(self, mocker):
        """Test that MetaSummary's get_summary method works when calls are associated"""
        mocker.patch('call_miner.models.condense_summaries', return_value="Mocked Summary")
        summary_text = self.agent.get_or_create_meta_summary()
        assert summary_text == "Mocked Summary"
