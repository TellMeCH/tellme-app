import pytest
from unittest.mock import patch
from django.urls import reverse, exceptions
from rest_framework import status
from call_miner.models import Topic

TREND_ACTIONS = ['conversations', 'trend']

ERROR_MESSAGES = {
    'max_topic_count_reached': "Cannot add more topics to this organization; max topic count reached."
}


@pytest.mark.django_db
class TestTopicList:
    """Tests for the topic-list API endpoint."""

    def test_superuser_can_list_all_topics(self, client, superuser, topic, another_organization_topic):
        """
        Test that a superuser can list all topics across organizations.
        """
        client.force_authenticate(user=superuser)
        response = client.get(reverse('topic-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_organization_admin_can_list_topics(self, client, organization_admin_user, topic,
                                                another_organization_topic):
        """
        Test that an organization admin can list topics only in their own organization.
        """
        client.force_authenticate(user=organization_admin_user)
        response = client.get(reverse('topic-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == topic.name

    def test_organization_analyst_can_list_topics(self, client, analyst_user, topic, another_organization_topic):
        """
        Test that an analyst can list topics in their own organization.
        """
        client.force_authenticate(user=analyst_user)
        response = client.get(reverse('topic-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == topic.name

    def test_agent_in_same_organization_can_list_topics(self, client, agent_user, topic, another_organization_topic):
        """
        Test that an agent in the same organization can list topics.
        """
        client.force_authenticate(user=agent_user)
        response = client.get(reverse('topic-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == topic.name

    def test_analyst_in_other_organization_can_list_topics(self, client, another_organization_analyst_user, topic,
                                                           another_organization_topic):
        """
        Test that an analyst in another organization can only list topics in their own organization.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        response = client.get(reverse('topic-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == another_organization_topic.name

    def test_agent_in_other_organization_can_list_topics(self, client, another_organization_agent_user, topic,
                                                         another_organization_topic):
        """
        Test that an agent in another organization can only list topics in their own organization.
        """
        client.force_authenticate(user=another_organization_agent_user)
        response = client.get(reverse('topic-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == another_organization_topic.name

    def test_unauthenticated_user_cannot_list_topics(self, client, topic, another_organization_topic):
        """
        Test that an unauthenticated user cannot list topics.
        """
        response = client.get(reverse('topic-list'))
        assert response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTopicRetrieve:
    """Test the topic-detail API endpoint for obtaining Topic instance details"""

    def test_superuser_can_retrieve_topic(self, client, superuser, topic):
        """
        Test that a superuser can retrieve any topic.
        """
        client.force_authenticate(user=superuser)
        url = reverse('topic-detail', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == topic.name

    def test_organization_analyst_can_retrieve_topic(self, client, analyst_user, topic):
        """
        Test that an analyst can retrieve a topic in their own organization.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('topic-detail', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == topic.name

    def test_agent_in_same_organization_can_retrieve_topic(self, client, agent_user, topic):
        """
        Test that an agent can retrieve a topic in their own organization.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('topic-detail', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == topic.name

    def test_analyst_in_other_organization_cannot_retrieve_topic(self, client, another_organization_analyst_user,
                                                                 topic):
        """
        Test that an analyst cannot retrieve a topic in another organization.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('topic-detail', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_agent_in_other_organization_cannot_retrieve_topic(self, client, another_organization_agent_user, topic):
        """
        Test that an agent cannot retrieve a topic in another organization.
        """
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('topic-detail', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_user_cannot_retrieve_topic(self, client, topic):
        """
        Test that an unauthenticated user cannot retrieve a topic.
        """
        url = reverse('topic-detail', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTopicCreate:
    """Tests for the creation of new Topic instances via the ViewSet"""

    def test_superuser_can_create_topic(self, client, superuser, organization):
        """
        Test that a superuser can create a new topic.
        """
        client.force_authenticate(user=superuser)
        data = {
            'name': 'New Topic',
            'description': 'A new topic',
            'organization': organization.id,
            'is_active': True
        }
        response = client.post(reverse('topic-list'), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Topic.objects.filter(name='New Topic').exists()

    def test_superuser_cannot_create_topic_without_organization(self, client, superuser):
        """
        Test that a superuser cannot create a new topic without specifying an organization.
        """
        client.force_authenticate(user=superuser)
        data = {
            'name': 'New Topic',
            'description': 'A new topic',
            'is_active': True
        }
        response = client.post(reverse('topic-list'), data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'organization' in response.data

    def test_organization_analyst_can_create_topic(self, client, analyst_user):
        """
        Test that an analyst can create a new topic within their own organization.
        """
        client.force_authenticate(user=analyst_user)
        data = {
            'name': 'Analyst Topic',
            'description': 'Created by analyst',
            'is_active': True
        }
        response = client.post(reverse('topic-list'), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Topic.objects.filter(name='Analyst Topic').exists()

    def test_organization_analyst_cannot_create_topic_specifying_organization(self, client, analyst_user,
                                                                              organization):
        """
        Test that an analyst cannot create a new topic specifying organization.
        """
        client.force_authenticate(user=analyst_user)
        data = {
            'name': 'Analyst Topic',
            'description': 'Created by analyst',
            'organization': organization.id,
            'is_active': True
        }
        response = client.post(reverse('topic-list'), data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'organization' in response.data

    def test_agent_in_same_organization_cannot_create_topic(self, client, agent_user, organization):
        """
        Test that an agent cannot create a topic in their organization.
        """
        client.force_authenticate(user=agent_user)
        data = {
            'name': 'Agent Topic',
            'description': 'Created by agent',
            'is_active': True
        }
        response = client.post(reverse('topic-list'), data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyst_in_other_organization_cannot_create_topic_elsewhere(self, client,
                                                                         another_organization_analyst_user,
                                                                         organization):
        """
        Test that an analyst cannot create a topic in another organization.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        data = {
            'name': 'Cross Org Topic',
            'description': 'Attempt to create in another org',
            'organization': organization.id,
            'is_active': True
        }
        response = client.post(reverse('topic-list'), data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'organization' in response.data

    def test_agent_in_other_organization_cannot_create_topic(self, client, another_organization_agent_user,
                                                             organization):
        """
        Test that an agent cannot create a topic in another organization.
        """
        client.force_authenticate(user=another_organization_agent_user)
        data = {
            'name': 'Another Agent Topic',
            'description': 'Created by another agent',
            'is_active': True
        }
        response = client.post(reverse('topic-list'), data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_create_topic(self, client, organization):
        """
        Test that an unauthenticated user cannot create a topic.
        """
        data = {
            'name': 'Unauthenticated Topic',
            'description': 'Should not be created',
            'is_active': True
        }
        response = client.post(reverse('topic-list'), data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_superuser_cannot_create_topic_beyond_max_user_count(self, client, superuser, organization):
        """Test that even a superuser cannot create more topics than the organization's max_topic_count."""
        client.force_authenticate(user=superuser)
        url = reverse('topic-list')
        topics_to_create = organization.max_topic_count - Topic.objects.filter(organization=organization).count()

        # Create topics up to the max count
        for i in range(topics_to_create):
            url = reverse('topic-list')
            data = {
                'name': f'Allowed Topic #{i}',
                'description': 'Should be created',
                'is_active': True,
                'organization': organization.id,
            }
            response = client.post(url, data, format='json')
            assert response.status_code == status.HTTP_201_CREATED

        # Attempt to create one more topic beyond the max count
        data = {
            'name': 'Excessive Topic',
            'description': 'Should not be created',
            'is_active': True,
            'organization': organization.id,
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ERROR_MESSAGES['max_topic_count_reached'] in str(response.data['non_field_errors'])

    def test_analyst_cannot_create_topic_beyond_max_user_count(self, client, analyst_user, organization):
        """Test that even a analyst cannot create more topics than the organization's max_topic_count."""
        client.force_authenticate(user=analyst_user)
        url = reverse('topic-list')
        topics_to_create = organization.max_topic_count - Topic.objects.filter(organization=organization).count()

        # Create topics up to the max count
        for i in range(topics_to_create):
            url = reverse('topic-list')
            data = {
                'name': f'Allowed Topic #{i}',
                'description': 'Should be created',
                'is_active': True
            }
            response = client.post(url, data, format='json')
            assert response.status_code == status.HTTP_201_CREATED

        # Attempt to create one more topic beyond the max count
        data = {
            'name': 'Excessive Topic',
            'description': 'Should not be created',
            'is_active': True
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ERROR_MESSAGES['max_topic_count_reached'] in str(response.data['non_field_errors'])


@pytest.mark.django_db
class TestTopicUpdate:
    """Tests for the update of an existing Topic instance."""

    def test_superuser_can_update_topic(self, client, superuser, topic):
        """
        Test that a superuser can update an existing topic.
        """
        client.force_authenticate(user=superuser)
        data = {'name': 'Updated Topic Name'}
        url = reverse('topic-detail', args=[topic.id])
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert Topic.objects.filter(name='Updated Topic Name').exists()

    def test_superuser_can_update_topic_organization(self, client, superuser, topic, another_organization):
        """
        Test that a superuser can update an existing topic's organization.
        """
        client.force_authenticate(user=superuser)
        data = {'organization': another_organization.id}
        url = reverse('topic-detail', args=[topic.id])
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert Topic.objects.filter(id=topic.id)[0].organization == another_organization

    def test_organization_analyst_can_update_topic(self, client, analyst_user, topic):
        """
        Test that an analyst can update a topic in their own organization.
        """
        client.force_authenticate(user=analyst_user)
        data = {'description': 'Updated by analyst'}
        url = reverse('topic-detail', args=[topic.id])
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert Topic.objects.filter(description='Updated by analyst').exists()

    def test_organization_analyst_cannot_update_topic_organization(self, client, analyst_user, topic,
                                                                   another_organization):
        """
        Test that an analyst cannot update an existing topic's organization.
        """
        client.force_authenticate(user=analyst_user)
        data = {'organization': another_organization.id}
        url = reverse('topic-detail', args=[topic.id])
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'organization' in response.data

    def test_agent_in_same_organization_cannot_update_topic(self, client, agent_user, topic):
        """
        Test that an agent cannot update a topic in their own organization.
        """
        client.force_authenticate(user=agent_user)
        data = {'description': 'Attempted update by agent'}
        url = reverse('topic-detail', args=[topic.id])
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyst_in_other_organization_cannot_update_topic(self, client, another_organization_analyst_user, topic):
        """
        Test that an analyst cannot update a topic in another organization.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        data = {'description': 'Attempted cross-org update'}
        url = reverse('topic-detail', args=[topic.id])
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_agent_in_other_organization_cannot_update_topic(self, client, another_organization_agent_user, topic):
        """
        Test that an agent cannot update a topic in another organization.
        """
        client.force_authenticate(user=another_organization_agent_user)
        data = {'description': 'Attempted update by another agent'}
        url = reverse('topic-detail', args=[topic.id])
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_update_topic(self, client, topic):
        """
        Test that an unauthenticated user cannot update a topic.
        """
        data = {'description': 'Attempted update by unauthenticated user'}
        url = reverse('topic-detail', args=[topic.id])
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestTopicDelete:
    """Tests for the deletion of an existing Topic instance"""

    def test_superuser_can_delete_topic(self, client, superuser, topic):
        """
        Test that a superuser can delete a topic.
        """
        client.force_authenticate(user=superuser)
        url = reverse('topic-detail', args=[topic.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_organization_analyst_can_delete_topic(self, client, analyst_user, topic):
        """
        Test that an analyst can delete a topic in their own organization.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('topic-detail', args=[topic.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_agent_in_same_organization_cannot_delete_topic(self, client, agent_user, topic):
        """
        Test that an agent cannot delete a topic in their own organization.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('topic-detail', args=[topic.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyst_in_other_organization_cannot_delete_topic(self, client, another_organization_analyst_user, topic):
        """
        Test that an analyst cannot delete a topic in another organization.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('topic-detail', args=[topic.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_agent_in_other_organization_cannot_delete_topic(self, client, another_organization_agent_user, topic):
        """
        Test that an agent cannot delete a topic in another organization.
        """
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('topic-detail', args=[topic.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_delete_topic(self, client, topic):
        """
        Test that an unauthenticated user cannot delete a topic.
        """
        url = reverse('topic-detail', args=[topic.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestTopicTrendActions:
    """Tests to obtain trends about a Topic instance's activity over time"""

    @staticmethod
    def _test_trend_action(client, url, expected_status):
        """
        Helper function to test trend actions.
        """
        response = client.get(url)
        assert response.status_code == expected_status

    def test_superuser_can_access_trend_actions(self, client, superuser, topic):
        """
        Test that a superuser can access all trend actions.
        """
        client.force_authenticate(user=superuser)
        for action in TREND_ACTIONS:
            url = reverse(f'topic-{action}', args=[topic.id])
            self._test_trend_action(client, url, status.HTTP_200_OK)

    def test_organization_analyst_can_access_trend_actions(self, client, analyst_user, topic):
        """
        Test that an analyst can access trend actions for their own organization.
        """
        client.force_authenticate(user=analyst_user)
        for action in TREND_ACTIONS:
            url = reverse(f'topic-{action}', args=[topic.id])
            self._test_trend_action(client, url, status.HTTP_200_OK)

    def test_agent_in_same_organization_can_access_trend_actions(self, client, agent_user, topic):
        """
        Test that an agent can access trend actions in their own organization.
        """
        client.force_authenticate(user=agent_user)
        for action in TREND_ACTIONS:
            url = reverse(f'topic-{action}', args=[topic.id])
            self._test_trend_action(client, url, status.HTTP_200_OK)

    def test_analyst_in_other_organization_cannot_access_trend_actions(self, client, another_organization_analyst_user,
                                                                       topic):
        """
        Test that an analyst in another organization cannot access trend actions.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        for action in TREND_ACTIONS:
            url = reverse(f'topic-{action}', args=[topic.id])
            self._test_trend_action(client, url, status.HTTP_404_NOT_FOUND)

    def test_agent_in_other_organization_cannot_access_trend_actions(self, client, another_organization_agent_user,
                                                                     topic):
        """
        Test that an agent in another organization cannot access trend actions.
        """
        client.force_authenticate(user=another_organization_agent_user)
        for action in TREND_ACTIONS:
            url = reverse(f'topic-{action}', args=[topic.id])
            self._test_trend_action(client, url, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_access_trend_actions(self, client, topic):
        """
        Test that an unauthenticated user cannot access trend actions.
        """
        for action in TREND_ACTIONS:
            url = reverse(f'topic-{action}', args=[topic.id])
            self._test_trend_action(client, url, status.HTTP_403_FORBIDDEN)

    def test_topic_conversations_action_returns_expected_content(self, client, analyst_user, topic,
                                                                 conversation):
        """
        Test that the 'conversations' action for a topic retrieves the expected conversation data.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('topic-conversations', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['title'] == conversation.title

    def test_topic_conversation_trend_action_returns_expected_content(self, client, analyst_user, topic,
                                                                      conversation):
        """
        Test that the 'trend' action retrieves the expected conversation trend data.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('topic-trend', args=[topic.id])
        response = client.get(url, {'trend_period': 'daily'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['count'] == 1

    def test_topic_duration_trend_action_returns_expected_content(self, client, analyst_user, topic,
                                                                  conversation):
        """
        Test that the 'trend' action for a topic retrieves the expected duration trend data.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('topic-trend', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['avg_duration'] == conversation.duration

    def test_topic_sentiment_trend_action_returns_expected_content(self, client, analyst_user, topic,
                                                                   conversation):
        """
        Test that the 'trend' action for a topic retrieves the expected sentiment trend data.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('topic-trend', args=[topic.id])
        response = client.get(url, {'field': 'sentiment'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['avg_sentiment'] == conversation.sentiment


@pytest.mark.django_db
class TestTopicSummary:
    """Tests for the topic-summary-data API endpoint and its access settings."""

    def test_superuser_can_access_summary_data(self, client, superuser, topic):
        """
        Test that a superuser can access the summary data of each and all topics.
        """
        client.force_authenticate(user=superuser)

        url = reverse('topic-summary-data', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse('topic-all-summaries')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_organization_analyst_can_access_summary_data(self, client, analyst_user, topic):
        """
        Test that an analyst can access the summary data of each and all topics in their own organization.
        """
        client.force_authenticate(user=analyst_user)

        url = reverse('topic-summary-data', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse('topic-all-summaries')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_agent_in_same_organization_can_access_summary_data(self, client, agent_user, topic):
        """
        Test that an agent can access the summary data of each and all topics in their own organization.
        """
        client.force_authenticate(user=agent_user)

        url = reverse('topic-summary-data', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse('topic-all-summaries')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_analyst_in_other_organization_cannot_access_summary_data(self, client, another_organization_analyst_user,
                                                                      topic):
        """
        Test that an analyst cannot access the summary data of a topic in another organization.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('topic-summary-data', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_agent_in_other_organization_cannot_access_summary_data(self, client, another_organization_agent_user,
                                                                    topic):
        """
        Test that an agent cannot access the summary data of a topic in another organization.
        """
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('topic-summary-data', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_user_cannot_access_summary_data(self, client, topic):
        """
        Test that an unauthenticated user cannot access the summary data of a topic.
        """
        url = reverse('topic-summary-data', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        url = reverse('topic-all-summaries')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_topic_summary_data_returns_expected_content(self, client, analyst_user, topic, conversation):
        """
        Test that the 'summary-data' action for a topic retrieves the expected summary data and mocks the summary
        generation.
        """

        client.force_authenticate(user=analyst_user)
        url = reverse('topic-summary-data', args=[topic.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'summary' in response.data
        assert response.data['summary'] == 'Mocked summary text'
        assert response.data['summary_call_count'] == 1
        assert response.data['summary_date'].date() == conversation.date.date()

    def test_all_summaries_returns_expected_content(self, client, analyst_user, topic, conversation):
        """
        Test that the 'all-summaries' action for all topic retrieves the expected summary data and mocks the summary
        generation.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('topic-all-summaries')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert topic.id in response.data
        assert response.data[topic.id]['summary'] == 'Mocked summary text'
        assert response.data[topic.id]['summary_call_count'] == 1
        assert response.data[topic.id]['summary_date'].date() == conversation.date.date()
        assert response.data[topic.id]['name'] == topic.name


@pytest.mark.django_db
class TestTopicListActive:
    """Tests for the topic-list-active action"""

    def test_superuser_can_list_active_topics(self, client, superuser, topic, another_organization_topic):
        """
        Test that a superuser can list all active topics.
        """
        client.force_authenticate(user=superuser)
        url = reverse('topic-list-active')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_organization_analyst_can_list_active_topics(self, client, analyst_user, topic, another_organization_topic):
        """
        Test that an analyst can list only active topics in their organization.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('topic-list-active')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == topic.name

    def test_agent_in_same_organization_can_list_active_topics(self, client, agent_user, topic,
                                                               another_organization_topic):
        """
        Test that an agent can list only active topics in their organization.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('topic-list-active')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == topic.name

    def test_analyst_in_other_organization_can_list_active_topics(self, client, another_organization_analyst_user,
                                                                  topic, another_organization_topic):
        """
        Test that an analyst can list only active topics in their own organization.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('topic-list-active')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == another_organization_topic.name

    def test_agent_in_other_organization_can_list_active_topics(self, client, another_organization_agent_user, topic,
                                                                another_organization_topic):
        """
        Test that an agent can list only active topics in their own organization.
        """
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('topic-list-active')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == another_organization_topic.name

    def test_unauthenticated_user_cannot_list_active_topics(self, client, topic, another_organization_topic):
        """
        Test that an unauthenticated user cannot list active topics.
        """
        url = reverse('topic-list-active')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_active_topics_excludes_inactive_topics(self, client, analyst_user, topic, organization):
        """
        Test that inactive topics are excluded from the active topics list.
        """
        # Create an inactive topic
        Topic.objects.create(
            name='Inactive Topic',
            description='Should not appear in active list',
            organization=organization,
            is_active=False
        )
        client.force_authenticate(user=analyst_user)
        url = reverse('topic-list-active')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == topic.name
