import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from call_miner.models import Organization, Analyst, Agent, Customer, Conversation
from datetime import datetime


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
        summary='Another summary',
        title='Another Conversation',
        sentiment=0.5,
        agent=another_agent,
        customer=another_customer,
        input_tokens=100,
        output_tokens=50
    )


@pytest.mark.django_db
def test_analyst_can_list_conversations_in_organization(client, organization_analyst_user, conversation,
                                                        another_conversation):
    """
    Test that an employee can list conversations within their own organization,
    and does not see conversations from other organizations.
    """
    # Employee should only see conversations from their own organization
    client.force_authenticate(user=organization_analyst_user)
    response = client.get(reverse('conversation-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == conversation.title


@pytest.mark.django_db
def test_superuser_can_list_all_conversations(client, superuser, conversation, another_conversation):
    """
    Test that a superuser can list all conversations across all organizations.
    """
    # Superuser should see all conversations
    client.force_authenticate(user=superuser)
    response = client.get(reverse('conversation-list'))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) >= 2


@pytest.mark.django_db
def test_analyst_can_view_conversation_in_organization(client, organization_analyst_user, conversation):
    """
    Test that an employee can view a conversation within their own organization.
    """
    # Employee in the same organization should be able to view the conversation
    client.force_authenticate(user=organization_analyst_user)
    response = client.get(reverse('conversation-detail', args=[conversation.id]))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_analyst_cannot_view_conversation_in_other_organization(client, organization_analyst_user,
                                                                another_conversation):
    """
    Test that an employee cannot view a conversation from another organization.
    """
    # Employee should not be able to view a conversation from another organization
    client.force_authenticate(user=organization_analyst_user)
    response = client.get(reverse('conversation-detail', args=[another_conversation.id]))
    assert response.status_code == status.HTTP_404_NOT_FOUND  # Not found due to queryset filtering


@pytest.mark.django_db
def test_superuser_can_view_any_conversation(client, superuser, conversation, another_conversation):
    """
    Test that a superuser can view any conversation across all organizations.
    """
    # Superuser should be able to view any conversation
    client.force_authenticate(user=superuser)
    response = client.get(reverse('conversation-detail', args=[conversation.id]))
    assert response.status_code == status.HTTP_200_OK

    response = client.get(reverse('conversation-detail', args=[another_conversation.id]))
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_analyst_can_view_conversation_transcript(client, organization_analyst_user, conversation):
    """
    Test that an employee can view the transcript of a conversation within their own organization.
    """
    # Employee in the same organization should be able to view the conversation transcript
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('conversation-transcript', args=[conversation.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert 'transcript' in response.data
    assert 'results' in response.data['transcript']
    assert len(response.data['transcript']['results']) > 0


@pytest.mark.django_db
def test_analyst_cannot_view_other_organization_conversation_transcript(client, organization_analyst_user, another_conversation):
    """
    Test that an employee cannot view the transcript of a conversation from another organization.
    """
    # Employee should not be able to view the transcript of a conversation from another organization
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('conversation-transcript', args=[another_conversation.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND  # Not found due to queryset filtering


@pytest.mark.django_db
def test_superuser_can_view_any_conversation_transcript(client, superuser, conversation, another_conversation):
    """
    Test that a superuser can view the transcript of any conversation across all organizations.
    """
    # Superuser should be able to view any conversation transcript
    client.force_authenticate(user=superuser)
    url = reverse('conversation-transcript', args=[conversation.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    url = reverse('conversation-transcript', args=[another_conversation.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_process_transcript_output(client, organization_analyst_user, conversation):
    """
    Test that the process_transcript() method correctly processes the transcript and
    the ViewSet returns the expected paginated response.
    """
    client.force_authenticate(user=organization_analyst_user)
    url = reverse('conversation-transcript', args=[conversation.id])

    # Fetch all pages of the transcript
    all_messages = []
    next_url = url
    while next_url:
        response = client.get(next_url)
        assert response.status_code == status.HTTP_200_OK

        # Extract processed transcript from response
        transcript_data = response.data.get('transcript', {})
        assert 'results' in transcript_data
        messages = transcript_data['results']
        all_messages.extend(messages)

        next_url = transcript_data.get('next')

    # Expected messages after processing
    expected_messages = []
    lines = conversation.transcript.strip().split('\n')
    message_id = 0
    for line in lines:
        line = line.strip()
        if line.startswith('<agent>:'):
            message_text = line[len('<agent>:'):].strip()
            expected_messages.append({
                'id': message_id,
                'message': message_text,
                'class': 'agent-message'
            })
            message_id += 1
        elif line.startswith('<customer>:'):
            message_text = line[len('<customer>:'):].strip()
            expected_messages.append({
                'id': message_id,
                'message': message_text,
                'class': 'customer-message'
            })
            message_id += 1

    # Ensure the number of messages matches
    assert len(all_messages) == len(expected_messages)

    # Compare each message
    for msg, expected_msg in zip(all_messages, expected_messages):
        assert msg['id'] == expected_msg['id']
        assert msg['message'] == expected_msg['message']
        assert msg['class'] == expected_msg['class']


@pytest.mark.django_db
def test_transcript_pagination(client, organization_analyst_user, conversation, settings):
    """
    Test that the processed transcript is paginated correctly based on the PAGE_SIZE setting.
    """
    # Set page size for testing pagination
    settings.REST_FRAMEWORK['PAGE_SIZE'] = 15

    client.force_authenticate(user=organization_analyst_user)
    url = reverse('conversation-transcript', args=[conversation.id])
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    # Check that pagination is applied
    transcript_data = response.data.get('transcript', {})
    assert 'next' in transcript_data
    assert 'previous' in transcript_data
    assert len(transcript_data['results']) == settings.REST_FRAMEWORK['PAGE_SIZE']

    # Fetch next page if available
    next_url = transcript_data['next']
    if next_url:
        response_next = client.get(next_url)
        assert response_next.status_code == status.HTTP_200_OK
        transcript_data_next = response_next.data.get('transcript', {})
        assert len(transcript_data_next['results']) > 0


@pytest.mark.django_db
def test_analyst_cannot_create_conversation(client, organization_analyst_user, agent, customer):
    """
    Test that an employee cannot create a new conversation.
    """
    # Employee should not be able to create a conversation
    client.force_authenticate(user=organization_analyst_user)
    data = {
        'path': 'path/to/new_conversation',
        'date': datetime.now().isoformat(),
        'duration': 100.0,
        'transcript': 'New transcript',
        'summary': 'New summary',
        'title': 'New Conversation',
        'sentiment': 0.6,
        'topics': [],
        'agent': agent.id,
        'customer': customer.id,
        'input_tokens': 120,
        'output_tokens': 60
    }
    response = client.post(reverse('conversation-list'), data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_organization_admin_cannot_create_conversation(client, organization_admin_user, agent, customer):
    """
    Test that an organization admin cannot create a new conversation.
    """
    # Organization admin should not be able to create a conversation
    client.force_authenticate(user=organization_admin_user)
    data = {
        'path': 'path/to/new_conversation',
        'date': datetime.now().isoformat(),
        'duration': 100.0,
        'transcript': 'Admin transcript',
        'summary': 'Admin summary',
        'title': 'Admin Conversation',
        'sentiment': 0.7,
        'topics': [],
        'agent': agent.id,
        'customer': customer.id,
        'input_tokens': 130,
        'output_tokens': 70
    }
    response = client.post(reverse('conversation-list'), data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_superuser_can_create_conversation(client, superuser, agent, customer):
    """
    Test that a superuser can create a new conversation.
    """
    # Superuser should be able to create a conversation
    client.force_authenticate(user=superuser)
    data = {
        'path': 'path/to/new_conversation',
        'date': datetime.now().isoformat(),
        'duration': 100.0,
        'transcript': 'New transcript',
        'summary': 'New summary',
        'title': 'New Conversation',
        'sentiment': 0.6,
        'topics': [],
        'agent': agent.id,
        'customer': customer.id,
        'input_tokens': 120,
        'output_tokens': 60
    }
    response = client.post(reverse('conversation-list'), data, format='json')
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_analyst_cannot_update_conversation(client, organization_analyst_user, conversation):
    """
    Test that an employee cannot update an existing conversation.
    """
    # Employee should not be able to update a conversation
    client.force_authenticate(user=organization_analyst_user)
    data = {'title': 'Updated Title'}
    response = client.patch(reverse('conversation-detail', args=[conversation.id]), data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_superuser_can_update_conversation(client, superuser, conversation):
    """
    Test that a superuser can update an existing conversation.
    """
    # Superuser should be able to update a conversation
    client.force_authenticate(user=superuser)
    data = {'title': 'Updated Title'}
    response = client.patch(reverse('conversation-detail', args=[conversation.id]), data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'Updated Title'


@pytest.mark.django_db
def test_analyst_cannot_delete_conversation(client, organization_analyst_user, conversation):
    """
    Test that an employee cannot delete a conversation.
    """
    # Employee should not be able to delete a conversation
    client.force_authenticate(user=organization_analyst_user)
    response = client.delete(reverse('conversation-detail', args=[conversation.id]))
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_superuser_can_delete_conversation(client, superuser, conversation):
    """
    Test that a superuser can delete a conversation.
    """
    # Superuser should be able to delete a conversation
    client.force_authenticate(user=superuser)
    response = client.delete(reverse('conversation-detail', args=[conversation.id]))
    assert response.status_code == status.HTTP_204_NO_CONTENT
