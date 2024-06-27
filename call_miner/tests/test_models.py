from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from call_miner.models import Organization, Topic, Agent, Customer, Call


class TestOrganization(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Test Organization")

    def test_organization_creation(self):
        """Test the adequate creation of organization attributes"""
        self.assertEqual(self.organization.name, "Test Organization")
        self.assertEqual(self.organization.slug, "test-organization")

    def test_organization_name_uniqueness(self):
        """Test the error raised when two organizations have the same name"""
        with self.assertRaises(IntegrityError):
            Organization.objects.create(name="Test Organization")


class TestTopic(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Test Organization")
        self.topic = Topic.objects.create(name="Test Topic", description="Test Description",
                                          organization=self.organization)

    def test_topic_creation(self):
        """Test the adequate creation of topic attributes"""
        self.assertEqual(self.topic.name, "Test Topic")
        self.assertEqual(self.topic.description, "Test Description")
        self.assertEqual(str(self.topic), "Test Topic")

    def test_topic_unique_together(self):
        """Test that two topics cannot have the same name in the same organization"""
        with self.assertRaises(IntegrityError):
            Topic.objects.create(name="Test Topic", description="Another Description", organization=self.organization)


# Test all the basic functionalities of the Agent model
class TestAgent(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Test Organization")
        self.agent = Agent.objects.create(name="Test Agent", organization=self.organization)

    def test_agent_organization_required(self):
        """Test that an organization is required in order to create an agent"""
        agent = Agent(name="Test Agent")
        with self.assertRaises(ValidationError):
            agent.full_clean()

    def test_agent_str(self):
        """Test that the name of the agent is used in the str representation of the object"""
        self.assertEqual(str(self.agent), "Test Agent")

    def test_agent_creation(self):
        """Test that the object is created when an organization is provided"""
        self.assertEqual(self.agent.name, "Test Agent")
        self.assertEqual(self.agent.slug, "test-agent-test-organization")

    def test_agent_duplicate_slugs(self):
        """Test that the slug of two agents in the same organization with the same name are not the same"""
        agent_2 = Agent.objects.create(name="Test Agent", organization=self.organization)
        self.assertEqual(agent_2.slug, "test-agent-test-organization-1")

    def test_agent_slugs_with_different_organizations(self):
        """
        Test the agent slugs created when multiple instances with the same name and different organization are created
        """
        org2 = Organization.objects.create(name="Test Organization 2")
        agent_2 = Agent.objects.create(name="Test Agent", organization=org2)
        self.assertEqual(agent_2.slug, "test-agent-test-organization-2")


class TestCustomer(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Test Organization")
        self.customer = Customer.objects.create(name="Test Customer", organization=self.organization)

    def test_customer_organization_required(self):
        """Test that it is necessary for a customer to have an organization to be created"""
        customer = Customer(name="Test Customer")
        with self.assertRaises(ValidationError):
            customer.full_clean()

    def test_customer_creation(self):
        """Test that the object is created when an organization is provided"""
        self.assertEqual(self.customer.name, "Test Customer")
        self.assertEqual(self.customer.slug, "test-customer-test-organization")

    def test_customer_str(self):
        """Test that the name of the customer is used in the str representation of the object"""
        self.assertEqual(str(self.customer), "Test Customer")

    def test_customer_duplicate_slugs(self):
        """Test that the slug of two customers in the same organization with the same name are not the same"""
        customer_2 = Customer.objects.create(name="Test Customer", organization=self.organization)
        self.assertEqual(customer_2.slug, "test-customer-test-organization-1")

    def test_customer_slugs_with_different_organizations(self):
        """
        Test the customer slugs created when multiple instances with the same name and different organization are
        created
        """
        org2 = Organization.objects.create(name="Test Organization 2")
        customer_2 = Customer.objects.create(name="Test Customer", organization=org2)
        self.assertEqual(customer_2.slug, "test-customer-test-organization-2")


class TestCall(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Test Organization")
        self.agent = Agent.objects.create(name="Test Agent", organization=self.organization)
        self.customer = Customer.objects.create(name="Test Customer", organization=self.organization)
        self.topic = Topic.objects.create(name="Test Topic", description="Test Description",
                                          organization=self.organization)
        self.call = Call.objects.create(path="Test Call", duration=60, transcript="Test transcript",
                                        sentiment=0.5, customer=self.customer, agent=self.agent)
        self.call.topics.add(self.topic)

    def test_call_creation(self):
        """Test that the object is created when an organization is provided"""
        self.assertEqual(self.call.path, "Test Call")
        self.assertIn(self.topic, self.call.topics.all())

    def test_call_validation(self):
        """Test that the object is created when an organization is provided"""
        call = Call(path="Invalid Call", duration=60, transcript="Invalid transcript", sentiment=0.5,
                    customer=self.customer, agent=self.agent)
        call.full_clean()

    def test_call_str(self):
        """Test that the name of the call is used in the str representation"""
        self.assertEqual(str(self.call), "Test Call")

    def test_call_customer_required(self):
        """Test that the call requires a customer to be defined"""
        call = Call(path="Invalid Call", duration=60, transcript="Invalid transcript", sentiment=0.5,
                    agent=self.agent)
        with self.assertRaises(ValidationError):
            call.full_clean()

    def test_call_agent_required(self):
        """Test that the call requires an agent to be defined"""
        call = Call(path="Invalid Call", duration=60, transcript="Invalid transcript", sentiment=0.5,
                    customer=self.customer)
        with self.assertRaises(ValidationError):
            call.full_clean()
