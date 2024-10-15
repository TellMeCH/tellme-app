import pytest
from unittest.mock import patch
from django.urls import reverse, exceptions
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from call_miner.models import Organization, Analyst, Agent, Customer, Conversation, Topic
from datetime import datetime

TREND_ACTIONS = ['conversations', 'conversation-trend', 'duration-trend', 'sentiment-trend']


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


@pytest.mark.django_db
def test_superuser_can_list_all_topics(client, superuser, topic, another_topic):
    client.force_authenticate(user=superuser)
    response = client.get(reverse('topic-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2


@pytest.mark.django_db
def test_organization_admin_can_list_topics(client, organization_admin_user, topic, another_topic):
    client.force_authenticate(user=organization_admin_user)
    response = client.get(reverse('topic-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == topic.name


@pytest.mark.django_db
def test_organization_analyst_can_list_topics(client, organization_analyst_user, topic, another_topic):
    client.force_authenticate(user=organization_analyst_user)
    response = client.get(reverse('topic-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == topic.name


@pytest.mark.django_db
def test_agent_in_same_organization_can_list_topics(client, agent, topic, another_topic):
    client.force_authenticate(user=agent.user)
    response = client.get(reverse('topic-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == topic.name


@pytest.mark.django_db
def test_analyst_in_other_organization_can_list_topics(client, another_organization_analyst_user, topic, another_topic):
    client.force_authenticate(user=another_organization_analyst_user)
    response = client.get(reverse('topic-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == another_topic.name


@pytest.mark.django_db
def test_agent_in_other_organization_can_list_topics(client, another_agent, topic, another_topic):
    client.force_authenticate(user=another_agent.user)
    response = client.get(reverse('topic-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == another_topic.name


@pytest.mark.django_db
def test_unauthenticated_user_cannot_list_topics(client, topic, another_topic):
    response = client.get(reverse('topic-list'))
    assert response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_superuser_can_retrieve_topic(client, superuser, topic):
    client.force_authenticate(user=superuser)
    url = reverse('topic-detail', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == topic.name


@pytest.mark.django_db
def test_organization_analyst_can_retrieve_topic(client, organization_analyst_user, topic):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('topic-detail', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == topic.name


@pytest.mark.django_db
def test_agent_in_same_organization_cannot_retrieve_topic(client, agent, topic):
    client.force_authenticate(user=agent.user)
    url = reverse('topic-detail', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_analyst_in_other_organization_cannot_retrieve_topic(client, another_organization_analyst_user, topic):
    client.force_authenticate(user=another_organization_analyst_user)
    url = reverse('topic-detail', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_agent_in_other_organization_cannot_retrieve_topic(client, another_agent, topic):
    client.force_authenticate(user=another_agent.user)
    url = reverse('topic-detail', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_unauthenticated_user_cannot_retrieve_topic(client, topic):
    url = reverse('topic-detail', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_superuser_can_create_topic(client, superuser, organization):
    client.force_authenticate(user=superuser)
    data = {
        'name': 'New Topic',
        'description': 'A new topic',
        'organization': organization.id,
        'is_active': True
    }
    response = client.post(reverse('topic-list'), data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == 'New Topic'


@pytest.mark.django_db
def test_organization_analyst_can_create_topic(client, organization_analyst_user, organization):
    client.force_authenticate(user=organization_analyst_user)
    data = {
        'name': 'Analyst Topic',
        'description': 'Created by analyst',
        'organization': organization.id,
        'is_active': True
    }
    response = client.post(reverse('topic-list'), data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == 'Analyst Topic'


@pytest.mark.django_db
def test_agent_in_same_organization_cannot_create_topic(client, agent, organization):
    client.force_authenticate(user=agent.user)
    data = {
        'name': 'Agent Topic',
        'description': 'Created by agent',
        'organization': organization.id,
        'is_active': True
    }
    response = client.post(reverse('topic-list'), data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_analyst_in_other_organization_cannot_create_topic(client, another_organization_analyst_user, organization):
    client.force_authenticate(user=another_organization_analyst_user)
    data = {
        'name': 'Cross Org Topic',
        'description': 'Attempt to create in another org',
        'organization': organization.id,
        'is_active': True
    }
    response = client.post(reverse('topic-list'), data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_agent_in_other_organization_cannot_create_topic(client, another_agent, organization):
    client.force_authenticate(user=another_agent.user)
    data = {
        'name': 'Another Agent Topic',
        'description': 'Created by another agent',
        'organization': organization.id,
        'is_active': True
    }
    response = client.post(reverse('topic-list'), data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_topic(client, organization):
    data = {
        'name': 'Unauthenticated Topic',
        'description': 'Should not be created',
        'organization': organization.id,
        'is_active': True
    }
    response = client.post(reverse('topic-list'), data)
    assert response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_superuser_can_update_topic(client, superuser, topic):
    client.force_authenticate(user=superuser)
    data = {'name': 'Updated Topic Name'}
    url = reverse('topic-detail', args=[topic.id])
    response = client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == 'Updated Topic Name'


@pytest.mark.django_db
def test_organization_analyst_can_update_topic(client, organization_analyst_user, topic):
    client.force_authenticate(user=organization_analyst_user)
    data = {'description': 'Updated by analyst'}
    url = reverse('topic-detail', args=[topic.id])
    response = client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['description'] == 'Updated by analyst'


@pytest.mark.django_db
def test_agent_in_same_organization_cannot_update_topic(client, agent, topic):
    client.force_authenticate(user=agent.user)
    data = {'description': 'Attempted update by agent'}
    url = reverse('topic-detail', args=[topic.id])
    response = client.patch(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_analyst_in_other_organization_cannot_update_topic(client, another_organization_analyst_user, topic):
    client.force_authenticate(user=another_organization_analyst_user)
    data = {'description': 'Attempted cross-org update'}
    url = reverse('topic-detail', args=[topic.id])
    response = client.patch(url, data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_agent_in_other_organization_cannot_update_topic(client, another_agent, topic):
    client.force_authenticate(user=another_agent.user)
    data = {'description': 'Attempted update by another agent'}
    url = reverse('topic-detail', args=[topic.id])
    response = client.patch(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_unauthenticated_user_cannot_update_topic(client, topic):
    data = {'description': 'Attempted update by unauthenticated user'}
    url = reverse('topic-detail', args=[topic.id])
    response = client.patch(url, data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_superuser_can_delete_topic(client, superuser, topic):
    client.force_authenticate(user=superuser)
    url = reverse('topic-detail', args=[topic.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_organization_analyst_can_delete_topic(client, organization_analyst_user, topic):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('topic-detail', args=[topic.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_agent_in_same_organization_cannot_delete_topic(client, agent, topic):
    client.force_authenticate(user=agent.user)
    url = reverse('topic-detail', args=[topic.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_analyst_in_other_organization_cannot_delete_topic(client, another_organization_analyst_user, topic):
    client.force_authenticate(user=another_organization_analyst_user)
    url = reverse('topic-detail', args=[topic.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_agent_in_other_organization_cannot_delete_topic(client, another_agent, topic):
    client.force_authenticate(user=another_agent.user)
    url = reverse('topic-detail', args=[topic.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_unauthenticated_user_cannot_delete_topic(client, topic):
    url = reverse('topic-detail', args=[topic.id])
    response = client.delete(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def _test_trend_action(client, url, expected_status):
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
def test_superuser_can_access_trend_actions(client, superuser, topic):
    client.force_authenticate(user=superuser)
    for action in TREND_ACTIONS:
        url = reverse(f'topic-{action}', args=[topic.id])
        _test_trend_action(client, url, status.HTTP_200_OK)


@pytest.mark.django_db
def test_organization_analyst_can_access_trend_actions(client, organization_analyst_user, topic):
    client.force_authenticate(user=organization_analyst_user)
    for action in TREND_ACTIONS:
        url = reverse(f'topic-{action}', args=[topic.id])
        _test_trend_action(client, url, status.HTTP_200_OK)


@pytest.mark.django_db
def test_agent_in_same_organization_cannot_access_trend_actions(client, agent, topic):
    client.force_authenticate(user=agent.user)
    for action in TREND_ACTIONS:
        url = reverse(f'topic-{action}', args=[topic.id])
        _test_trend_action(client, url, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_analyst_in_other_organization_cannot_access_trend_actions(client, another_organization_analyst_user, topic):
    client.force_authenticate(user=another_organization_analyst_user)
    for action in TREND_ACTIONS:
        url = reverse(f'topic-{action}', args=[topic.id])
        _test_trend_action(client, url, status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
def test_agent_in_other_organization_cannot_access_trend_actions(client, another_agent, topic):
    client.force_authenticate(user=another_agent.user)
    for action in TREND_ACTIONS:
        url = reverse(f'topic-{action}', args=[topic.id])
        _test_trend_action(client, url, status.HTTP_404_NOT_FOUND)


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_trend_actions(client, topic):
    for action in TREND_ACTIONS:
        url = reverse(f'topic-{action}', args=[topic.id])
        _test_trend_action(client, url, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
def test_superuser_can_access_summary_data(client, superuser, topic):
    client.force_authenticate(user=superuser)
    url = reverse('topic-summary-data', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_organization_analyst_can_access_summary_data(client, organization_analyst_user, topic):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('topic-summary-data', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_agent_in_same_organization_cannot_access_summary_data(client, agent, topic):
    client.force_authenticate(user=agent.user)
    url = reverse('topic-summary-data', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_analyst_in_other_organization_cannot_access_summary_data(client, another_organization_analyst_user, topic):
    client.force_authenticate(user=another_organization_analyst_user)
    url = reverse('topic-summary-data', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_agent_in_other_organization_cannot_access_summary_data(client, another_agent, topic):
    client.force_authenticate(user=another_agent.user)
    url = reverse('topic-summary-data', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_summary_data(client, topic):
    url = reverse('topic-summary-data', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_superuser_can_list_active_topics(client, superuser, topic, another_topic):
    client.force_authenticate(user=superuser)
    url = reverse('topic-list-active')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2


@pytest.mark.django_db
def test_organization_analyst_can_list_active_topics(client, organization_analyst_user, topic, another_topic):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('topic-list-active')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == topic.name


@pytest.mark.django_db
def test_agent_in_same_organization_can_list_active_topics(client, agent, topic, another_topic):
    client.force_authenticate(user=agent.user)
    url = reverse('topic-list-active')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == topic.name


@pytest.mark.django_db
def test_analyst_in_other_organization_can_list_active_topics(client, another_organization_analyst_user, topic, another_topic):
    client.force_authenticate(user=another_organization_analyst_user)
    url = reverse('topic-list-active')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == another_topic.name


@pytest.mark.django_db
def test_agent_in_other_organization_can_list_active_topics(client, another_agent, topic, another_topic):
    client.force_authenticate(user=another_agent.user)
    url = reverse('topic-list-active')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == another_topic.name


@pytest.mark.django_db
def test_unauthenticated_user_cannot_list_active_topics(client, topic, another_topic):
    url = reverse('topic-list-active')
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_active_topics_excludes_inactive_topics(client, organization_analyst_user, topic, organization):
    # Create an inactive topic
    Topic.objects.create(
        name='Inactive Topic',
        description='Should not appear in active list',
        organization=organization,
        is_active=False
    )
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('topic-list-active')
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == topic.name


@pytest.mark.django_db
def test_topic_conversations_action_returns_expected_content(client, organization_analyst_user, topic, conversation):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('topic-conversations', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'conversations' in response.data
    results = response.data['conversations']['results']
    assert len(results) == 1
    assert results[0]['title'] == conversation.title


@pytest.mark.django_db
def test_topic_conversation_topic_trend_action_is_disabled(client, organization_analyst_user, topic, conversation):
    client.force_authenticate(user=organization_analyst_user)
    with pytest.raises(exceptions.NoReverseMatch):
        url = reverse('topic-conversation-topic-trend', args=[topic.id])
        response = client.get(url)


@pytest.mark.django_db
def test_topic_conversation_trend_action_returns_expected_content(client, organization_analyst_user, topic, conversation):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('topic-conversation-trend', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'conversation_trend' in response.data
    results = response.data['conversation_trend']['results']
    assert len(results) == 1  # Depending on date truncation
    assert results[0]['count'] == 1


@pytest.mark.django_db
def test_topic_duration_trend_action_returns_expected_content(client, organization_analyst_user, topic, conversation):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('topic-duration-trend', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'duration_trend' in response.data
    results = response.data['duration_trend']['results']
    assert len(results) == 1
    assert results[0]['avg_value'] == conversation.duration


@pytest.mark.django_db
def test_topic_sentiment_trend_action_returns_expected_content(client, organization_analyst_user, topic, conversation):
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('topic-sentiment-trend', args=[topic.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'sentiment_trend' in response.data
    results = response.data['sentiment_trend']['results']
    assert len(results) == 1
    assert results[0]['avg_value'] == conversation.sentiment


@pytest.mark.django_db
def test_topic_summary_data_returns_expected_content(client, organization_analyst_user, topic, conversation):
    with patch('call_miner.models.condense_summaries') as mock_condense_summaries:
        mock_condense_summaries.return_value = 'Mocked summary text'
        client.force_authenticate(user=organization_analyst_user)
        url = reverse('topic-summary-data', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'summary_data' in response.data
        summary_data = response.data['summary_data']
        assert summary_data['summary'] == 'Mocked summary text'
        assert summary_data['summary_call_count'] == 1  # Only one conversation
        assert summary_data['summary_date'].date() == conversation.date.date()
