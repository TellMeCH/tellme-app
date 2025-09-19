import pytz
import pytest
from django.urls import reverse
from rest_framework import status
from tellme.call_miner.models import Organization, Conversation, Topic
from datetime import datetime, timedelta
import zoneinfo


@pytest.mark.django_db
class TestOrganizationList:
    """Tests for the organization-list endpoint"""
    def test_superuser_can_list_organizations(self, client, superuser):
        """Test that a superuser can list all organizations."""
        client.force_authenticate(user=superuser)
        url = reverse('organization-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0  # Check that organizations are returned

    def test_analyst_cannot_list_all_organizations(self, client, analyst_user):
        """Test that a regular analyst cannot list all organizations."""
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_list_all_organizations(self, client, agent_user):
        """Test that an agent cannot list all organizations."""
        client.force_authenticate(user=agent_user)
        url = reverse('organization-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_another_organization_analyst_cannot_list_organizations(self, client, another_organization_analyst_user):
        """Test that an analyst from another organization cannot list organizations."""
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('organization-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_list_all_organizations(self, client, agent_user):
        """Test that an unauthenticated user cannot list all organizations."""
        client.force_authenticate(user=agent_user)
        url = reverse('organization-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestOrganizationRetrieve:
    """Tests for the organization-detail API endpoint"""
    def test_superuser_can_retrieve_any_organization(self, client, superuser, organization, another_organization):
        """Test that a superuser can retrieve any organization."""
        client.force_authenticate(user=superuser)
        url = reverse('organization-detail', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse('organization-detail', args=[another_organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_analyst_can_retrieve_own_organization(self, client, analyst_user, organization):
        """Test that an analyst can retrieve their own organization."""
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-detail', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Test Organization'

    def test_analyst_cannot_retrieve_other_organization(self, client, analyst_user, another_organization):
        """Test that an analyst cannot retrieve another organization's details."""
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-detail', args=[another_organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_agent_cannot_retrieve_own_organization(self, client, agent_user, organization):
        """Test that an agent cannot retrieve their own organization's details."""
        client.force_authenticate(user=agent_user)
        url = reverse('organization-detail', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_retrieve_other_organization(self, client, agent_user, another_organization):
        """Test that an agent cannot retrieve another organization's details."""
        client.force_authenticate(user=agent_user)
        url = reverse('organization-detail', args=[another_organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_another_organization_analyst_cannot_retrieve_organization(self, client, another_organization_analyst_user,
                                                                       organization):
        """Test that an analyst from another organization cannot retrieve an organization's details."""
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('organization-detail', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_user_cannot_retrieve_organization(self, client, organization):
        """Test that an unauthenticated user cannot retrieve an organization's details."""
        url = reverse('organization-detail', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestOrganizationCreate:
    """Tests for the creation of new Organizations"""
    def test_superuser_can_create_organization(self, client, superuser):
        """Test that a superuser can create an organization."""
        client.force_authenticate(user=superuser)
        url = reverse('organization-list')
        data = {'name': 'New Organization', 'max_user_count': 20}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Organization.objects.filter(name='New Organization').exists()

    def test_analyst_cannot_create_organization(self, client, analyst_user):
        """Test that an analyst cannot create an organization."""
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-list')
        data = {'name': 'Unauthorized Organization', 'max_user_count': 20}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Organization.objects.filter(name='Unauthorized Organization').exists()

    def test_agent_cannot_create_organization(self, client, agent_user):
        """Test that an agent cannot create an organization."""
        client.force_authenticate(user=agent_user)
        url = reverse('organization-list')
        data = {'name': 'Unauthorized Organization', 'max_user_count': 20}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Organization.objects.filter(name='Unauthorized Organization').exists()

    def test_another_organization_analyst_cannot_create_organization(self, client, another_organization_analyst_user):
        """Test that an analyst from another organization cannot create an organization."""
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('organization-list')
        data = {'name': 'Unauthorized Creation', 'max_user_count': 20}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_create_organization(self, client):
        """Test that an unauthenticated user cannot create an organization."""
        url = reverse('organization-list')
        data = {'name': 'Unauthorized Organization', 'max_user_count': 20}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Organization.objects.filter(name='Unauthorized Organization').exists()


@pytest.mark.django_db
class TestOrganizationUpdate:
    """Tests for updating existing Organizations"""
    def test_superuser_can_update_organization(self, client, superuser, organization):
        """Test that a superuser can update an organization's details."""
        client.force_authenticate(user=superuser)
        url = reverse('organization-detail', args=[organization.id])
        data = {'name': 'Updated Organization', 'max_user_count': 15}
        response = client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        organization.refresh_from_db()
        assert organization.name == 'Updated Organization'
        assert organization.max_user_count == 15

    def test_analyst_cannot_update_organization(self, client, analyst_user, organization):
        """Test that an analyst cannot update an organization's details."""
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-detail', args=[organization.id])
        data = {'name': 'Unauthorized Update', 'max_user_count': 15}
        response = client.put(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_update_organization(self, client, agent_user, organization):
        """Test that an agent cannot update an organization's details."""
        client.force_authenticate(user=agent_user)
        url = reverse('organization-detail', args=[organization.id])
        data = {'name': 'Unauthorized Update', 'max_user_count': 15}
        response = client.put(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_another_organization_analyst_cannot_update_organization(self, client, another_organization_analyst_user,
                                                                     organization):
        """Test that an analyst from another organization cannot update an organization's details."""
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('organization-detail', args=[organization.id])
        data = {'name': 'Unauthorized Update', 'max_user_count': 20}
        response = client.put(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_update_organization(self, client, organization):
        """Test that an unauthenticated user cannot update an organization's details."""
        url = reverse('organization-detail', args=[organization.id])
        data = {'name': 'Unauthorized Update', 'max_user_count': 15}
        response = client.put(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestOrganizationDelete:
    """Tests for deleting existing Organizations"""
    def test_superuser_can_delete_organization(self, client, superuser, organization):
        """Test that a superuser can delete an organization."""
        client.force_authenticate(user=superuser)
        url = reverse('organization-detail', args=[organization.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Organization.objects.filter(id=organization.id).exists()

    def test_analyst_cannot_delete_organization(self, client, analyst_user, organization):
        """Test that an analyst cannot delete an organization."""
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-detail', args=[organization.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Organization.objects.filter(id=organization.id).exists()

    def test_agent_cannot_delete_organization(self, client, agent_user, organization):
        """Test that an agent cannot delete an organization."""
        client.force_authenticate(user=agent_user)
        url = reverse('organization-detail', args=[organization.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Organization.objects.filter(id=organization.id).exists()

    def test_another_organization_analyst_cannot_delete_organization(self, client, another_organization_analyst_user,
                                                                     organization):
        """Test that an analyst from another organization cannot delete an organization."""
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('organization-detail', args=[organization.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_delete_organization(self, client, organization):
        """Test that an unauthenticated user cannot delete an organization."""
        url = reverse('organization-detail', args=[organization.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Organization.objects.filter(id=organization.id).exists()


@pytest.mark.django_db
class TestOrganizationActions:
    """Tests for organization-conversations and all the trend-related API endpoints of an Organization"""
    def test_superuser_can_access_any_organization_conversations_action(self, client, superuser, organization,
                                                                        another_organization):
        """Test that a superuser can access the conversations of any organization."""
        client.force_authenticate(user=superuser)
        url = reverse('organization-conversations', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse('organization-conversations', args=[another_organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_analyst_can_access_own_organization_conversations_action(self, client, analyst_user,
                                                                      organization,
                                                                      conversation):
        """Test that an analyst can access the conversations of their own organization."""
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-conversations', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_analyst_cannot_access_other_organization_conversations_action(self, client, analyst_user,
                                                                           another_organization):
        """Test that an analyst cannot access the conversations of another organization."""
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-conversations', args=[another_organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_agent_cannot_access_own_organization_conversations_action(self, client, agent_user, organization):
        """Test that an agent cannot access the conversations of their own organization."""
        client.force_authenticate(user=agent_user)
        url = reverse('organization-conversations', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_access_other_organization_conversations_action(self, client, agent_user,
                                                                         another_organization):
        """Test that an agent cannot access the conversations of another organization."""
        client.force_authenticate(user=agent_user)
        url = reverse('organization-conversations', args=[another_organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_another_organization_analyst_cannot_access_other_organization_conversations_action(
            self,
            client,
            another_organization_analyst_user,
            organization):
        """
        Test that an analyst from another organization cannot access the conversations of a different organization.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('organization-conversations', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_user_cannot_access_conversations_action(self, client, organization):
        """Test that an unauthenticated user cannot access an organization's conversations."""
        url = reverse('organization-conversations', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_superuser_can_access_any_organization_trends_actions(self, client, superuser, organization,
                                                                  another_organization):
        """Test that a superuser can access the trend actions of any organization."""
        client.force_authenticate(user=superuser)
        url = reverse('organization-trend')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        for org in [organization, another_organization]:
            assert org.id in response.data

    def test_analyst_can_access_own_organization_trends_actions(self, client, analyst_user, organization,
                                                                another_organization):
        """Test that an analyst can access the trend actions of their own organization."""
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-trend')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert organization.id in response.data
        assert another_organization.id not in response.data

    def test_agent_cannot_access_own_organization_trends_actions(self, client, agent_user, organization):
        """Test that an agent cannot access the trend actions of their own organization."""
        client.force_authenticate(user=agent_user)
        url = reverse('organization-trend')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_another_organization_analyst_cannot_access_other_organization_trends_actions(
            self,
            client,
            another_organization_analyst_user,
            organization
    ):
        """
        Test that an analyst from another organization cannot access the trend actions of a different organization.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('organization-trend')
        response = client.get(url)
        assert organization.id not in response.data

    def test_unauthenticated_user_cannot_access_trends_actions(self, client, organization):
        """Test that an unauthenticated user cannot access an organization's trend actions."""
        url = reverse('organization-trend')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_superuser_can_access_any_organization_overview_actions(self, client, superuser, organization,
                                                                  another_organization):
        """Test that a superuser can access the overview actions of any organization."""
        client.force_authenticate(user=superuser)
        url = reverse('organization-overview')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        for org in [organization, another_organization]:
            assert org.id in response.data

    def test_analyst_can_access_own_organization_overview_actions(self, client, analyst_user, organization,
                                                                another_organization):
        """Test that an analyst can access the overview actions of their own organization."""
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-overview')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert organization.id in response.data
        assert another_organization.id not in response.data

    def test_agent_cannot_access_own_organization_overview_actions(self, client, agent_user, organization):
        """Test that an agent cannot access the overview actions of their own organization."""
        client.force_authenticate(user=agent_user)
        url = reverse('organization-overview')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_another_organization_analyst_cannot_access_other_organization_overview_actions(
            self,
            client,
            another_organization_analyst_user,
            organization
    ):
        """
        Test that an analyst from another organization cannot access the overview actions of a different organization.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('organization-overview')
        response = client.get(url)
        assert organization.id not in response.data

    def test_unauthenticated_user_cannot_access_overview_actions(self, client, organization):
        """Test that an unauthenticated user cannot access an organization's overview actions."""
        url = reverse('organization-overview')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_conversations_action_returns_correct_data(self, client, analyst_user, organization,
                                                       conversation):
        """Check the content of an organization's conversations."""
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-conversations', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
        conversations = data['results']
        assert len(conversations) == 1
        assert conversations[0]['title'] == conversation.title
        assert conversations[0]['date'].replace('Z', '') == conversation.date.strftime('%Y-%m-%dT%H:%M:%S')

    def test_conversations_action_pagination(self, client, analyst_user, organization, agent, customer):
        """Check that pagination works when calling organization-conversations."""
        # Create multiple conversations to test pagination
        for i in range(15):
            Conversation.objects.create(
                path=f'path/to/conversation_{i}',
                date=datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC) - timedelta(days=i),
                duration=100 + i,
                title=f'Test title {i}',
                summary=f'Test summary {i}',
                transcript=f'Test transcript {i}',
                sentiment=1.5 + i * 0.1,
                agent=agent,
                customer=customer,
                input_tokens=100 + i,
                output_tokens=50 + i
            )
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-conversations', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        conversations = data['results']
        assert len(conversations) == 15
        assert 'next' in data

    def test_conversation_trend_action_returns_correct_data(self, client, analyst_user, organization,
                                                            agent,
                                                            customer):
        """Check that the daily conversation trend responds as expected to the different period specifications."""
        # Create conversations on different days
        for i in range(5):
            Conversation.objects.create(
                path=f'path/to/conversation_{i}',
                date=datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC) - timedelta(days=i),
                duration=100 + i,
                title=f'Test title {i}',
                summary=f'Test summary {i}',
                transcript=f'Test transcript {i}',
                sentiment=1.5 + i * 0.1,
                agent=agent,
                customer=customer,
                input_tokens=100 + i,
                output_tokens=50 + i
            )
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-trend')
        response = client.get(url, {'trend_period': 'daily'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json().get(str(organization.id))
        assert 'results' in data
        results = data['results']
        assert len(results) == 5  # One entry per day
        for entry in results:
            assert 'date' in entry
            assert 'count' in entry
            assert entry['count'] == 1

    def test_conversation_topic_trend_action_returns_correct_data(self, client, analyst_user, organization,
                                                                  agent,
                                                                  customer):
        """Check that the organization's topic trends are as expected."""
        # Create topics
        topic1 = Topic.objects.create(name='Topic 1', description='Description 1', organization=organization)
        topic2 = Topic.objects.create(name='Topic 2', description='Description 2', organization=organization)
        # Create conversations with topics
        for i in range(5):
            conv = Conversation.objects.create(
                path=f'path/to/conversation_{i}',
                date=datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC) - timedelta(days=i),
                duration=100 + i,
                title=f'Test title {i}',
                summary=f'Test summary {i}',
                transcript=f'Test transcript {i}',
                sentiment=1.5 + i * 0.1,
                agent=agent,
                customer=customer,
                input_tokens=100 + i,
                output_tokens=50 + i
            )
            if i % 2 == 0:
                conv.topics.add(topic1)
            else:
                conv.topics.add(topic2)
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-trend')
        response = client.get(url, {'trend_period': 'daily', 'per_topic': 'true'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json().get(str(organization.id))
        assert 'results' in data
        results = data['results']
        assert len(results) == 5  # One entry per day per topic
        for entry in results:
            assert 'date' in entry
            assert 'topic_name' in entry
            assert 'topic_id' in entry
            assert 'count' in entry
            assert entry['count'] == 1
            assert entry['topic_name'] in ['Topic 1', 'Topic 2']

    def test_duration_trend_action_returns_correct_data(self, client, analyst_user, organization, agent,
                                                        customer):
        """Check that the duration trend of the organization returns the expected results."""
        # Create conversations with varying durations
        for i in range(5):
            Conversation.objects.create(
                path=f'path/to/conversation_{i}',
                date=datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC) - timedelta(days=i),
                duration=100 + i * 10,
                title=f'Test title {i}',
                summary=f'Test summary {i}',
                transcript=f'Test transcript {i}',
                sentiment=3.5,
                agent=agent,
                customer=customer,
                input_tokens=100,
                output_tokens=50
            )
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-trend')
        response = client.get(url, {'trend_period': 'daily'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json().get(str(organization.id))
        assert 'results' in data
        results = data['results']
        assert len(results) == 5
        for entry in results:
            assert 'date' in entry
            assert 'avg_duration' in entry
            assert entry['avg_duration'] in [100.0, 110.0, 120.0, 130.0, 140.0]

    def test_sentiment_trend_action_returns_correct_data(self, client, analyst_user, organization, agent,
                                                         customer):
        """Check that the sentiment trend of the organization returns the expected results."""
        # Create conversations with varying sentiments
        for i in range(5):
            Conversation.objects.create(
                path=f'path/to/conversation_{i}',
                date=datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC) - timedelta(days=i),
                duration=100,
                title=f'Test title {i}',
                summary=f'Test summary {i}',
                transcript=f'Test transcript {i}',
                sentiment=1 * i,
                agent=agent,
                customer=customer,
                input_tokens=100,
                output_tokens=50
            )
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-trend')
        response = client.get(url, {'trend_period': 'daily', 'field': 'sentiment'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json().get(str(organization.id))
        assert 'results' in data
        results = data['results']
        assert len(results) == 5
        for entry in results:
            assert 'date' in entry
            assert 'avg_sentiment' in entry

    def test_trend_actions_invalid_trend_period(self, client, analyst_user, organization):
        """Test that an error is raised whenever an incorrect trend period is specified."""
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-trend')
        response = client.get(url, {'trend_period': 'invalid_period'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_conversation_trend_action_weekly_period(self, client, analyst_user, organization, agent,
                                                     customer):
        """Test the conversation trend action when a weekly period is specified."""
        # Create conversations over several weeks
        for i in range(21):  # 3 weeks
            Conversation.objects.create(
                path=f'path/to/conversation_{i}',
                date=datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC) + timedelta(days=i),
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
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-trend')
        response = client.get(url, {'trend_period': 'weekly'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json().get(str(organization.id))
        results = data['results']
        assert len(results) == 3  # Three weeks
        for entry in results:
            assert 'date' in entry
            assert 'count' in entry

    def test_conversation_trend_action_monthly_period(self, client, analyst_user, organization, agent,
                                                      customer):
        """Test the conversation trend action when a monthly period is specified."""
        # Create conversations over several months
        for i in range(90):  # 3 months
            Conversation.objects.create(
                path=f'path/to/conversation_{i}',
                date=datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC) + timedelta(days=i),
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
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-trend')
        response = client.get(url, {'trend_period': 'monthly'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json().get(str(organization.id))
        results = data['results']
        assert len(results) == 3
        for entry in results:
            assert 'date' in entry
            assert 'count' in entry

    def test_duration_trend_action_weekly_period(self, client, analyst_user, organization, agent,
                                                 customer):
        """Test the duration trend action when a weekly period is specified."""
        # Create conversations over several weeks
        for i in range(21):  # 3 weeks
            Conversation.objects.create(
                path=f'path/to/conversation_{i}',
                date=datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC) + timedelta(days=i),
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
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-trend')
        response = client.get(url, {'trend_period': 'weekly', 'field': 'duration'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json().get(str(organization.id))
        results = data['results']
        assert len(results) == 3
        for entry in results:
            assert 'date' in entry
            assert 'avg_duration' in entry

    def test_duration_trend_action_monthly_period(self, client, analyst_user, organization, agent,
                                                  customer):
        """Test the duration trend action when a monthly period is specified."""
        # Create conversations over several months
        for i in range(90):  # Approx 3 months
            Conversation.objects.create(
                path=f'path/to/conversation_{i}',
                date=datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC) + timedelta(days=i),
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
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-trend')
        response = client.get(url, {'trend_period': 'monthly'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json().get(str(organization.id))
        results = data['results']
        assert len(results) == 3  # Three months
        for entry in results:
            assert 'date' in entry
            assert 'avg_duration' in entry

    def test_sentiment_trend_action_weekly_period(self, client, analyst_user, organization, agent,
                                                  customer):
        """Test the sentiment trend action when a weekly period is specified."""
        # Create conversations over several weeks
        for i in range(21):  # 3 weeks
            Conversation.objects.create(
                path=f'path/to/conversation_{i}',
                date=datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC) + timedelta(days=i),
                duration=100 + i,
                title=f'Test title {i}',
                summary=f'Test summary {i}',
                transcript=f'Test transcript {i}',
                sentiment=2.5,
                agent=agent,
                customer=customer,
                input_tokens=100,
                output_tokens=50
            )
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-trend')
        response = client.get(url, {'trend_period': 'weekly', 'field': 'sentiment'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json().get(str(organization.id))
        results = data['results']
        assert len(results) == 3
        for entry in results:
            assert 'date' in entry
            assert 'avg_sentiment' in entry

    def test_sentiment_trend_action_monthly_period(self, client, analyst_user, organization, agent,
                                                   customer):
        """Test the sentiment trend action when a monthly period is specified."""
        # Create conversations over several months
        for i in range(90):  # Approx 3 months
            Conversation.objects.create(
                path=f'path/to/conversation_{i}',
                date=datetime(2024, 1, 1, 0, 0, 0, tzinfo=pytz.UTC) + timedelta(days=i),
                duration=100 + i,
                title=f'Test title {i}',
                summary=f'Test summary {i}',
                transcript=f'Test transcript {i}',
                sentiment=2.5,
                agent=agent,
                customer=customer,
                input_tokens=100,
                output_tokens=50
            )
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-trend')
        response = client.get(url, {'trend_period': 'monthly'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json().get(str(organization.id))
        results = data['results']
        assert len(results) == 3  # Three months
        for entry in results:
            assert 'date' in entry
            assert 'avg_sentiment' in entry

    def test_overview_action_returns_correct_data(self, client, analyst_user, organization,
                                                            agent,
                                                            customer):
        """Check that the overview action responds as expected."""
        # Create conversations on different days
        utc = zoneinfo.ZoneInfo("UTC")
        topic1 = Topic.objects.create(name='Topic 1', description='Description 1', organization=organization)
        for i in range(5):
            conv = Conversation.objects.create(
                path=f'path/to/conversation_{i}',
                date=datetime.now(tz=utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i),
                duration=100 + i,
                title=f'Test title {i}',
                summary=f'Test summary {i}',
                transcript=f'Test transcript {i}',
                sentiment=1.5 + i * 0.1,
                agent=agent,
                customer=customer,
                input_tokens=100 + i,
                output_tokens=50 + i
            )
            conv.topics.add(topic1)
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-overview')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data = response.json().get(str(organization.id)).get('general')
        for kpi in ['avg_sentiment', 'avg_duration', 'count', 'most_popular_topic']:
            assert kpi in data
        assert 'Topic 1' in data['most_popular_topic'].values()

    def test_overview_action_per_topic_returns_correct_data(self, client, analyst_user, organization,
                                                                  agent,
                                                                  customer):
        """Check that the organization's overview action returns as expected."""
        # Create topics
        topic1 = Topic.objects.create(name='Topic 1', description='Description 1', organization=organization)
        topic2 = Topic.objects.create(name='Topic 2', description='Description 2', organization=organization)
        topic3 = Topic.objects.create(name='Topic 3', description='Unused', organization=organization)
        # Create conversations with topics
        utc = zoneinfo.ZoneInfo("UTC")
        for i in range(5):
            conv_date = (
                    datetime.now(tz=utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0) -
                    timedelta(days=i + 1)
            )
            conv = Conversation.objects.create(
                path=f'path/to/conversation_{i}',
                date=conv_date,
                duration=100 + i,
                title=f'Test title {i}',
                summary=f'Test summary {i}',
                transcript=f'Test transcript {i}',
                sentiment=1.5 + i * 0.1,
                agent=agent,
                customer=customer,
                input_tokens=100 + i,
                output_tokens=50 + i
            )
            if i > 2:  # Ensure topic2 appears more than topic1
                conv.topics.add(topic1)
            else:
                conv.topics.add(topic2)
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-overview')
        response = client.get(url, {'per_topic': True})
        assert response.status_code == status.HTTP_200_OK
        data = response.json().get(str(organization.id))
        assert len(data) == 2  # One entry per topic, topic3 omitted
        assert list(data.keys())[0] == topic2.name  # Ensure ordering by descending popularity
        for topic_name, entry in data.items():
            for kpi in ['avg_sentiment', 'avg_duration', 'count']:
                assert kpi in entry
            assert topic_name in [topic1.name, topic2.name]
            assert topic_name != topic3.name

    def test_conversations_action_no_data(self, client, analyst_user, organization):
        """Test that the conversations action can return an empty result when no conversations are present."""
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-conversations', args=[organization.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'results' in data
        assert data['results'] == []

    def test_trends_actions_no_data(self, client, analyst_user, organization):
        """Test that the conversation trend actions can return an empty result when no conversations are present."""
        client.force_authenticate(user=analyst_user)
        url = reverse('organization-trend')
        response = client.get(url, {'trend_period': 'daily'})
        assert response.status_code == status.HTTP_200_OK
        data = response.json().get(str(organization.id))
        assert 'results' in data
        assert data['results'] == []
