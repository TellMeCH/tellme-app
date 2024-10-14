import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from call_miner.models import Organization, Analyst, Agent, Customer, Conversation
from datetime import datetime

TREND_ACTIONS = ['conversation-trend', 'conversation-topic-trend', 'duration-trend', 'sentiment-trend']


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
    """Create and return an employee user associated with the given organization."""
    user = User.objects.create_user('employee', 'employee@example.com', 'password')
    Analyst.objects.create(user=user, organization=organization, role='ANALYST', is_organization_admin=False)
    return user


@pytest.fixture
def another_organization_analyst_user(another_organization):
    """Create and return an employee user associated with another organization."""
    user = User.objects.create_user('another_employee', 'another_employee@example.com', 'password')
    Analyst.objects.create(user=user, organization=another_organization, role='ANALYST', is_organization_admin=False)
    return user


@pytest.fixture
def agent(organization):
    """Create and return an agent associated with the given organization."""
    user = User.objects.create_user('agent', 'agent@example.com', 'password')
    agent = Agent.objects.create(user=user, organization=organization, role='AGENT')
    return agent


@pytest.fixture
def customer(organization):
    """Create and return a customer associated with the given organization."""
    return Customer.objects.create(name='Test Customer', organization=organization)


@pytest.fixture
def conversation(agent, customer):
    """Create and return a conversation between the given agent and customer."""
    return Conversation.objects.create(
        path='path/to/conversation',
        date=datetime.now(),
        duration=123.45,
        title='Test title',
        summary='Test summary',
        transcript=f"""
        <agent>: Hello, {agent.user.username}, how can I assist you today?
        <customer>: Hi, I have an issue with my product. It's acting weird.
        <agent>: Could you describe the problem?
        <customer>: Yes, it keeps making a strange noise and flashing red lights.
        <agent>: That doesn't sound right. Let me look into that for you.
        <customer>: Thank you, it's driving me crazy!
        """ * 4,
        sentiment=0.5,
        agent=agent,
        customer=customer,
        input_tokens=100,
        output_tokens=50
    )


@pytest.fixture
def another_agent(another_organization):
    """Create and return an agent associated with another organization."""
    user = User.objects.create_user('another_agent', 'another_agent@example.com', 'password')
    agent = Agent.objects.create(user=user, organization=another_organization, role='AGENT')
    return agent


@pytest.fixture
def another_customer(another_organization):
    """Create and return a customer associated with another organization."""
    return Customer.objects.create(name='Another Customer', organization=another_organization)


@pytest.fixture
def another_conversation(another_agent, another_customer):
    """Create and return another conversation between the given agent and customer."""
    return Conversation.objects.create(
        path='path/to/another_conversation',
        date=datetime.now(),
        duration=123.45,
        transcript='Another test transcript',
        title='Another Conversation',
        summary='Another summary',
        sentiment=0.5,
        agent=another_agent,
        customer=another_customer,
        input_tokens=100,
        output_tokens=50
    )


