import pytest
from unittest.mock import patch, Mock, MagicMock
import uuid
import zoneinfo
from rest_framework.test import APIClient
from datetime import timedelta, datetime
from tellme.call_miner.models import (
    Organization, Analyst, Agent, Customer, Conversation, Topic, SuggestedTopic, User, Employee, OrganizationAPIKey
)


@pytest.fixture(autouse=True)
def mock_firebase_auth():
    """Mock firebase_admin.auth methods to prevent real Firebase interactions during tests."""
    with patch('firebase_admin.auth.create_user') as mock_create_user, \
         patch('firebase_admin.auth.delete_user') as mock_delete_user, \
         patch('firebase_admin.auth.get_user_by_email') as mock_get_user_by_email:

        # Mock create_user to return a mock user with a unique UID
        def create_user_side_effect(*args, **kwargs):
            mock_user = Mock()
            mock_user.uid = str(uuid.uuid4())
            return mock_user
        mock_create_user.side_effect = create_user_side_effect

        # Mock delete_user to do nothing
        mock_delete_user.return_value = None

        # Mock get_user_by_email to return a mock user with a fixed UID
        def get_user_by_email_side_effect(email):
            mock_user = Mock()
            mock_user.uid = f"mocked-uid-for-{email}"
            return mock_user
        mock_get_user_by_email.side_effect = get_user_by_email_side_effect

        yield


@pytest.fixture(autouse=True)
def mock_condense_summaries():
    """
    Mocking the call to OpenAI API for re-summarization. Making it autouse to avoid any unexpected costs.
    """
    with patch('tellme.call_miner.models.condense_summaries') as mock:
        mock.return_value = {'Reasons for Calling': 'Billing issues and account setup inquiries are common.'}
        yield mock


@pytest.fixture(autouse=True)
def mock_user_email_sending():
    """
    Mocks out User's send_onboarding_email() and send_verification_email()
    methods so that no real email logic is triggered.
    """
    with patch('tellme.call_miner.models.User.send_onboarding_email') as mock_onboarding, \
         patch('tellme.call_miner.models.User.send_verification_email') as mock_verification:
        # You can further control return values or side effects if needed.
        mock_onboarding.return_value = None
        mock_verification.return_value = None

        yield mock_onboarding, mock_verification


@pytest.fixture
def client():
    """Return an instance of the DRF APIClient for testing."""
    return APIClient()


@pytest.fixture
def organization():
    """Create and return a test Organization."""
    return Organization.objects.create(
        name='Test Organization',
        max_user_count=10,
        revenue_search_prefix='testorg.ch/de/'
    )


@pytest.fixture
def api_key(organization):
    """Create and return a test Organization API Key"""
    _ = OrganizationAPIKey.create_key(organization, 'test_key')
    return organization.api_keys.get(name='test_key')


@pytest.fixture
def another_organization():
    """Create and return another test Organization."""
    return Organization.objects.create(
        name='Another Organization',
        max_user_count=10,
        revenue_search_prefix='anotherorga.ch/de/'
    )


@pytest.fixture
def user():
    return User.objects.create_user(
        first_name="test",
        last_name="user",
        email="testuser@acme.org",
        auth_type="password"
    )


@pytest.fixture
def another_user():
    return User.objects.create_user(
        first_name="another",
        last_name="user",
        email="anotheruser@acme.org",
        auth_type="password"
    )


@pytest.fixture
def superuser():
    """Create and return a superuser for testing."""
    user = User.objects.create_superuser('superuser@example.com', 'superpassword', 'super', 'user')
    return user


@pytest.fixture
def organization_admin_user(organization):
    """Create and return an organization admin user associated with the given organization."""
    user = User.objects.create_user('orgadmin@example.com', 'password', 'organization', 'admin')
    Analyst.objects.create(user=user, organization=organization, is_organization_admin=True)
    return user


@pytest.fixture
def another_organization_admin_user(another_organization):
    """Create and return an organization admin in another organization."""
    user = User.objects.create_user('another_orgadmin@example.com', 'password', 'another', 'orgadmin')
    Employee.objects.create(user=user, organization=another_organization, is_organization_admin=True)
    return user


@pytest.fixture
def analyst_user(organization):
    """Create and return an analyst user associated with the given organization."""
    user = User.objects.create_user('analyst@example.com', 'password', 'analyst', 'example')
    Analyst.objects.create(user=user, organization=organization, is_organization_admin=False)
    return user


@pytest.fixture
def another_organization_analyst_user(another_organization):
    """Create and return an analyst user associated with another organization."""
    user = User.objects.create_user('another_analyst@example.com', 'password', 'another', 'analyst')
    Analyst.objects.create(user=user, organization=another_organization, is_organization_admin=False)
    return user


@pytest.fixture
def agent(organization):
    """Create and return an agent associated with the given organization."""
    user = User.objects.create_user('agent@example.com', 'password', 'agent', 'example')
    agent = Agent.objects.create(user=user, organization=organization)
    return agent


@pytest.fixture
def agent_user(organization):
    """Create and return an agent associated with the given organization."""
    user = User.objects.create_user('agent_user@example.com', 'password', 'agent', 'user')
    Agent.objects.create(user=user, organization=organization)
    return user


