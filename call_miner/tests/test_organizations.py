import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from call_miner.models import Organization, Analyst, Agent, Customer, Conversation, Topic
from datetime import datetime, timedelta, date

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
    """Create and return an analyst user associated with the given organization."""
    user = User.objects.create_user('employee', 'employee@example.com', 'password')
    Analyst.objects.create(user=user, organization=organization, role='ANALYST', is_organization_admin=False)
    return user


@pytest.fixture
def another_organization_analyst_user(another_organization):
    """Create and return an analyst user associated with another organization."""
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
def test_superuser_can_list_organizations(client, superuser):
    """Test that a superuser can list all organizations."""
    client.force_authenticate(user=superuser)
    url = reverse('organization-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0  # Check that organizations are returned


@pytest.mark.django_db
def test_analyst_cannot_list_all_organizations(client, organization_analyst_user):
    """Test that a regular analyst cannot list all organizations."""
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_agent_cannot_list_all_organizations(client, agent):
    """Test that an agent cannot list all organizations."""
    client.force_authenticate(user=agent.user)
    url = reverse('organization-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_another_organization_analyst_cannot_list_organizations(client, another_organization_analyst_user):
    """Test that an analyst from another organization cannot list organizations."""
    client.force_authenticate(user=another_organization_analyst_user)
    url = reverse('organization-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_unauthenticated_user_cannot_list_all_organizations(client, agent):
    """Test that an unauthenticated user cannot list all organizations."""
    client.force_authenticate(user=agent.user)
    url = reverse('organization-list')
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_superuser_can_retrieve_any_organization(client, superuser, organization, another_organization):
    """Test that a superuser can retrieve any organization."""
    client.force_authenticate(user=superuser)
    url = reverse('organization-detail', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    url = reverse('organization-detail', args=[another_organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_analyst_can_retrieve_own_organization(client, organization_analyst_user, organization):
    """Test that an analyst can retrieve their own organization."""
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-detail', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'Test Organization'


@pytest.mark.django_db
def test_analyst_cannot_retrieve_other_organization(client, organization_analyst_user, another_organization):
    """Test that an analyst cannot retrieve another organization's details."""
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-detail', args=[another_organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_agent_cannot_retrieve_own_organization(client, agent, organization):
    """Test that an agent cannot retrieve their own organization's details."""
    client.force_authenticate(user=agent.user)
    url = reverse('organization-detail', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_agent_cannot_retrieve_other_organization(client, agent, another_organization):
    """Test that an agent cannot retrieve another organization's details."""
    client.force_authenticate(user=agent.user)
    url = reverse('organization-detail', args=[another_organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_another_organization_analyst_cannot_retrieve_organization(client, another_organization_analyst_user,
                                                                   organization):
    """Test that an analyst from another organization cannot retrieve an organization's details."""
    client.force_authenticate(user=another_organization_analyst_user)
    url = reverse('organization-detail', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_unauthenticated_user_cannot_retrieve_organization(client, organization):
    """Test that an unauthenticated user cannot retrieve an organization's details."""
    url = reverse('organization-detail', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_superuser_can_create_organization(client, superuser):
    """Test that a superuser can create an organization."""
    client.force_authenticate(user=superuser)
    url = reverse('organization-list')
    data = {'name': 'New Organization', 'max_user_count': 20}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Organization.objects.filter(name='New Organization').exists()


@pytest.mark.django_db
def test_analyst_cannot_create_organization(client, organization_analyst_user):
    """Test that an analyst cannot create an organization."""
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-list')
    data = {'name': 'Unauthorized Organization', 'max_user_count': 20}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Organization.objects.filter(name='Unauthorized Organization').exists()


@pytest.mark.django_db
def test_agent_cannot_create_organization(client, agent):
    """Test that an agent cannot create an organization."""
    client.force_authenticate(user=agent.user)
    url = reverse('organization-list')
    data = {'name': 'Unauthorized Organization', 'max_user_count': 20}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Organization.objects.filter(name='Unauthorized Organization').exists()


@pytest.mark.django_db
def test_another_organization_analyst_cannot_create_organization(client, another_organization_analyst_user):
    """Test that an analyst from another organization cannot create an organization."""
    client.force_authenticate(user=another_organization_analyst_user)
    url = reverse('organization-list')
    data = {'name': 'Unauthorized Creation', 'max_user_count': 20}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_organization(client):
    """Test that an unauthenticated user cannot create an organization."""
    url = reverse('organization-list')
    data = {'name': 'Unauthorized Organization', 'max_user_count': 20}
    response = client.post(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not Organization.objects.filter(name='Unauthorized Organization').exists()


@pytest.mark.django_db
def test_superuser_can_update_organization(client, superuser, organization):
    """Test that a superuser can update an organization's details."""
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
    """Test that an analyst cannot update an organization's details."""
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-detail', args=[organization.id])
    data = {'name': 'Unauthorized Update', 'max_user_count': 15}
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_agent_cannot_update_organization(client, agent, organization):
    """Test that an agent cannot update an organization's details."""
    client.force_authenticate(user=agent.user)
    url = reverse('organization-detail', args=[organization.id])
    data = {'name': 'Unauthorized Update', 'max_user_count': 15}
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_another_organization_analyst_cannot_update_organization(client, another_organization_analyst_user,
                                                                 organization):
    """Test that an analyst from another organization cannot update an organization's details."""
    client.force_authenticate(user=another_organization_analyst_user)
    url = reverse('organization-detail', args=[organization.id])
    data = {'name': 'Unauthorized Update', 'max_user_count': 20}
    response = client.put(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_unauthenticated_user_cannot_update_organization(client, organization):
    """Test that an unauthenticated user cannot update an organization's details."""
    url = reverse('organization-detail', args=[organization.id])
    data = {'name': 'Unauthorized Update', 'max_user_count': 15}
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_superuser_can_delete_organization(client, superuser, organization):
    """Test that a superuser can delete an organization."""
    client.force_authenticate(user=superuser)
    url = reverse('organization-detail', args=[organization.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Organization.objects.filter(id=organization.id).exists()


@pytest.mark.django_db
def test_analyst_cannot_delete_organization(client, organization_analyst_user, organization):
    """Test that an analyst cannot delete an organization."""
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-detail', args=[organization.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Organization.objects.filter(id=organization.id).exists()


@pytest.mark.django_db
def test_agent_cannot_delete_organization(client, agent, organization):
    """Test that an agent cannot delete an organization."""
    client.force_authenticate(user=agent.user)
    url = reverse('organization-detail', args=[organization.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Organization.objects.filter(id=organization.id).exists()


@pytest.mark.django_db
def test_another_organization_analyst_cannot_delete_organization(client, another_organization_analyst_user,
                                                                 organization):
    """Test that an analyst from another organization cannot delete an organization."""
    client.force_authenticate(user=another_organization_analyst_user)
    url = reverse('organization-detail', args=[organization.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_unauthenticated_user_cannot_delete_organization(client, organization):
    """Test that an unauthenticated user cannot delete an organization."""
    url = reverse('organization-detail', args=[organization.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Organization.objects.filter(id=organization.id).exists()


@pytest.mark.django_db
def test_superuser_can_access_any_organization_conversations_action(client, superuser, organization,
                                                                    another_organization):
    """Test that a superuser can access the conversations of any organization."""
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
    """Test that an analyst can access the conversations of their own organization."""
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-conversations', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['conversations']['results']) == 1


@pytest.mark.django_db
def test_analyst_cannot_access_other_organization_conversations_action(client, organization_analyst_user,
                                                                       another_organization):
    """Test that an analyst cannot access the conversations of another organization."""
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-conversations', args=[another_organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_agent_cannot_access_own_organization_conversations_action(client, agent, organization):
    """Test that an agent cannot access the conversations of their own organization."""
    client.force_authenticate(user=agent.user)
    url = reverse('organization-conversations', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_agent_cannot_access_other_organization_conversations_action(client, agent, another_organization):
    """Test that an agent cannot access the conversations of another organization."""
    client.force_authenticate(user=agent.user)
    url = reverse('organization-conversations', args=[another_organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_another_organization_analyst_cannot_access_other_organization_conversations_action(
        client,
        another_organization_analyst_user,
        organization):
    """Test that an analyst from another organization cannot access the conversations of a different organization."""
    client.force_authenticate(user=another_organization_analyst_user)
    url = reverse('organization-conversations', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_conversations_action(client, organization):
    """Test that an unauthenticated user cannot access an organization's conversations."""
    url = reverse('organization-conversations', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_superuser_can_access_any_organization_trends_actions(client, superuser, organization, another_organization):
    """Test that a superuser can access the trend actions of any organization."""
    client.force_authenticate(user=superuser)
    for org in [organization, another_organization]:
        for action in TREND_ACTIONS:
            url = reverse(f'organization-{action}', args=[org.id])
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_analyst_can_access_own_organization_trends_actions(client, organization_analyst_user, organization):
    """Test that an analyst can access the trend actions of their own organization."""
    client.force_authenticate(user=organization_analyst_user)
    for action in TREND_ACTIONS:
        url = reverse(f'organization-{action}', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_analyst_cannot_access_other_organization_trends_actions(client, organization_analyst_user,
                                                                 another_organization):
    """Test that an analyst cannot access the trend actions of another organization."""
    client.force_authenticate(user=organization_analyst_user)
    for action in TREND_ACTIONS:
        url = reverse(f'organization-{action}', args=[another_organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_agent_cannot_access_own_organization_trends_actions(client, agent, organization):
    """Test that an agent cannot access the trend actions of their own organization."""
    client.force_authenticate(user=agent.user)
    for action in TREND_ACTIONS:
        url = reverse(f'organization-{action}', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_agent_cannot_access_other_organization_trends_actions(client, agent, another_organization):
    """Test that an agent cannot access the trend actions of another organization."""
    client.force_authenticate(user=agent.user)
    for action in TREND_ACTIONS:
        url = reverse(f'organization-{action}', args=[another_organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_another_organization_analyst_cannot_access_other_organization_trends_actions(
        client,
        another_organization_analyst_user,
        organization
):
    """Test that an analyst from another organization cannot access the trend actions of a different organization."""
    client.force_authenticate(user=another_organization_analyst_user)
    for action in TREND_ACTIONS:
        url = reverse(f'organization-{action}', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_trends_actions(client, organization):
    """Test that an unauthenticated user cannot access an organization's trend actions."""
    for action in TREND_ACTIONS:
        url = reverse(f'organization-{action}', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_conversations_action_returns_correct_data(client, organization_analyst_user, organization, conversation):
    """Check the content of an organization's conversations."""
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-conversations', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'conversations' in data
    conversations = data['conversations']['results']
    assert len(conversations) == 1
    assert conversations[0]['title'] == conversation.title
    assert conversations[0]['date'].replace('Z', '') == conversation.date.isoformat()  # Adjust for timezone


@pytest.mark.django_db
def test_conversations_action_pagination(client, organization_analyst_user, organization, agent, customer):
    """Check that pagination works when calling organization-conversations."""
    # Create multiple conversations to test pagination
    for i in range(15):
        Conversation.objects.create(
            path=f'path/to/conversation_{i}',
            date=datetime.now() - timedelta(days=i),
            duration=100 + i,
            title=f'Test title {i}',
            summary=f'Test summary {i}',
            transcript=f'Test transcript {i}',
            sentiment=0.5 + i * 0.01,
            agent=agent,
            customer=customer,
            input_tokens=100 + i,
            output_tokens=50 + i
        )
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-conversations', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    conversations = data['conversations']['results']
    assert len(conversations) == 15
    assert 'next' in data['conversations']


@pytest.mark.django_db
def test_conversation_trend_action_returns_correct_data(client, organization_analyst_user, organization, agent,
                                                        customer):
    """Check that the daily conversation trend responds as expected to the different period specifications."""
    # Create conversations on different days
    for i in range(5):
        Conversation.objects.create(
            path=f'path/to/conversation_{i}',
            date=datetime.now() - timedelta(days=i),
            duration=100 + i,
            title=f'Test title {i}',
            summary=f'Test summary {i}',
            transcript=f'Test transcript {i}',
            sentiment=0.5 + i * 0.1,
            agent=agent,
            customer=customer,
            input_tokens=100 + i,
            output_tokens=50 + i
        )
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-conversation-trend', args=[organization.id])
    response = client.get(url, {'trend_period': 'daily'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'conversation_trend' in data
    results = data['conversation_trend']['results']
    assert len(results) == 5  # One entry per day
    for entry in results:
        assert 'date' in entry
        assert 'count' in entry
        assert entry['count'] == 1


@pytest.mark.django_db
def test_conversation_topic_trend_action_returns_correct_data(client, organization_analyst_user, organization, agent,
                                                              customer):
    """Check that the organization's topic trends are as expected."""
    # Create topics
    topic1 = Topic.objects.create(name='Topic 1', description='Description 1', organization=organization)
    topic2 = Topic.objects.create(name='Topic 2', description='Description 2', organization=organization)
    # Create conversations with topics
    for i in range(5):
        conv = Conversation.objects.create(
            path=f'path/to/conversation_{i}',
            date=datetime.now() - timedelta(days=i),
            duration=100 + i,
            title=f'Test title {i}',
            summary=f'Test summary {i}',
            transcript=f'Test transcript {i}',
            sentiment=0.5 + i * 0.1,
            agent=agent,
            customer=customer,
            input_tokens=100 + i,
            output_tokens=50 + i
        )
        if i % 2 == 0:
            conv.topics.add(topic1)
        else:
            conv.topics.add(topic2)
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-conversation-topic-trend', args=[organization.id])
    response = client.get(url, {'trend_period': 'daily'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'conversation_topic_trend' in data
    results = data['conversation_topic_trend']['results']
    assert len(results) == 5  # One entry per day per topic
    for entry in results:
        assert 'date' in entry
        assert 'topic' in entry
        assert 'count' in entry
        assert entry['count'] == 1
        assert entry['topic'] in ['Topic 1', 'Topic 2']


@pytest.mark.django_db
def test_duration_trend_action_returns_correct_data(client, organization_analyst_user, organization, agent, customer):
    """Check that the duration trend of the organization returns the expected results."""
    # Create conversations with varying durations
    for i in range(5):
        Conversation.objects.create(
            path=f'path/to/conversation_{i}',
            date=datetime.now() - timedelta(days=i),
            duration=100 + i * 10,
            title=f'Test title {i}',
            summary=f'Test summary {i}',
            transcript=f'Test transcript {i}',
            sentiment=0.5,
            agent=agent,
            customer=customer,
            input_tokens=100,
            output_tokens=50
        )
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-duration-trend', args=[organization.id])
    response = client.get(url, {'trend_period': 'daily'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'duration_trend' in data
    results = data['duration_trend']['results']
    assert len(results) == 5
    for entry in results:
        assert 'date' in entry
        assert 'avg_value' in entry
        assert entry['avg_value'] in [100.0, 110.0, 120.0, 130.0, 140.0]


@pytest.mark.django_db
def test_sentiment_trend_action_returns_correct_data(client, organization_analyst_user, organization, agent, customer):
    """Check that the sentiment trend of the organization returns the expected results."""
    # Create conversations with varying sentiments
    for i in range(5):
        Conversation.objects.create(
            path=f'path/to/conversation_{i}',
            date=datetime.now() - timedelta(days=i),
            duration=100,
            title=f'Test title {i}',
            summary=f'Test summary {i}',
            transcript=f'Test transcript {i}',
            sentiment=0.1 * i,
            agent=agent,
            customer=customer,
            input_tokens=100,
            output_tokens=50
        )
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-sentiment-trend', args=[organization.id])
    response = client.get(url, {'trend_period': 'daily'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'sentiment_trend' in data
    results = data['sentiment_trend']['results']
    assert len(results) == 5
    for entry in results:
        assert 'date' in entry
        assert 'avg_value' in entry


@pytest.mark.django_db
def test_trend_actions_invalid_trend_period(client, organization_analyst_user, organization):
    """Test that an error is raised whenever an incorrect trend period is specified."""
    client.force_authenticate(user=organization_analyst_user)
    for action in TREND_ACTIONS:
        url = reverse(f'organization-{action}', args=[organization.id])
        response = client.get(url, {'trend_period': 'invalid_period'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_conversation_trend_action_weekly_period(client, organization_analyst_user, organization, agent, customer):
    """Test the conversation trend action when a weekly period is specified."""
    # Create conversations over several weeks
    for i in range(21):  # 3 weeks
        Conversation.objects.create(
            path=f'path/to/conversation_{i}',
            date=date(2024, 1, 1) + timedelta(days=i),
            duration=100,
            title=f'Test title {i}',
            summary=f'Test summary {i}',
            transcript=f'Test transcript {i}',
            sentiment=0.5,
            agent=agent,
            customer=customer,
            input_tokens=100,
            output_tokens=50
        )
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-conversation-trend', args=[organization.id])
    response = client.get(url, {'trend_period': 'weekly'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    results = data['conversation_trend']['results']
    assert len(results) == 3  # Three weeks
    for entry in results:
        assert 'date' in entry
        assert 'count' in entry


@pytest.mark.django_db
def test_conversation_trend_action_monthly_period(client, organization_analyst_user, organization, agent, customer):
    """Test the conversation trend action when a monthly period is specified."""
    # Create conversations over several months
    for i in range(90):  # 3 months
        Conversation.objects.create(
            path=f'path/to/conversation_{i}',
            date=date(2024, 1, 1) + timedelta(days=i),
            duration=100,
            title=f'Test title {i}',
            summary=f'Test summary {i}',
            transcript=f'Test transcript {i}',
            sentiment=0.5,
            agent=agent,
            customer=customer,
            input_tokens=100,
            output_tokens=50
        )
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-conversation-trend', args=[organization.id])
    response = client.get(url, {'trend_period': 'monthly'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    results = data['conversation_trend']['results']
    assert len(results) == 3
    for entry in results:
        assert 'date' in entry
        assert 'count' in entry


@pytest.mark.django_db
def test_duration_trend_action_weekly_period(client, organization_analyst_user, organization, agent, customer):
    """Test the duration trend action when a weekly period is specified."""
    # Create conversations over several weeks
    for i in range(21):  # 3 weeks
        Conversation.objects.create(
            path=f'path/to/conversation_{i}',
            date=date(2024, 1, 1) + timedelta(days=i),
            duration=100 + i,
            title=f'Test title {i}',
            summary=f'Test summary {i}',
            transcript=f'Test transcript {i}',
            sentiment=0.5,
            agent=agent,
            customer=customer,
            input_tokens=100,
            output_tokens=50
        )
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-duration-trend', args=[organization.id])
    response = client.get(url, {'trend_period': 'weekly'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    results = data['duration_trend']['results']
    assert len(results) == 3
    for entry in results:
        assert 'date' in entry
        assert 'avg_value' in entry


@pytest.mark.django_db
def test_duration_trend_action_monthly_period(client, organization_analyst_user, organization, agent, customer):
    """Test the duration trend action when a monthly period is specified."""
    # Create conversations over several months
    for i in range(90):  # Approx 3 months
        Conversation.objects.create(
            path=f'path/to/conversation_{i}',
            date=date(2024, 1, 1) + timedelta(days=i),
            duration=100 + i,
            title=f'Test title {i}',
            summary=f'Test summary {i}',
            transcript=f'Test transcript {i}',
            sentiment=0.5,
            agent=agent,
            customer=customer,
            input_tokens=100,
            output_tokens=50
        )
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-duration-trend', args=[organization.id])
    response = client.get(url, {'trend_period': 'monthly'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    results = data['duration_trend']['results']
    assert len(results) == 3  # Three months
    for entry in results:
        assert 'date' in entry
        assert 'avg_value' in entry


@pytest.mark.django_db
def test_sentiment_trend_action_weekly_period(client, organization_analyst_user, organization, agent, customer):
    """Test the sentiment trend action when a weekly period is specified."""
    # Create conversations over several weeks
    for i in range(21):  # 3 weeks
        Conversation.objects.create(
            path=f'path/to/conversation_{i}',
            date=date(2024, 1, 1) + timedelta(days=i),
            duration=100 + i,
            title=f'Test title {i}',
            summary=f'Test summary {i}',
            transcript=f'Test transcript {i}',
            sentiment=0.5,
            agent=agent,
            customer=customer,
            input_tokens=100,
            output_tokens=50
        )
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-sentiment-trend', args=[organization.id])
    response = client.get(url, {'trend_period': 'weekly'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    results = data['sentiment_trend']['results']
    assert len(results) == 3
    for entry in results:
        assert 'date' in entry
        assert 'avg_value' in entry


@pytest.mark.django_db
def test_sentiment_trend_action_monthly_period(client, organization_analyst_user, organization, agent, customer):
    """Test the sentiment trend action when a monthly period is specified."""
    # Create conversations over several months
    for i in range(90):  # Approx 3 months
        Conversation.objects.create(
            path=f'path/to/conversation_{i}',
            date=date(2024, 1, 1) + timedelta(days=i),
            duration=100 + i,
            title=f'Test title {i}',
            summary=f'Test summary {i}',
            transcript=f'Test transcript {i}',
            sentiment=0.5,
            agent=agent,
            customer=customer,
            input_tokens=100,
            output_tokens=50
        )
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-sentiment-trend', args=[organization.id])
    response = client.get(url, {'trend_period': 'monthly'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    results = data['sentiment_trend']['results']
    assert len(results) == 3  # Three months
    for entry in results:
        assert 'date' in entry
        assert 'avg_value' in entry

@pytest.mark.django_db
def test_conversations_action_no_data(client, organization_analyst_user, organization):
    """Test that the conversations action can return an empty result when no conversations are present."""
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('organization-conversations', args=[organization.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'conversations' in data
    assert data['conversations']['results'] == []


@pytest.mark.django_db
def test_trends_actions_no_data(client, organization_analyst_user, organization):
    """Test that the conversation trend actions can return an empty result when no conversations are present."""
    client.force_authenticate(user=organization_analyst_user)
    for action in TREND_ACTIONS:
        url = reverse(f'organization-{action}', args=[organization.id])
        response = client.get(url, {'trend_period': 'daily'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert action.replace('-', '_') in data
        assert data[action.replace('-', '_')]['results'] == []
