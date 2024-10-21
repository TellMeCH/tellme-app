import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from call_miner.models import Organization, Analyst, Agent, Customer, Conversation, Topic
from datetime import datetime

TREND_ACTIONS = ['conversations', 'conversation-trend', 'conversation-topic-trend', 'duration-trend',
                 'sentiment-trend', 'summary-data']


@pytest.fixture
def client():
    """Return an instance of the DRF APIClient for testing."""
    return APIClient()


@pytest.fixture
def organization():
    """Create and return a test Organization."""
    return Organization.objects.create(name='Test Organization', max_user_count=10)


@pytest.fixture
def another_organization():
    """Create and return another test Organization."""
    return Organization.objects.create(name='Another Organization', max_user_count=10)


@pytest.fixture
def superuser():
    """Create and return a superuser for testing."""
    user = User.objects.create_superuser('superuser', 'superuser@example.com', 'superpassword')
    return user


@pytest.fixture
def organization_admin_user(organization):
    """Create and return an organization admin user associated with the given organization."""
    user = User.objects.create_user('orgadmin', 'orgadmin@example.com', 'password')
    Analyst.objects.create(user=user, organization=organization, role='ANALYST', is_organization_admin=True)
    return user


@pytest.fixture
def organization_analyst_user(organization):
    """Create and return an analyst user associated with the given organization."""
    user = User.objects.create_user('analyst', 'analyst@example.com', 'password')
    Analyst.objects.create(user=user, organization=organization, role='ANALYST', is_organization_admin=False)
    return user


@pytest.fixture
def another_organization_analyst_user(another_organization):
    """Create and return an analyst user associated with another organization."""
    user = User.objects.create_user('another_analyst', 'another_analyst@example.com', 'password')
    Analyst.objects.create(user=user, organization=another_organization, role='ANALYST', is_organization_admin=False)
    return user


@pytest.fixture
def agent(organization):
    """Create and return an agent associated with the given organization."""
    user = User.objects.create_user('agent', 'agent@example.com', 'password')
    agent = Agent.objects.create(user=user, organization=organization, role='AGENT')
    return agent


@pytest.fixture
def another_agent(another_organization):
    """Create and return an agent associated with another organization."""
    user = User.objects.create_user('another_agent', 'another_agent@example.com', 'password')
    agent = Agent.objects.create(user=user, organization=another_organization, role='AGENT')
    return agent


@pytest.fixture
def customer(organization):
    """Create and return a customer associated with the given organization."""
    return Customer.objects.create(name='Test Customer', organization=organization)


@pytest.fixture
def another_customer(another_organization):
    """Create and return a customer associated with another organization."""
    return Customer.objects.create(name='Another Customer', organization=another_organization)


@pytest.fixture
def topic(organization):
    """Create and return a topic associated with the given organization."""
    return Topic.objects.create(
        name='Test Topic',
        description='A test topic',
        organization=organization,
        is_active=True
    )


@pytest.fixture
def another_topic(another_organization):
    """Create and return another topic associated with another organization."""
    return Topic.objects.create(
        name='Another Topic',
        description='Another test topic',
        organization=another_organization,
        is_active=True
    )


@pytest.fixture
def conversation(agent, customer, topic):
    """Create and return a conversation between the given agent and customer."""
    conv = Conversation.objects.create(
        path='path/to/conversation',
        date=datetime.now(),
        duration=123.45,
        title='Test Conversation',
        summary='Test summary',
        transcript='Test transcript',
        sentiment=0.5,
        agent=agent,
        customer=customer,
        input_tokens=100,
        output_tokens=50
    )
    conv.topics.add(topic)
    return conv


@pytest.fixture
def another_conversation(another_agent, another_customer, another_topic):
    """Create and return another conversation between the given agent and customer."""
    conv = Conversation.objects.create(
        path='path/to/another_conversation',
        date=datetime.now(),
        duration=123.45,
        title='Another Conversation',
        summary='Another summary',
        transcript='Another test transcript',
        sentiment=0.5,
        agent=another_agent,
        customer=another_customer,
        input_tokens=100,
        output_tokens=50
    )
    conv.topics.add(another_topic)
    return conv


