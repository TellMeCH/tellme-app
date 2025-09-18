import pytest
from datetime import datetime
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from apps.call_miner.models import Agent, User

TREND_ACTIONS = ['conversations', 'trend', 'overview']


@pytest.fixture
def agent_manager(organization):
    """Create and return an agent who is a manager in the organization."""
    user = User.objects.create_user('manager@example.com', 'password', 'agent', 'manager')
    agent = Agent.objects.create(user=user, organization=organization, role='AGENT')
    return agent


@pytest.fixture
def agent_managed_by_manager(organization, agent_manager):
    """Create and return an agent managed by agent_manager."""
    user = User.objects.create_user('managed_agent@example.com', 'password', 'managed', 'agent')
    agent = Agent.objects.create(user=user, organization=organization, role='AGENT', manager=agent_manager)
    return agent


@pytest.fixture
def another_agent_in_same_org(organization):
    """Create and return another agent in the same organization."""
    user = User.objects.create_user('another_agent_in_same_org@example.com', 'password', 'another', 'agent')
    agent = Agent.objects.create(user=user, organization=organization, role='AGENT')
    return agent


@pytest.mark.django_db
class TestAgentList:
    """Tests for the agent-list API endpoint"""

    def test_superuser_can_list_all_agents(self, client, superuser, agent, another_organization_agent):
        """
        Test that a superuser can list all agents across organizations.
        """
        client.force_authenticate(user=superuser)
        response = client.get(reverse('agent-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_organization_admin_can_list_agents(self, client, organization_admin_user, agent, agent_managed_by_manager):
        """
        Test that an organization admin can list agents in their own organization.
        """
        client.force_authenticate(user=organization_admin_user)
        response = client.get(reverse('agent-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_analyst_can_list_agents(self, client, analyst_user, agent, agent_managed_by_manager,
                                     another_organization_agent):
        """
        Test that an organization analyst can list agents in their own organization.
        """
        client.force_authenticate(user=analyst_user)
        response = client.get(reverse('agent-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_agent_can_list_agents_in_own_organization(self, client, agent_user, agent_managed_by_manager,
                                                       another_organization_agent):
        """
        Test that an agent can list agents in their own organization.
        """
        client.force_authenticate(user=agent_user)
        response = client.get(reverse('agent-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_another_organization_agent_cannot_list_agents_in_another_organization(self, client, agent,
                                                                                   agent_managed_by_manager,
                                                                                   another_organization_agent):
        """
        Test that an agent can list agents in their own organization.
        """
        client.force_authenticate(user=another_organization_agent.user)
        response = client.get(reverse('agent-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_unauthenticated_user_cannot_list_agents(self, client):
        """
        Test that an unauthenticated user cannot list agents.
        """
        response = client.get(reverse('agent-list'))
        assert response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAgentRetrieve:
    """Tests for the agent-detail API endpoint"""

    def test_superuser_can_retrieve_any_agent(self, client, superuser, agent, another_organization_agent):
        """
        Test that a superuser can retrieve any agent.
        """
        client.force_authenticate(user=superuser)
        url = reverse('agent-detail', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == agent.user.email

        url = reverse('agent-detail', args=[another_organization_agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == another_organization_agent.user.email

    def test_organization_admin_can_retrieve_other_agent_details(self, client, organization_admin_user, agent):
        """
        Test that an organization admin can retrieve an agent's details in their own organization.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('agent-detail', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == agent.user.email

    def test_organization_admin_cannot_retrieve_another_organization_agent_details(self, client,
                                                                                   organization_admin_user,
                                                                                   another_organization_agent):
        """
        Test that an organization admin cannot retrieve an agent's details in another organization.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('agent-detail', args=[another_organization_agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_organization_analyst_cannot_retrieve_other_agent_details(self, client, analyst_user, agent):
        """
        Test that an analyst cannot retrieve an agent's details in their own organization.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('agent-detail', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_manager_can_retrieve_managed_agent(self, client, agent_manager, agent_managed_by_manager):
        """
        Test that an agent manager can retrieve details of a managed agent.
        """
        client.force_authenticate(user=agent_manager.user)
        url = reverse('agent-detail', args=[agent_managed_by_manager.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == agent_managed_by_manager.user.email

    def test_agent_manager_cannot_retrieve_non_managed_agent(self, client, agent_manager, agent):
        """
        Test that an agent manager cannot retrieve details of a non-managed agent.
        """
        client.force_authenticate(user=agent_manager.user)
        url = reverse('agent-detail', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_can_retrieve_own_details(self, client, agent):
        """
        Test that an agent can retrieve their own details.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('agent-detail', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == agent.user.email

    def test_agent_cannot_retrieve_other_agent_details(self, client, agent_user, another_agent_in_same_org):
        """
        Test that an agent cannot retrieve another agent's details in their own organization.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('agent-detail', args=[another_agent_in_same_org.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_in_other_organization_cannot_retrieve_agent(self, client, another_organization_agent_user, agent):
        """
        Test that an agent in another organization cannot retrieve an agent.
        """
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('agent-detail', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_user_cannot_retrieve_agent(self, client, agent):
        """
        Test that an unauthenticated user cannot retrieve an agent.
        """
        url = reverse('agent-detail', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_conversation_stats(self, client, organization_admin_user, conversation, agent, customer, topic):
        """
        Test that the conversation stats for the agent are as expected
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('agent-detail', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "conversation_count" in response.data
        assert "first_conversation_date" in response.data
        assert "last_conversation_date" in response.data
        assert response.data.get("conversation_count") == 1
        assert response.data.get("first_conversation_date") == conversation.date.isoformat()[:-6] + 'Z'
        assert response.data.get("last_conversation_date") == conversation.date.isoformat()[:-6] + 'Z'


@pytest.mark.django_db
class TestAgentCreate:
    """Tests for the creation of new Agents"""

    def test_superuser_cannot_create_agent(self, client, superuser, organization):
        """
        Test that a superuser can't create an agent via the AgentViewSet.
        """
        client.force_authenticate(user=superuser)
        data = {
            'username': 'new_agent',
            'password': 'password',
            'organization': organization.id,
            'role': 'AGENT'
        }
        response = client.post(reverse('agent-list'), data=data)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_organization_admin_cannot_create_agent_in_own_organization(self, client, organization_admin_user,
                                                                        organization):
        """
        Test that an organization admin can't create an agent in their own organization via the AgentViewSet.
        """
        client.force_authenticate(user=organization_admin_user)
        data = {
            'username': 'new_agent',
            'password': 'password',
            'organization': organization.id,
            'role': 'AGENT'
        }
        response = client.post(reverse('agent-list'), data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_organization_admin_cannot_create_agent_in_another_organization(self, client, organization_admin_user,
                                                                            another_organization):
        """
        Test that an organization admin cannot create an agent in another organization.
        """
        client.force_authenticate(user=organization_admin_user)
        data = {
            'username': 'new_agent',
            'password': 'password',
            'organization': another_organization.id,
            'role': 'AGENT'
        }
        response = client.post(reverse('agent-list'), data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyst_cannot_create_agent(self, client, analyst_user, organization):
        """
        Test that an analyst cannot create an agent.
        """
        client.force_authenticate(user=analyst_user)
        data = {
            'username': 'new_agent',
            'password': 'password',
            'organization': organization.id,
            'role': 'AGENT'
        }
        response = client.post(reverse('agent-list'), data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_create_agent(self, client, agent_user, organization):
        """
        Test that an agent cannot create another agent.
        """
        client.force_authenticate(user=agent_user)
        data = {
            'username': 'new_agent',
            'password': 'password',
            'organization': organization.id,
            'role': 'AGENT'
        }
        response = client.post(reverse('agent-list'), data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_create_agent(self, client, agent, organization):
        """
        Test that an unauthenticated user cannot create an agent.
        """
        data = {
            'username': 'new_agent',
            'password': 'password',
            'organization': organization.id,
            'role': 'AGENT'
        }
        response = client.post(reverse('agent-list'), data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAgentUpdate:
    """Tests for updating Agents via the API"""

    def test_superuser_can_update_agent_manager(self, client, superuser, agent, agent_manager):
        """
        Test that a superuser cannot update an agent's manager via the AgentViewSet.
        """
        client.force_authenticate(user=superuser)
        data = {'manager': agent_manager.id}
        url = reverse('agent-detail', args=[agent.id])
        response = client.patch(url, data=data)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_organization_admin_cannot_update_agent_manager(self, client, organization_admin_user, agent,
                                                            agent_manager):
        """
        Test that an organization admin cannot update an agent's manager in their own organization via the AgentViewSet.
        """
        client.force_authenticate(user=organization_admin_user)
        data = {'manager': agent_manager.id}
        url = reverse('agent-detail', args=[agent.id])
        response = client.patch(url, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_organization_admin_cannot_update_agent_in_another_organization(self, client, organization_admin_user,
                                                                            another_organization_agent, agent_manager):
        """
        Test that an organization admin cannot update an agent in another organization.
        """
        client.force_authenticate(user=organization_admin_user)
        data = {'manager': agent_manager.id}
        url = reverse('agent-detail', args=[another_organization_agent.id])
        response = client.patch(url, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyst_cannot_update_agent(self, client, analyst_user, agent, agent_manager):
        """
        Test that an analyst cannot update an agent.
        """
        client.force_authenticate(user=analyst_user)
        data = {'manager': agent_manager.id}
        url = reverse('agent-detail', args=[agent.id])
        response = client.patch(url, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_update_another_agent(self, client, agent_user, another_agent_in_same_org, agent_manager):
        """
        Test that an agent cannot update another agent in their organization.
        """
        client.force_authenticate(user=agent_user)
        data = {'manager': agent_manager.id}
        url = reverse('agent-detail', args=[another_agent_in_same_org.id])
        response = client.patch(url, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_update_self_manager(self, client, agent, agent_manager):
        """
        Test that an agent cannot update their own manager.
        """
        client.force_authenticate(user=agent.user)
        data = {'manager': agent_manager.id}
        url = reverse('agent-detail', args=[agent.id])
        response = client.patch(url, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_update_agent(self, client, agent, agent_manager):
        """
        Test that an unauthenticated user cannot update an agent.
        """
        data = {'manager': agent_manager.id}
        url = reverse('agent-detail', args=[agent.id])
        response = client.patch(url, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAgentDelete:
    """Tests for deleting agents via the API"""

    def test_superuser_cannot_delete_agent(self, client, superuser, agent):
        """
        Test that a superuser can't delete an agent via the AgentViewSet.
        """
        client.force_authenticate(user=superuser)
        url = reverse('agent-detail', args=[agent.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_organization_admin_cannot_delete_agent(self, client, organization_admin_user, agent):
        """
        Test that an organization admin can't delete an agent in their own organization via the AgentViewSet.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('agent-detail', args=[agent.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_organization_admin_cannot_delete_agent_in_another_organization(self, client, organization_admin_user,
                                                                            another_organization_agent):
        """
        Test that an organization admin cannot delete an agent in another organization.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('agent-detail', args=[another_organization_agent.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyst_cannot_delete_agent(self, client, analyst_user, agent):
        """
        Test that an analyst cannot delete an agent.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('agent-detail', args=[agent.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_delete_another_agent(self, client, agent_user, another_agent_in_same_org):
        """
        Test that an agent cannot delete another agent in their own organization.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('agent-detail', args=[another_agent_in_same_org.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_delete_agent(self, client, agent):
        """
        Test that an unauthenticated user cannot delete an agent.
        """
        url = reverse('agent-detail', args=[agent.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestAgentTrendActions:
    """Tests for retrieving activity trends of each Agent"""

    @staticmethod
    def _test_trend_action(client, url, expected_status):
        """
        Helper function to test trend actions.
        """
        response = client.get(url)
        assert response.status_code == expected_status

    def test_superuser_can_access_agent_trend_actions(self, client, superuser, agent):
        """
        Test that a superuser can access all trend actions for any agent.
        """
        client.force_authenticate(user=superuser)
        for action in TREND_ACTIONS:
            url = reverse(f'agent-{action}', args=[agent.id])
            self._test_trend_action(client, url, status.HTTP_200_OK)

    def test_organization_admin_can_access_agent_trend_actions(self, client, organization_admin_user, agent):
        """
        Test that an organization admin can access trend actions for agents.
        """
        client.force_authenticate(user=organization_admin_user)
        for action in TREND_ACTIONS:
            url = reverse(f'agent-{action}', args=[agent.id])
            self._test_trend_action(client, url, status.HTTP_200_OK)

    def test_organization_admin_cannot_access_another_organization_agent_trend_actions(self, client,
                                                                                       organization_admin_user,
                                                                                       another_organization_agent):
        """
        Test that an organization admin cannot access trend actions for agents in other organizations.
        """
        client.force_authenticate(user=organization_admin_user)
        for action in TREND_ACTIONS:
            url = reverse(f'agent-{action}', args=[another_organization_agent.id])
            self._test_trend_action(client, url, status.HTTP_404_NOT_FOUND)

    def test_organization_analyst_cannot_access_agent_trend_actions(self, client, analyst_user, agent):
        """
        Test that an analyst cannot access trend actions for agents.
        """
        client.force_authenticate(user=analyst_user)
        for action in TREND_ACTIONS:
            url = reverse(f'agent-{action}', args=[agent.id])
            self._test_trend_action(client, url, status.HTTP_403_FORBIDDEN)

    def test_agent_manager_can_access_managed_agent_trend_actions(self, client, agent_manager,
                                                                  agent_managed_by_manager):
        """
        Test that an agent manager can access trend actions for managed agents.
        """
        client.force_authenticate(user=agent_manager.user)
        for action in TREND_ACTIONS:
            url = reverse(f'agent-{action}', args=[agent_managed_by_manager.id])
            self._test_trend_action(client, url, status.HTTP_200_OK)

    def test_agent_manager_cannot_access_non_managed_agent_trend_actions(self, client, agent_manager_user, agent):
        """
        Test that an agent manager cannot access trend actions for managed agents.
        """
        client.force_authenticate(user=agent_manager_user)
        for action in TREND_ACTIONS:
            url = reverse(f'agent-{action}', args=[agent.id])
            self._test_trend_action(client, url, status.HTTP_403_FORBIDDEN)

    def test_agent_can_access_own_trend_actions(self, client, agent):
        """
        Test that an agent can access trend actions for themselves.
        """
        client.force_authenticate(user=agent.user)
        for action in TREND_ACTIONS:
            url = reverse(f'agent-{action}', args=[agent.id])
            self._test_trend_action(client, url, status.HTTP_200_OK)

    def test_agent_cannot_access_other_agent_trend_actions(self, client, agent_user, another_agent_in_same_org):
        """
        Test that an agent cannot access trend actions for other agents in the same organization.
        """
        client.force_authenticate(user=agent_user)
        for action in TREND_ACTIONS:
            url = reverse(f'agent-{action}', args=[another_agent_in_same_org.id])
            self._test_trend_action(client, url, status.HTTP_403_FORBIDDEN)

    def test_agent_in_other_organization_cannot_access_agent_trend_actions(self, client,
                                                                           another_organization_agent_user, agent):
        """
        Test that an agent in another organization cannot access trend actions for an agent.
        """
        client.force_authenticate(user=another_organization_agent_user)
        for action in TREND_ACTIONS:
            url = reverse(f'agent-{action}', args=[agent.id])
            self._test_trend_action(client, url, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_access_agent_trend_actions(self, client, agent):
        """
        Test that an unauthenticated user cannot access trend actions for an agent.
        """
        for action in TREND_ACTIONS:
            url = reverse(f'agent-{action}', args=[agent.id])
            self._test_trend_action(client, url, status.HTTP_403_FORBIDDEN)

    def test_agent_conversations_action_returns_expected_content(self, client, agent, conversation):
        """
        Test that the 'conversations' action for an agent retrieves the expected conversation data.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('agent-conversations', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['title'] == conversation.title

    def test_agent_conversation_trend_action_returns_expected_content(self, client, agent, conversation):
        """
        Test that the 'trend' action for an agent retrieves the expected conversation count data.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('agent-trend', args=[agent.id])
        response = client.get(url, {'trend_period': 'daily', 'field': 'count'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['count'] == 1
        assert results[0]['date'] == conversation.date

    def test_agent_conversation_topic_trend_action_returns_expected_content(self, client, agent, conversation):
        """
        Test that the 'trend' action for an agent retrieves the expected conversation count data per topic.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('agent-trend', args=[agent.id])
        response = client.get(url, {'trend_period': 'daily', 'field': 'count', 'per_topic': 'true'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['count'] == 1
        assert results[0]['date'] == conversation.date
        assert results[0]['topic_name'] == str(conversation.topics.all()[0])
        assert 'topic_id' in results[0]

    def test_agent_duration_trend_action_returns_expected_content(self, client, agent, conversation):
        """
        Test that the 'trend' action for an agent retrieves the expected duration trend data.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('agent-trend', args=[agent.id])
        response = client.get(url, {'trend_period': 'daily', 'field': 'duration'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['avg_duration'] == conversation.duration

    def test_agent_sentiment_trend_action_returns_expected_content(self, client, agent, conversation):
        """
        Test that the 'trend' action for an agent retrieves the expected sentiment trend data.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('agent-trend', args=[agent.id])
        response = client.get(url, {'trend_period': 'daily', 'field': 'sentiment'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['avg_sentiment'] == conversation.sentiment

    def test_agent_sentiment_per_topic_trend_action_returns_expected_content(self, client, agent, conversation):
        """
        Test that the 'trend' action for an agent retrieves the expected sentiment trend data per topic.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('agent-trend', args=[agent.id])
        response = client.get(url, {'trend_period': 'daily', 'field': 'sentiment', 'per_topic': 'true'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['avg_sentiment'] == conversation.sentiment
        assert results[0]['topic_name'] == str(conversation.topics.all()[0])
        assert 'topic_id' in results[0]

    def test_agent_overview_action_returns_expected_content(self, client, agent, conversation):
        """
        Test that the 'overview' action for an agent retrieves the expected conversation count data.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('agent-overview', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'general' in response.data
        results = response.data['general']
        for kpi in ['avg_sentiment', 'avg_duration', 'count', 'most_popular_topic']:
            assert kpi in results

    def test_agent_overview_per_topic_action_returns_expected_content(self, client, agent, conversation):
        """
        Test that the 'trend' action for an agent retrieves the expected conversation count data per topic.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('agent-overview', args=[agent.id])
        response = client.get(url, {'per_topic': 'true'})
        assert response.status_code == status.HTTP_200_OK
        assert str(conversation.topics.all()[0]) in response.data
        results = response.data[str(conversation.topics.all()[0])]
        for kpi in ['avg_sentiment', 'avg_duration', 'count']:
            assert kpi in results


@pytest.mark.django_db
class TestAgentSummary:
    """Tests for retrieving conversation summaries of each agent"""

    def test_superuser_can_access_agent_summary_data(self, client, superuser, agent):
        """
        Test that a superuser can access the summary data of any agent.
        """
        client.force_authenticate(user=superuser)
        url = reverse('agent-summary-data', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_organization_admin_can_access_agent_summary_data(self, client, organization_admin_user, agent):
        """
        Test that an organization admin can access the summary data of an agent.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('agent-summary-data', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_organization_admin_cannot_access_another_organization_agent_summary_data(self, client,
                                                                                      organization_admin_user,
                                                                                      another_organization_agent):
        """
        Test that an organization admin cannot access the summary data of an agent in another organization.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('agent-summary-data', args=[another_organization_agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_organization_analyst_cannot_access_agent_summary_data(self, client, analyst_user, agent):
        """
        Test that an analyst cannot access the summary data of an agent.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('agent-summary-data', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_manager_can_access_managed_agent_summary_data(self, client, agent_manager, agent_managed_by_manager):
        """
        Test that an agent manager can access the summary data of managed agents.
        """
        client.force_authenticate(user=agent_manager.user)
        url = reverse('agent-summary-data', args=[agent_managed_by_manager.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_agent_manager_cannot_access_non_managed_agent_summary_data(self, client, agent_manager, agent):
        """
        Test that an agent manager cannot access the summary data of non-managed agents.
        """
        client.force_authenticate(user=agent_manager.user)
        url = reverse('agent-summary-data', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_can_access_own_summary_data(self, client, agent):
        """
        Test that an agent can access their own summary data.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('agent-summary-data', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_agent_cannot_access_other_agent_summary_data(self, client, agent_user, another_agent_in_same_org):
        """
        Test that an agent cannot access the summary data of other agents in the same organization.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('agent-summary-data', args=[another_agent_in_same_org.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_in_other_organization_cannot_access_agent_summary_data(self, client,
                                                                          another_organization_agent_user, agent):
        """
        Test that an agent in another organization cannot access the summary data of an agent.
        """
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('agent-summary-data', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_user_cannot_access_agent_summary_data(self, client, agent):
        """
        Test that an unauthenticated user cannot access the summary data of an agent.
        """
        url = reverse('agent-summary-data', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_summary_data_returns_expected_content(self, client, agent, conversation_today):
        """
        Test that the 'summary-data' action for an agent retrieves the expected summary data.
        """
        with patch('apps.call_miner.models.condense_summaries') as mock_condense_summaries:
            mock_condense_summaries.return_value = 'Mocked summary text'
            client.force_authenticate(user=agent.user)
            url = reverse('agent-summary-data', args=[agent.id])

            for period in ['week', 'month', 'quarter']:
                response = client.get(url, {'period': period})
                assert response.status_code == status.HTTP_200_OK
                assert 'summary' in response.data
                assert response.data['summary'] == 'Mocked summary text'
                assert response.data['summary_call_count'] == 1
                assert response.data['summary_date'].date() == conversation_today.date.date()
                assert 'period_label' in response.data

                if period == 'month':
                    assert response.data['period_label'] == datetime.today().strftime('%Y-%m')
                elif period == 'week':
                    assert response.data['period_label'] == datetime.today().strftime("%G-W%V")
                else:
                    label = f"{datetime.today().year}-Q{(datetime.today().month - 1) // 3 + 1}"
                    assert response.data['period_label'] == label

    def test_all_summaries_uses_month_period(
            self, client, organization_admin_user, agent, topic, conversation_today
    ):
        """
        • agent → already has 1 call (from fixture) → included
        • period label must be monthly
        """
        # silent agent without any conversation
        silent_user = User.objects.create_user(
            "silent@example.com", "password", "Silent", "Agent"
        )
        silent_agent = Agent.objects.create(
            user=silent_user, organization=agent.organization
        )

        client.force_authenticate(user=organization_admin_user)
        resp = client.get(reverse("agent-all-summaries"))
        assert resp.status_code == status.HTTP_200_OK

        data = resp.data
        assert agent.id in data

        expected_month = datetime.today().strftime("%Y-%m")
        assert data[agent.id]["period_label"] == expected_month


@pytest.mark.django_db
class TestAgentManagedAgents:
    """Tests for retrieving the managed agent of an agent manager"""

    def test_superuser_can_access_agent_managed_agents(self, client, superuser, agent_manager,
                                                       agent_managed_by_manager):
        """
        Test that a superuser can access an agent's managed_agents action.
        """
        client.force_authenticate(user=superuser)
        url = reverse('agent-managed-agents', args=[agent_manager.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        managed_agents = response.data['results']
        assert len(managed_agents) == 1
        assert managed_agents[0]['email'] == agent_managed_by_manager.user.email

    def test_organization_admin_can_access_agent_managed_agents(self, client, organization_admin_user, agent_manager,
                                                                agent_managed_by_manager):
        """
        Test that an analyst cannot access an agent's managed_agents action.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('agent-managed-agents', args=[agent_manager.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        managed_agents = response.data['results']
        assert len(managed_agents) == 1
        assert managed_agents[0]['email'] == agent_managed_by_manager.user.email

    def test_organization_admin_cannot_access_another_organization_agent_managed_agents(self, client,
                                                                                        organization_admin_user,
                                                                                        another_organization_agent):
        """
        Test that an analyst cannot access an agent's managed_agents action.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('agent-managed-agents', args=[another_organization_agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_organization_analyst_cannot_access_agent_managed_agents(self, client, analyst_user,
                                                                     agent_manager):
        """
        Test that an analyst cannot access an agent's managed_agents action.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('agent-managed-agents', args=[agent_manager.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_manager_can_access_managed_agents(self, client, agent_manager, agent_managed_by_manager, agent):
        """
        Test that an agent manager can access the managed_agents action.
        """
        client.force_authenticate(user=agent_manager.user)
        url = reverse('agent-managed-agents', args=[agent_manager.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        managed_agents = response.data['results']
        assert len(managed_agents) == 1
        assert managed_agents[0]['email'] == agent_managed_by_manager.user.email

    def test_agent_cannot_access_other_agents_managed_agents(self, client, agent_user, agent_manager):
        """
        Test that an agent cannot access another agent's managed_agents action.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('agent-managed-agents', args=[agent_manager.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_can_access_own_managed_agents(self, client, agent):
        """
        Test that an agent can access their own managed_agents action even if they have no managed agents.
        """
        client.force_authenticate(user=agent.user)
        url = reverse('agent-managed-agents', args=[agent.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        managed_agents = response.data['results']
        assert len(managed_agents) == 0

    def test_agent_in_other_organization_cannot_access_other_organization_agent_summary_data(self, client,
                                                                                             another_organization_agent_user,
                                                                                             agent_manager,
                                                                                             agent_managed_by_manager):
        """
        Test that an agent in another organization cannot access the managed agents of an agent manager.
        """
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('agent-managed-agents', args=[agent_manager.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_user_cannot_access_agent_managed_agents(self, client, agent_manager,
                                                                     agent_managed_by_manager):
        """
        Test that an unauthenticated user cannot access the managed agents of an agent.
        """
        url = reverse('agent-managed-agents', args=[agent_manager.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
