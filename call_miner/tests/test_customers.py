import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from call_miner.models import Organization, Analyst, Agent, Customer, Conversation, Topic
from datetime import datetime

TREND_ACTIONS = ['conversations', 'conversation-trend', 'conversation-topic-trend', 'duration-trend', 'sentiment-trend']


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
def test_customer_list_as_superuser(client, superuser, customer, another_customer):
    client.force_authenticate(user=superuser)
    url = reverse('customer-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2


@pytest.mark.django_db
def test_customer_list_as_analyst_in_org(client, organization_analyst_user, customer, another_customer):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('customer-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == customer.name


@pytest.mark.django_db
def test_customer_list_as_analyst_outside_org(client, another_organization_analyst_user, customer, another_customer):
    client.force_authenticate(user=another_organization_analyst_user)
    url = reverse('customer-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == another_customer.name


@pytest.mark.django_db
def test_customer_list_as_agent_in_org(client, agent):
    client.force_authenticate(user=agent.user)
    url = reverse('customer-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_customer_list_as_agent_outside_org(client, another_agent):
    client.force_authenticate(user=another_agent.user)
    url = reverse('customer-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_customer_list_as_unauthenticated_user(client):
    url = reverse('customer-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_retrieve_as_superuser(client, superuser, customer):
    client.force_authenticate(user=superuser)
    url = reverse('customer-detail', args=[customer.pk])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_customer_retrieve_as_analyst_in_org(client, organization_analyst_user, customer):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('customer-detail', args=[customer.pk])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_customer_retrieve_as_analyst_outside_org(client, another_organization_analyst_user, customer):
    client.force_authenticate(user=another_organization_analyst_user)
    url = reverse('customer-detail', args=[customer.pk])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_customer_retrieve_as_agent_in_org(client, agent, customer):
    client.force_authenticate(user=agent.user)
    url = reverse('customer-detail', args=[customer.pk])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_customer_retrieve_as_agent_outside_org(client, another_agent, customer):
    client.force_authenticate(user=another_agent.user)
    url = reverse('customer-detail', args=[customer.pk])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_customer_retrieve_as_unauthenticated_user(client, customer):
    url = reverse('customer-detail', args=[customer.pk])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_create_as_superuser(client, superuser, organization):
    client.force_authenticate(user=superuser)
    url = reverse('customer-list')
    data = {'name': 'New Customer', 'organization': organization.pk}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_customer_create_as_analyst_in_org(client, organization_analyst_user, organization):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('customer-list')
    data = {'name': 'New Customer', 'organization': organization.pk}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_create_as_analyst_outside_org(client, another_organization_analyst_user, organization):
    client.force_authenticate(user=another_organization_analyst_user)
    url = reverse('customer-list')
    data = {'name': 'New Customer', 'organization': organization.pk}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_create_as_agent_in_org(client, agent, organization):
    client.force_authenticate(user=agent.user)
    url = reverse('customer-list')
    data = {'name': 'New Customer', 'organization': organization.pk}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_create_as_agent_outside_org(client, another_agent, organization):
    client.force_authenticate(user=another_agent.user)
    url = reverse('customer-list')
    data = {'name': 'New Customer', 'organization': organization.pk}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_create_as_unauthenticated_user(client, organization):
    url = reverse('customer-list')
    data = {'name': 'New Customer', 'organization': organization.pk}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_update_as_superuser(client, superuser, customer):
    client.force_authenticate(user=superuser)
    url = reverse('customer-detail', args=[customer.pk])
    data = {'name': 'Updated Customer Name'}
    response = client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_customer_update_as_analyst_in_org(client, organization_analyst_user, customer):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('customer-detail', args=[customer.pk])
    data = {'name': 'Updated Customer Name'}
    response = client.patch(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_update_as_analyst_outside_org(client, another_organization_analyst_user, customer):
    client.force_authenticate(user=another_organization_analyst_user)
    url = reverse('customer-detail', args=[customer.pk])
    data = {'name': 'Updated Customer Name'}
    response = client.patch(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_update_as_agent_in_org(client, agent, customer):
    client.force_authenticate(user=agent.user)
    url = reverse('customer-detail', args=[customer.pk])
    data = {'name': 'Updated Customer Name'}
    response = client.patch(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_update_as_agent_outside_org(client, another_agent, customer):
    client.force_authenticate(user=another_agent.user)
    url = reverse('customer-detail', args=[customer.pk])
    data = {'name': 'Updated Customer Name'}
    response = client.patch(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_update_as_unauthenticated_user(client, customer):
    url = reverse('customer-detail', args=[customer.pk])
    data = {'name': 'Updated Customer Name'}
    response = client.patch(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_delete_as_superuser(client, superuser, customer):
    client.force_authenticate(user=superuser)
    url = reverse('customer-detail', args=[customer.pk])
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_customer_delete_as_analyst_in_org(client, organization_analyst_user, customer):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('customer-detail', args=[customer.pk])
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_delete_as_analyst_outside_org(client, another_organization_analyst_user, customer):
    client.force_authenticate(user=another_organization_analyst_user)
    url = reverse('customer-detail', args=[customer.pk])
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_delete_as_agent_in_org(client, agent, customer):
    client.force_authenticate(user=agent.user)
    url = reverse('customer-detail', args=[customer.pk])
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_delete_as_agent_outside_org(client, another_agent, customer):
    client.force_authenticate(user=another_agent.user)
    url = reverse('customer-detail', args=[customer.pk])
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_delete_as_unauthenticated_user(client, customer):
    url = reverse('customer-detail', args=[customer.pk])
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_customer_trend_actions_as_superuser(client, superuser, customer):
    client.force_authenticate(user=superuser)
    for action in TREND_ACTIONS:
        url = reverse(f'customer-{action}', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_customer_trend_actions_as_analyst_in_org(client, organization_analyst_user, customer):
    client.force_authenticate(user=organization_analyst_user)
    for action in TREND_ACTIONS:
        url = reverse(f'customer-{action}', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_customer_trend_actions_as_analyst_outside_org(client, another_organization_analyst_user, customer):
    client.force_authenticate(user=another_organization_analyst_user)
    for action in TREND_ACTIONS:
        url = reverse(f'customer-{action}', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_customer_trend_actions_as_agent_in_org(client, agent, customer):
    client.force_authenticate(user=agent.user)
    for action in TREND_ACTIONS:
        url = reverse(f'customer-{action}', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_customer_trend_actions_as_agent_outside_org(client, another_agent, customer):
    client.force_authenticate(user=another_agent.user)
    for action in TREND_ACTIONS:
        url = reverse(f'customer-{action}', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_customer_trend_actions_as_unauthenticated_user(client, customer):
    for action in TREND_ACTIONS:
        url = reverse(f'customer-{action}', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
