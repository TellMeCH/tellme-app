import pytest
from django.urls import reverse
from rest_framework import status
from apps.call_miner.models import Topic, SuggestedTopic


@pytest.mark.django_db
class TestSuggestedTopicList:
    """Tests for the suggested-topic-list API endpoint."""

    def test_superuser_can_list_all_suggested_topics(self, client, superuser, suggested_topic, another_organization_suggested_topic):
        """
        Test that a superuser can list all suggested topics across organizations.
        """
        client.force_authenticate(user=superuser)
        response = client.get(reverse('suggested-topic-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_organization_admin_can_list_suggested_topics(self, client, organization_admin_user, suggested_topic,
                                                         another_organization_suggested_topic):
        """
        Test that an organization admin can list suggested topics only in their own organization.
        """
        client.force_authenticate(user=organization_admin_user)
        response = client.get(reverse('suggested-topic-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == suggested_topic.name

    def test_organization_analyst_can_list_suggested_topics(self, client, analyst_user, suggested_topic, another_organization_suggested_topic):
        """
        Test that an analyst can list suggested topics in their own organization.
        """
        client.force_authenticate(user=analyst_user)
        response = client.get(reverse('suggested-topic-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == suggested_topic.name

    def test_agent_in_same_organization_can_list_suggested_topics(self, client, agent_user, suggested_topic, another_organization_suggested_topic):
        """
        Test that an agent in the same organization can list suggested topics.
        """
        client.force_authenticate(user=agent_user)
        response = client.get(reverse('suggested-topic-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == suggested_topic.name

    def test_analyst_in_other_organization_can_list_suggested_topics(self, client, another_organization_analyst_user, suggested_topic,
                                                                   another_organization_suggested_topic):
        """
        Test that an analyst in another organization can only list suggested topics in their own organization.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        response = client.get(reverse('suggested-topic-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == another_organization_suggested_topic.name

    def test_agent_in_other_organization_can_list_suggested_topics(self, client, another_organization_agent_user, suggested_topic,
                                                                  another_organization_suggested_topic):
        """
        Test that an agent in another organization can only list suggested topics in their own organization.
        """
        client.force_authenticate(user=another_organization_agent_user)
        response = client.get(reverse('suggested-topic-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == another_organization_suggested_topic.name

    def test_unauthenticated_user_cannot_list_suggested_topics(self, client, suggested_topic, another_organization_suggested_topic):
        """
        Test that an unauthenticated user cannot list suggested topics.
        """
        response = client.get(reverse('suggested-topic-list'))
        assert response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_suggested_topic_conversation_stats(self, client, organization_admin_user, conversation, agent, customer, suggested_topic):
        """
        Test that the conversation stats for the suggested topic are as expected.
        """
        client.force_authenticate(user=organization_admin_user)
        response = client.get(reverse('suggested-topic-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        result = response.data['results'][0]
        assert "conversation_count" in result
        assert "first_conversation_date" in result
        assert "last_conversation_date" in result
        assert result.get("conversation_count") == 1
        assert result.get("first_conversation_date") == conversation.date.isoformat()[:-6] + 'Z'
        assert result.get("last_conversation_date") == conversation.date.isoformat()[:-6] + 'Z'


@pytest.mark.django_db
class TestSuggestedTopicAccept:
    """Tests for the suggested-topic accept functionality."""

    def test_superuser_can_accept_suggested_topic(self, client, superuser, suggested_topic, organization):
        """
        Test that a superuser can accept a suggested topic.
        """
        client.force_authenticate(user=superuser)
        url = reverse('suggested-topic-accept', args=[suggested_topic.id])
        response = client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify response contains new topic data
        assert 'name' in response.data
        assert response.data['name'] == suggested_topic.name
        assert response.data['description'] == suggested_topic.description

        # Verify suggested topic no longer exists
        assert not SuggestedTopic.objects.filter(id=suggested_topic.id).exists()
        
        # Verify regular topic was created
        assert Topic.objects.filter(name=suggested_topic.name, organization=organization).exists()

    def test_organization_admin_can_accept_suggested_topic(self, client, organization_admin_user, suggested_topic, organization):
        """
        Test that an organization admin can accept a suggested topic.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('suggested-topic-accept', args=[suggested_topic.id])
        response = client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify response contains new topic data
        assert 'name' in response.data
        assert response.data['name'] == suggested_topic.name

        # Verify suggested topic no longer exists
        assert not SuggestedTopic.objects.filter(id=suggested_topic.id).exists()
        
        # Verify regular topic was created
        assert Topic.objects.filter(name=suggested_topic.name, organization=organization).exists()

    def test_organization_analyst_can_accept_suggested_topic(self, client, analyst_user, suggested_topic, organization):
        """
        Test that an analyst can accept a suggested topic in their own organization.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('suggested-topic-accept', args=[suggested_topic.id])
        response = client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify suggested topic no longer exists
        assert not SuggestedTopic.objects.filter(id=suggested_topic.id).exists()
        
        # Verify regular topic was created
        assert Topic.objects.filter(name=suggested_topic.name, organization=organization).exists()

    def test_agent_in_same_organization_cannot_accept_suggested_topic(self, client, agent_user, suggested_topic):
        """
        Test that an agent cannot accept a suggested topic in their organization.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('suggested-topic-accept', args=[suggested_topic.id])
        response = client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyst_in_other_organization_cannot_accept_suggested_topic(self, client, another_organization_analyst_user, suggested_topic):
        """
        Test that an analyst cannot accept a suggested topic in another organization.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('suggested-topic-accept', args=[suggested_topic.id])
        response = client.post(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_agent_in_other_organization_cannot_accept_suggested_topic(self, client, another_organization_agent_user, suggested_topic):
        """
        Test that an agent cannot accept a suggested topic in another organization.
        """
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('suggested-topic-accept', args=[suggested_topic.id])
        response = client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_accept_suggested_topic(self, client, suggested_topic):
        """
        Test that an unauthenticated user cannot accept a suggested topic.
        """
        url = reverse('suggested-topic-accept', args=[suggested_topic.id])
        response = client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_accept_suggested_topic_preserves_conversation_count(self, client, analyst_user, suggested_topic, conversation, organization):
        """
        Test that accepting a suggested topic preserves the conversation count.
        """
        # Force update stats to ensure they're current
        suggested_topic.update_conversation_stats()
        suggested_topic.refresh_from_db()

        # Verify initial state
        assert suggested_topic.conversation_count == 1
        
        client.force_authenticate(user=analyst_user)
        url = reverse('suggested-topic-accept', args=[suggested_topic.id])
        response = client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Get the new topic
        new_topic = Topic.objects.get(name=suggested_topic.name, organization=organization)
        
        # Verify conversation count is preserved
        assert new_topic.conversation_count == 1
        
        # Verify the conversation is now linked to the new topic
        conversation.refresh_from_db()
        assert new_topic in conversation.topics.all()
        assert suggested_topic not in conversation.suggested_topics.all()

    def test_accept_suggested_topic_removes_from_suggested_list(self, client, analyst_user, suggested_topic, organization):
        """
        Test that accepting a suggested topic removes it from the suggested topics list.
        """
        # Verify suggested topic appears in list initially
        client.force_authenticate(user=analyst_user)
        list_response = client.get(reverse('suggested-topic-list'))
        assert len(list_response.data['results']) == 1
        
        # Accept the suggested topic
        accept_url = reverse('suggested-topic-accept', args=[suggested_topic.id])
        accept_response = client.post(accept_url)
        assert accept_response.status_code == status.HTTP_200_OK
        
        # Verify suggested topic no longer appears in list
        list_response = client.get(reverse('suggested-topic-list'))
        assert len(list_response.data['results']) == 0

    def test_accept_suggested_topic_appears_in_topics_list(self, client, analyst_user, suggested_topic, organization):
        """
        Test that accepting a suggested topic makes it appear in the regular topics list.
        """
        # Get initial topics count
        client.force_authenticate(user=analyst_user)
        initial_topics_response = client.get(reverse('topic-list'))
        initial_count = len(initial_topics_response.data['results'])
        
        # Accept the suggested topic
        accept_url = reverse('suggested-topic-accept', args=[suggested_topic.id])
        accept_response = client.post(accept_url)
        assert accept_response.status_code == status.HTTP_200_OK
        
        # Verify new topic appears in topics list
        final_topics_response = client.get(reverse('topic-list'))
        assert len(final_topics_response.data['results']) == initial_count + 1
        
        # Find the new topic in the list
        topic_names = [topic['name'] for topic in final_topics_response.data['results']]
        assert suggested_topic.name in topic_names

    def test_accept_nonexistent_suggested_topic_returns_404(self, client, analyst_user):
        """
        Test that trying to accept a non-existent suggested topic returns 404.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('suggested-topic-accept', args=[9999])
        response = client.post(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_cannot_accept_topic_beyond_max_topic_count(self, client, analyst_user, organization, suggested_topic):
        """Test that one can't accept a suggested topic beyond the organization's max_topic_count."""
        client.force_authenticate(user=analyst_user)
        
        # Get current topic count
        current_topic_count = Topic.objects.filter(organization=organization).count()
        topics_to_create = organization.max_topic_count - current_topic_count
        
        # Create topics up to the max count via API
        for i in range(topics_to_create):
            data = {
                'name': f'Allowed Topic #{i}',
                'description': 'Should be created',
                'is_active': True
            }
            response = client.post(reverse('topic-list'), data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
        
        # Verify we're now at the max count
        assert Topic.objects.filter(organization=organization).count() == organization.max_topic_count
        
        # Try to accept the suggested topic beyond the max count
        accept_url = reverse('suggested-topic-accept', args=[suggested_topic.id])
        accept_response = client.post(accept_url)
        assert accept_response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Verify error message
        assert 'non_field_errors' in accept_response.data
        assert 'maximum topic count reached' in str(accept_response.data['non_field_errors'][0]).lower()
        
        # Verify the suggested topic still exists (wasn't accepted)
        assert SuggestedTopic.objects.filter(id=suggested_topic.id).exists()
        
        # Verify no new regular topic was created
        assert not Topic.objects.filter(name=suggested_topic.name, organization=organization).exists()

    def test_can_accept_topic_at_max_topic_count_minus_one(self, client, analyst_user, organization, suggested_topic):
        """Test that one can accept a suggested topic when it would exactly reach the max_topic_count."""
        client.force_authenticate(user=analyst_user)
        
        # Get current topic count
        current_topic_count = Topic.objects.filter(organization=organization).count()
        topics_to_create = organization.max_topic_count - current_topic_count - 1  # Leave space for 1 more
        
        # Create topics up to max_count - 1
        for i in range(topics_to_create):
            data = {
                'name': f'Allowed Topic #{i}',
                'description': 'Should be created',
                'is_active': True
            }
            response = client.post(reverse('topic-list'), data, format='json')
            assert response.status_code == status.HTTP_201_CREATED
        
        # Verify we're at max_count - 1
        assert Topic.objects.filter(organization=organization).count() == organization.max_topic_count - 1
        
        # Accept the suggested topic (should succeed as it reaches exactly max_count)
        accept_url = reverse('suggested-topic-accept', args=[suggested_topic.id])
        accept_response = client.post(accept_url)
        assert accept_response.status_code == status.HTTP_200_OK
        
        # Verify the suggested topic no longer exists
        assert not SuggestedTopic.objects.filter(id=suggested_topic.id).exists()
        
        # Verify the regular topic was created
        assert Topic.objects.filter(name=suggested_topic.name, organization=organization).exists()
        
        # Verify we're now at exactly the max count
        assert Topic.objects.filter(organization=organization).count() == organization.max_topic_count

    def test_accept_validation_uses_current_topic_count(self, client, analyst_user, organization, suggested_topic):
        """Test that validation correctly counts current topics at time of acceptance."""
        client.force_authenticate(user=analyst_user)
        
        # Create a topic directly in the database to change the count between requests
        initial_count = Topic.objects.filter(organization=organization).count()
        
        # Fill up to max count - 1
        topics_to_create = organization.max_topic_count - initial_count - 1
        for i in range(topics_to_create):
            Topic.objects.create(
                name=f'Direct Topic #{i}',
                description='Created directly',
                organization=organization,
                is_active=True
            )
        
        # Verify we're at max - 1
        assert Topic.objects.filter(organization=organization).count() == organization.max_topic_count - 1
        
        # This should succeed (at exactly max count)
        accept_response = client.post(reverse('suggested-topic-accept', args=[suggested_topic.id]))
        assert accept_response.status_code == status.HTTP_200_OK