@pytest.mark.django_db
def test_superuser_can_retrieve_any_organization(client, superuser, organization, another_organization):
    client.force_authenticate(user=superuser)
    # Retrieve organization
    url = reverse('organization-detail', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    # Retrieve another organization
    url = reverse('organization-detail', args=[another_organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_analyst_can_retrieve_own_organization(client, organization_analyst_user, organization):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-detail', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'Test Organization'


@pytest.mark.django_db
def test_analyst_cannot_retrieve_other_organization(client, organization_analyst_user, another_organization):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-detail', args=[another_organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_agent_cannot_retrieve_own_organization(client, agent, organization):
    client.force_authenticate(user=agent.user)
    url = reverse('organization-detail', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_agent_cannot_retrieve_other_organization(client, agent, another_organization):
    client.force_authenticate(user=agent.user)
    url = reverse('organization-detail', args=[another_organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_unauthenticated_user_cannot_retrieve_organization(client, organization):
    url = reverse('organization-detail', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_superuser_can_create_organization(client, superuser):
    client.force_authenticate(user=superuser)
    url = reverse('organization-list')
    data = {'name': 'New Organization', 'max_user_count': 20}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Organization.objects.filter(name='New Organization').exists()


@pytest.mark.django_db
def test_analyst_cannot_create_organization(client, organization_analyst_user):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-list')
    data = {'name': 'Unauthorized Organization', 'max_user_count': 20}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Organization.objects.filter(name='Unauthorized Organization').exists()


@pytest.mark.django_db
def test_agent_cannot_create_organization(client, agent):
    client.force_authenticate(user=agent.user)
    url = reverse('organization-list')
    data = {'name': 'Unauthorized Organization', 'max_user_count': 20}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Organization.objects.filter(name='Unauthorized Organization').exists()


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_organization(client):
    url = reverse('organization-list')
    data = {'name': 'Unauthorized Organization', 'max_user_count': 20}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Organization.objects.filter(name='Unauthorized Organization').exists()


@pytest.mark.django_db
def test_superuser_can_update_organization(client, superuser, organization):
    client.force_authenticate(user=superuser)
    url = reverse('organization-detail', args=[organization.id])
    data = {'name': 'Updated Organization', 'max_user_count': 15}
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    organization.refresh_from_db()
    assert organization.name == 'Updated Organization'
    assert organization.max_user_count == 15


@pytest.mark.django_db
def test_analyst_cannot_update_organization(client, organization_analyst_user, organization):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-detail', args=[organization.id])
    data = {'name': 'Unauthorized Update', 'max_user_count': 15}
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_agent_cannot_update_organization(client, agent, organization):
    client.force_authenticate(user=agent.user)
    url = reverse('organization-detail', args=[organization.id])
    data = {'name': 'Unauthorized Update', 'max_user_count': 15}
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_unauthenticated_user_cannot_update_organization(client, organization):
    url = reverse('organization-detail', args=[organization.id])
    data = {'name': 'Unauthorized Update', 'max_user_count': 15}
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_superuser_can_delete_organization(client, superuser, organization):
    client.force_authenticate(user=superuser)
    url = reverse('organization-detail', args=[organization.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Organization.objects.filter(id=organization.id).exists()


@pytest.mark.django_db
def test_analyst_cannot_delete_organization(client, organization_analyst_user, organization):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-detail', args=[organization.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Organization.objects.filter(id=organization.id).exists()


@pytest.mark.django_db
def test_agent_cannot_delete_organization(client, agent, organization):
    client.force_authenticate(user=agent.user)
    url = reverse('organization-detail', args=[organization.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Organization.objects.filter(id=organization.id).exists()


@pytest.mark.django_db
def test_unauthenticated_user_cannot_delete_organization(client, organization):
    url = reverse('organization-detail', args=[organization.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Organization.objects.filter(id=organization.id).exists()


@pytest.mark.django_db
def test_superuser_can_access_any_organization_conversations_action(client, superuser, organization,
                                                                    another_organization):
    client.force_authenticate(user=superuser)
    url = reverse('organization-conversations', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    url = reverse('organization-conversations', args=[another_organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_analyst_can_access_own_organization_conversations_action(client, organization_analyst_user, organization,
                                                                  conversation):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-conversations', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['conversations']['results']) == 1


@pytest.mark.django_db
def test_analyst_cannot_access_other_organization_conversations_action(client, organization_analyst_user,
                                                                       another_organization):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-conversations', args=[another_organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_agent_cannot_access_own_organization_conversations_action(client, agent, organization):
    client.force_authenticate(user=agent.user)
    url = reverse('organization-conversations', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_agent_cannot_access_other_organization_conversations_action(client, agent, another_organization):
    client.force_authenticate(user=agent.user)
    url = reverse('organization-conversations', args=[another_organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_conversations_action(client, organization):
    url = reverse('organization-conversations', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_superuser_can_access_any_organization_trends_actions(client, superuser, organization, another_organization):
    client.force_authenticate(user=superuser)
    for org in [organization, another_organization]:
        for action in TREND_ACTIONS:
            url = reverse(f'organization-{action}', args=[org.id])
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_analyst_can_access_own_organization_trends_actions(client, organization_analyst_user, organization):
    client.force_authenticate(user=organization_analyst_user)
    for action in TREND_ACTIONS:
        url = reverse(f'organization-{action}', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_analyst_cannot_access_other_organization_trends_actions(client, organization_analyst_user,
                                                                 another_organization):
    client.force_authenticate(user=organization_analyst_user)
    for action in TREND_ACTIONS:
        url = reverse(f'organization-{action}', args=[another_organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_agent_cannot_access_own_organization_trends_actions(client, agent, organization):
    client.force_authenticate(user=agent.user)
    for action in TREND_ACTIONS:
        url = reverse(f'organization-{action}', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_agent_cannot_access_other_organization_trends_actions(client, agent, another_organization):
    client.force_authenticate(user=agent.user)
    for action in TREND_ACTIONS:
        url = reverse(f'organization-{action}', args=[another_organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_trends_actions(client, organization):
    for action in TREND_ACTIONS:
        url = reverse(f'organization-{action}', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