@pytest.fixture
def agent_manager_user(organization):
    """Create and return an agent manager and an agent managed by them."""
    manager_user = User.objects.create_user('manager@example.com', 'password', 'manager', 'example')
    manager = Agent.objects.create(user=manager_user, organization=organization, is_organization_admin=False)
    agent_user = User.objects.create_user('agent2@example.com', 'password', 'agent2', 'example')
    Agent.objects.create(user=agent_user, organization=organization, is_organization_admin=False, manager=manager)
    return manager_user


@pytest.fixture
def another_organization_agent(another_organization):
    """Create and return an agent associated with another organization."""
    user = User.objects.create_user('another_agent@example.com', 'password', 'another', 'agent')
    agent = Agent.objects.create(user=user, organization=another_organization)
    return agent


@pytest.fixture
def another_organization_agent_user(another_organization):
    """Create and return an agent in another organization."""
    user = User.objects.create_user('another_org_employee@example.com', 'password', 'another', 'employee')
    Employee.objects.create(user=user, organization=another_organization, is_organization_admin=False, role='AGENT')
    return user


@pytest.fixture
def customer(organization):
    """Create and return a customer associated with the given organization."""
    return Customer.objects.create(
        external_id='02ac34b094eed76ca56ffc826db3f9a4d7b3d8f337beefc33c342b0035fea0dd',
        organization=organization
    )


@pytest.fixture
def another_organization_customer(another_organization):
    """Create and return a customer associated with another organization."""
    return Customer.objects.create(
        external_id='104da9683b41c996e98eb89311009de7ae3ec2b07c41a52200eda8b0df6dfde9',
        organization=another_organization
    )


@pytest.fixture
def conversation(agent, customer, topic, suggested_topic):
    """Create and return a conversation between the given agent and customer."""
    utc = zoneinfo.ZoneInfo("UTC")
    conv_date = (
            datetime.now(tz=utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            - timedelta(days=15)
    )
    conv = Conversation.objects.create(
        path='path/to/conversation',
        date=conv_date,
        duration=123.45,
        title='Test Conversation',
        summary='Test summary',
        transcript=f"""
        <agent>: Hello, {agent.user.first_name} here. How can I assist you today?
        <customer>: Hi, I have an issue with my product. It's acting weird.
        <agent>: Could you describe the problem?
        <customer>: Yes, it keeps making a strange noise and flashing red lights.
        <agent>: That doesn't sound right. Let me look into that for you.
        <customer>: Thank you, it's driving me crazy!
        """ * 4,
        sentiment=4.5,
        starting_sentiment=3.0,
        ending_sentiment=5.0,
        agent=agent,
        customer=customer,
        input_tokens=100,
        output_tokens=50,
        revenue_at_stake=299.99,
        resolved=False
    )
    conv.topics.add(topic)
    conv.suggested_topics.add(suggested_topic)
    return conv


@pytest.fixture
def conversation_today(agent, customer, topic):
    """Create and return a conversation ocurring TODAY between the given agent and customer."""
    utc = zoneinfo.ZoneInfo("UTC")
    conv = Conversation.objects.create(
        path='path/to/conversation',
        date=datetime.now(tz=utc),
        duration=123.45,
        title='Test Conversation',
        summary='Test summary',
        transcript=f"""
        <agent>: Hello, {agent.user.first_name} here. How can I assist you today?
        <customer>: Hi, I have an issue with my product. It's acting weird.
        <agent>: Could you describe the problem?
        <customer>: Yes, it keeps making a strange noise and flashing red lights.
        <agent>: That doesn't sound right. Let me look into that for you.
        <customer>: Thank you, it's driving me crazy!
        """ * 4,
        sentiment=4.5,
        starting_sentiment=4.0,
        ending_sentiment=4.0,
        agent=agent,
        customer=customer,
        input_tokens=100,
        output_tokens=50,
        revenue_at_stake=199.50,
        resolved=False,
    )
    conv.topics.add(topic)
    return conv


@pytest.fixture
def another_organization_conversation(another_organization_agent, another_organization_customer,
                                      another_organization_topic):
    """Create and return another conversation between the given agent and customer."""
    utc = zoneinfo.ZoneInfo("UTC")
    conv_date = (
            datetime.now(tz=utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            - timedelta(days=15)
    )
    conv = Conversation.objects.create(
        path='path/to/another_conversation',
        date=conv_date,
        duration=123.45,
        title='Another Conversation',
        summary='Another summary',
        transcript='Another test transcript',
        sentiment=3.5,
        starting_sentiment=2.0,
        ending_sentiment=4.0,
        agent=another_organization_agent,
        customer=another_organization_customer,
        input_tokens=100,
        output_tokens=50,
        revenue_at_stake=149.75,
        resolved=False,
    )
    conv.topics.add(another_organization_topic)
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
def another_organization_topic(another_organization):
    """Create and return another topic associated with another organization."""
    return Topic.objects.create(
        name='Another Topic',
        description='Another test topic',
        organization=another_organization,
        is_active=True
    )


@pytest.fixture
def suggested_topic(organization):
    """Create and return a suggested topic associated with the given organization."""
    return SuggestedTopic.objects.create(
        name='Test Suggested Topic',
        description='A test suggested topic',
        organization=organization
    )


@pytest.fixture
def another_organization_suggested_topic(another_organization):
    """Create and return another suggested topic associated with another organization."""
    return SuggestedTopic.objects.create(
        name='Another Suggested Topic',
        description='Another test suggested topic',
        organization=another_organization
    )

