import pytest
from django.urls import reverse
from call_miner.models import Conversation, Agent, Customer, Organization, Topic
from datetime import datetime

@pytest.fixture
def setup_data(db):
    """
    Fixture to create the necessary test data (Organization, Agent, Customer, Topics, and a Conversation).
    This will automatically roll back the changes after each test.
    """
    organization = Organization.objects.create(name="Test Organization")
    agent = Agent.objects.create(name="Test Agent", organization=organization)
    customer = Customer.objects.create(name="Test Customer", organization=organization)

    topic1 = Topic.objects.create(name="Topic 1", organization=organization, description="Topic 1 Description")
    topic2 = Topic.objects.create(name="Topic 2", organization=organization, description="Topic 2 Description")

    conversation = Conversation.objects.create(
        path="test_path",
        date=datetime.now(),
        duration=300,
        transcript="Agent: Hello\n\nCustomer: Hi there\n\nAgent: How can I help?\n\nCustomer: I need assistance",
        sentiment=0.5,
        summary="A short summary",
        input_tokens=10,
        output_tokens=20,
        customer=customer,
        agent=agent
    )
    conversation.topics.set([topic1, topic2])

    return {
        'organization': organization,
        'agent': agent,
        'customer': customer,
        'topic1': topic1,
        'topic2': topic2,
        'conversation': conversation
    }


@pytest.mark.django_db
def test_call_view(client, setup_data):
    """
    Test the CallView to ensure it returns the correct response and the context data is properly set up.
    """
    # Reverse lookup for the detail view's URL
    conversation = setup_data['conversation']
    url = reverse('call_detail', args=[conversation.id])

    # Get the response from the view
    response = client.get(url)

    # Test if the view returns a 200 status code
    assert response.status_code == 200

    # Test if the correct template is used
    assert 'call_detail.html' in [template.name for template in response.templates]

    # Test if the correct context data is passed
    assert response.context['call'] == conversation
    assert response.context['agent'] == setup_data['agent']
    assert response.context['customer'] == setup_data['customer']
    assert response.context['date'] == conversation.date
    assert response.context['summary'] == conversation.summary

    # Test that the topics are correct
    assert list(response.context['topics']) == [setup_data['topic1'], setup_data['topic2']]

    # Test that the transcript is processed correctly
    processed_transcript = response.context['transcript']
    expected_transcript = [
        {'speaker': 'Agent:', 'message': 'Hello', 'class': 'agent-message'},
        {'speaker': 'Customer:', 'message': 'Hi there', 'class': 'customer-message'},
        {'speaker': 'Agent:', 'message': 'How can I help?', 'class': 'agent-message'},
        {'speaker': 'Customer:', 'message': 'I need assistance', 'class': 'customer-message'}
    ]
    assert processed_transcript == expected_transcript