@pytest.mark.django_db
class TestCustomerList:
    """Test the customer-list API endpoint."""

    def test_customer_list_as_superuser(self, client, superuser, customer, another_customer):
        """Test that a superuser can list all customers across organizations."""
        client.force_authenticate(user=superuser)
        url = reverse('customer-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_customer_list_as_analyst_in_org(self, client, organization_analyst_user, customer, another_customer):
        """
        Test that an analyst within the organization can list customers in their organization.
        """
        client.force_authenticate(user=organization_analyst_user)
        url = reverse('customer-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == customer.name

    def test_customer_list_as_analyst_outside_org(self, client, another_organization_analyst_user, customer,
                                                  another_customer):
        """
        Test that an analyst outside the organization sees only their own organization's customers.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('customer-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == another_customer.name

    def test_customer_list_as_agent_in_org(self, client, agent, customer):
        """Test that an agent within the organization can list customers in their organization."""
        client.force_authenticate(user=agent.user)
        url = reverse('customer-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == customer.name

    def test_customer_list_as_agent_outside_org(self, client, another_agent, another_customer):
        """Test that an agent outside the organization sees only their own organization's customers."""
        client.force_authenticate(user=another_agent.user)
        url = reverse('customer-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == another_customer.name

    def test_customer_list_as_unauthenticated_user(self, client):
        """Test that an unauthenticated user cannot list customers."""
        url = reverse('customer-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCustomerRetrieve:
    """Test the customer-detail API endpoint for viewing a Customer's details."""

    def test_customer_retrieve_as_superuser(self, client, superuser, customer):
        """Test that a superuser can retrieve any customer."""
        client.force_authenticate(user=superuser)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == customer.name

    def test_customer_retrieve_as_analyst_in_org(self, client, organization_analyst_user, customer):
        """Test that an analyst within the organization can retrieve a customer."""
        client.force_authenticate(user=organization_analyst_user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == customer.name

    def test_customer_retrieve_as_analyst_outside_org(self, client, another_organization_analyst_user, customer):
        """Test that an analyst outside the organization cannot retrieve customers from another organization."""
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_customer_retrieve_as_agent_in_org(self, client, agent, customer):
        """Test that an agent within the organization can retrieve a customer."""
        client.force_authenticate(user=agent.user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == customer.name

    def test_customer_retrieve_as_agent_outside_org(self, client, another_agent, customer):
        """Test that an agent outside the organization cannot retrieve customers from another organization."""
        client.force_authenticate(user=another_agent.user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_customer_retrieve_as_unauthenticated_user(self, client, customer):
        """Test that an unauthenticated user cannot retrieve a customer."""
        url = reverse('customer-detail', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCustomerCreate:
    """Test the creation of a new Customer instance"""

    def test_customer_create_as_superuser(self, client, superuser, organization):
        """Test that a superuser can create a new customer."""
        client.force_authenticate(user=superuser)
        url = reverse('customer-list')
        data = {'name': 'New Customer', 'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Customer.objects.filter(name='New Customer').exists()

    def test_customer_create_as_analyst_in_org(self, client, organization_analyst_user, organization):
        """Test that an analyst within the organization cannot create a new customer."""
        client.force_authenticate(user=organization_analyst_user)
        url = reverse('customer-list')
        data = {'name': 'New Customer', 'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_create_as_analyst_outside_org(self, client, another_organization_analyst_user, organization):
        """Test that an analyst outside the organization cannot create a customer in another organization."""
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('customer-list')
        data = {'name': 'New Customer', 'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_create_as_agent_in_org(self, client, agent, organization):
        """Test that an agent within the organization cannot create a new customer."""
        client.force_authenticate(user=agent.user)
        url = reverse('customer-list')
        data = {'name': 'New Customer', 'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_create_as_agent_outside_org(self, client, another_agent, organization):
        """Test that an agent outside the organization cannot create a customer in another organization."""
        client.force_authenticate(user=another_agent.user)
        url = reverse('customer-list')
        data = {'name': 'New Customer', 'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_create_as_unauthenticated_user(self, client, organization):
        """Test that an unauthenticated user cannot create a customer."""
        url = reverse('customer-list')
        data = {'name': 'New Customer', 'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCustomerUpdate:
    """Tests for the update of existing Customer instances."""

    def test_customer_update_as_superuser(self, client, superuser, customer):
        """Test that a superuser can update a customer."""
        client.force_authenticate(user=superuser)
        url = reverse('customer-detail', args=[customer.pk])
        data = {'name': 'Updated Customer Name'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert Customer.objects.filter(name='Updated Customer Name').exists()

    def test_customer_update_as_analyst_in_org(self, client, organization_analyst_user, customer):
        """Test that an analyst within the organization cannot update a customer."""
        client.force_authenticate(user=organization_analyst_user)
        url = reverse('customer-detail', args=[customer.pk])
        data = {'name': 'Updated Customer Name'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_update_as_analyst_outside_org(self, client, another_organization_analyst_user, customer):
        """Test that an analyst outside the organization cannot update a customer."""
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('customer-detail', args=[customer.pk])
        data = {'name': 'Updated Customer Name'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_update_as_agent_in_org(self, client, agent, customer):
        """Test that an agent within the organization cannot update a customer."""
        client.force_authenticate(user=agent.user)
        url = reverse('customer-detail', args=[customer.pk])
        data = {'name': 'Updated Customer Name'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_update_as_agent_outside_org(self, client, another_agent, customer):
        """Test that an agent outside the organization cannot update a customer."""
        client.force_authenticate(user=another_agent.user)
        url = reverse('customer-detail', args=[customer.pk])
        data = {'name': 'Updated Customer Name'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_update_as_unauthenticated_user(self, client, customer):
        """Test that an unauthenticated user cannot update a customer."""
        url = reverse('customer-detail', args=[customer.pk])
        data = {'name': 'Updated Customer Name'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCustomerDelete:
    """Tests for the deletion of existing Customer instances"""

    def test_customer_delete_as_superuser(self, client, superuser, customer):
        """Test that a superuser can delete a customer."""
        client.force_authenticate(user=superuser)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_customer_delete_as_analyst_in_org(self, client, organization_analyst_user, customer):
        """Test that an analyst within the organization cannot delete a customer."""
        client.force_authenticate(user=organization_analyst_user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_delete_as_analyst_outside_org(self, client, another_organization_analyst_user, customer):
        """Test that an analyst outside the organization cannot delete a customer."""
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_delete_as_agent_in_org(self, client, agent, customer):
        """Test that an agent within the organization cannot delete a customer."""
        client.force_authenticate(user=agent.user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_delete_as_agent_outside_org(self, client, another_agent, customer):
        """Test that an agent outside the organization cannot delete a customer."""
        client.force_authenticate(user=another_agent.user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_delete_as_unauthenticated_user(self, client, customer):
        """Test that an unauthenticated user cannot delete a customer."""
        url = reverse('customer-detail', args=[customer.pk])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCustomerActions:
    """Test the ViewSet actions for viewing a Customer's activity trends and conversation summary"""

    def test_customer_trend_actions_as_superuser(self, client, superuser, customer):
        """Test that a superuser can access trend actions for a customer."""
        client.force_authenticate(user=superuser)
        for action in TREND_ACTIONS:
            url = reverse(f'customer-{action}', args=[customer.pk])
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK

    def test_customer_trend_actions_as_analyst_in_org(self, client, organization_analyst_user, customer):
        """Test that an analyst within the organization can access trend actions for a customer."""
        client.force_authenticate(user=organization_analyst_user)
        for action in TREND_ACTIONS:
            url = reverse(f'customer-{action}', args=[customer.pk])
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK

    def test_customer_trend_actions_as_analyst_outside_org(self, client, another_organization_analyst_user, customer):
        """Test that an analyst outside the organization cannot access trend actions for a customer."""
        client.force_authenticate(user=another_organization_analyst_user)
        for action in TREND_ACTIONS:
            url = reverse(f'customer-{action}', args=[customer.pk])
            response = client.get(url)
            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_customer_trend_actions_as_agent_in_org(self, client, agent, customer):
        """Test that an agent within the organization can access trend actions for a customer."""
        client.force_authenticate(user=agent.user)
        for action in TREND_ACTIONS:
            url = reverse(f'customer-{action}', args=[customer.pk])
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK

    def test_customer_trend_actions_as_agent_outside_org(self, client, another_agent, customer):
        """Test that an agent outside the organization cannot access trend actions for a customer."""
        client.force_authenticate(user=another_agent.user)
        for action in TREND_ACTIONS:
            url = reverse(f'customer-{action}', args=[customer.pk])
            response = client.get(url)
            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_customer_trend_actions_as_unauthenticated_user(self, client, customer):
        """Test that an unauthenticated user cannot access trend actions for a customer."""
        for action in TREND_ACTIONS:
            url = reverse(f'customer-{action}', args=[customer.pk])
            response = client.get(url)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_conversations_action_returns_expected_content(self, client, agent, customer, conversation):
        """
        Test that the 'conversations' action for a customer retrieves the expected conversation data.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('customer-conversations', args=[customer.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'conversations' in response.data
        results = response.data['conversations']['results']
        assert len(results) == 1
        assert results[0]['title'] == conversation.title

    def test_customer_conversation_trend_action_returns_expected_content(self, client, agent, customer, conversation):
        """
        Test that the 'conversation_trend' action for an agent retrieves the expected conversation data.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('customer-conversation-trend', args=[customer.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'conversation_trend' in response.data
        results = response.data['conversation_trend']['results']
        assert len(results) == 1
        assert results[0]['count'] == 1
        assert results[0]['date'].date() == conversation.date.date()

    def test_customer_conversation_topic_trend_action_returns_expected_content(self, client, agent, customer,
                                                                               conversation):
        """
        Test that the 'conversation_topic_trend' action for a customer retrieves the expected conversation data.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('customer-conversation-topic-trend', args=[customer.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'conversation_topic_trend' in response.data
        results = response.data['conversation_topic_trend']['results']
        assert len(results) == 1
        assert results[0]['count'] == 1
        assert results[0]['date'].date() == conversation.date.date()
        assert results[0]['topic'] == str(conversation.topics.all()[0])

    def test_customer_duration_trend_action_returns_expected_content(self, client, agent, customer, conversation):
        """
        Test that the 'duration-trend' action for a customer retrieves the expected duration trend data.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('customer-duration-trend', args=[customer.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'duration_trend' in response.data
        results = response.data['duration_trend']['results']
        assert len(results) == 1
        assert results[0]['avg_value'] == conversation.duration

    def test_customer_sentiment_trend_action_returns_expected_content(self, client, agent, customer, conversation):
        """
        Test that the 'sentiment-trend' action for a customer retrieves the expected sentiment trend data.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('customer-sentiment-trend', args=[customer.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'sentiment_trend' in response.data
        results = response.data['sentiment_trend']['results']
        assert len(results) == 1
        assert results[0]['avg_value'] == conversation.sentiment

    def test_customer_summary_data_returns_expected_content(self, client, agent, customer):
        """
        Test that the 'summary-data' action for a customer retrieves the expected summary data.
        """
        with patch('call_miner.models.condense_summaries') as mock_condense_summaries:
            mock_condense_summaries.return_value = 'Mocked summary text'
            client.force_authenticate(user=agent.user)
            url = reverse('customer-summary-data', args=[customer.id])
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert 'summary_data' in response.data
            summary_data = response.data['summary_data']
            assert summary_data['summary'] == 'Mocked summary text'
