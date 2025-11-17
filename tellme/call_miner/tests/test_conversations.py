import pytest
from django.utils import timezone
from datetime import timedelta
from urllib.parse import urlparse, parse_qs
from django.urls import reverse
from rest_framework import status
from tellme.call_miner.models import Conversation
from datetime import datetime


@pytest.mark.django_db
class TestConversationList:
    """Tests for the conversation-list API endpoint"""

    def test_superuser_can_list_all_conversations(self, client, superuser, conversation,
                                                  another_organization_conversation):
        """
        Test that a superuser can list all conversations across all organizations.
        """
        # Superuser should see all conversations
        client.force_authenticate(user=superuser)
        response = client.get(reverse('conversation-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 2

    def test_analyst_can_list_conversations_in_organization(self, client, analyst_user, conversation):
        """
        Test that an analyst can list conversations within their own organization,
        and does not see conversations from other organizations.
        """
        client.force_authenticate(user=analyst_user)
        response = client.get(reverse('conversation-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == conversation.title

    def test_agent_can_list_conversations_in_organization(self, client, agent_user, conversation):
        """
        Test that an agent can list conversations within their own organization,
        and does not see conversations from other organizations.
        """
        client.force_authenticate(user=agent_user)
        response = client.get(reverse('conversation-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == conversation.title

    def test_another_organization_analyst_cannot_list_conversations(self, client, another_organization_analyst_user,
                                                                    another_organization_conversation):
        """Test that an analyst from another organization cannot list conversations."""
        client.force_authenticate(user=another_organization_analyst_user)
        response = client.get(reverse('conversation-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == another_organization_conversation.title

    def test_unauthenticated_user_cannot_list_conversations(self, client, organization):
        """
        Test that an unauthenticated user can't list conversations
        """
        url = reverse('conversation-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_conversation_list_ordering_allowed_fields(self, client, analyst_user, conversation):
        """Test that all allowed ordering fields work correctly"""
        client.force_authenticate(user=analyst_user)
        allowed_fields = ['date', 'sentiment', 'resolved']

        for field in allowed_fields:
            # Test ascending
            response = client.get(reverse('conversation-list'), {'ordering': field})
            assert response.status_code == status.HTTP_200_OK, f"Failed for field: {field}"

            # Test descending
            response = client.get(reverse('conversation-list'), {'ordering': f'-{field}'})
            assert response.status_code == status.HTTP_200_OK, f"Failed for field: -{field}"

    def test_conversation_list_ordering_invalid_field(self, client, analyst_user, conversation):
        """Test that ordering by invalid fields is ignored and default ordering is applied"""
        client.force_authenticate(user=analyst_user)

        # Get response with invalid ordering
        invalid_response = client.get(reverse('conversation-list'), {'ordering': 'invalid_field'})
        assert invalid_response.status_code == status.HTTP_200_OK

        # Get response with default ordering
        default_response = client.get(reverse('conversation-list'))
        assert default_response.status_code == status.HTTP_200_OK

        # Results should be the same (invalid ordering ignored, default applied)
        assert invalid_response.data == default_response.data

    def test_conversation_list_no_ordering_parameter(self, client, analyst_user, conversation):
        """Test that default ordering is applied when no ordering parameter is provided"""
        client.force_authenticate(user=analyst_user)
        response = client.get(reverse('conversation-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_conversation_list_cursor_with_different_ordering_fails(self, client, analyst_user, conversation, customer, agent):
        """Test that using a cursor with different ordering than the cursor was created with fails gracefully"""

        # Create additional conversations to enable pagination
        base_date = timezone.now()
        for i in range(3):
            Conversation.objects.create(
                path=f"test_{i}.mp3",
                date=base_date - timedelta(days=i),
                duration=300.0 + i * 100,
                transcript=f"Test transcript {i}",
                sentiment=2.0 + i * 0.5,
                summary=f"Summary {i}",
                title=f"Title {i}",
                input_tokens=100 + i * 10,
                output_tokens=50 + i * 5,
                customer=customer,
                agent=agent,
                resolved=i % 2 == 0
            )

        client.force_authenticate(user=analyst_user)

        # Get first page ordered by date to obtain a cursor
        date_response = client.get(reverse('conversation-list'), {
            'ordering': 'date',
            'page_size': 2  # Force pagination
        })
        assert date_response.status_code == status.HTTP_200_OK

        # Extract cursor
        next_url = date_response.data.get('next')
        parsed_url = urlparse(next_url)
        cursor_params = parse_qs(parsed_url.query)
        cursor = cursor_params.get('cursor', [None])[0]

        # Try to use cursor with same ordering
        response = client.get(reverse('conversation-list'), {
            'ordering': 'date',
            'cursor': cursor
        })

        assert response.status_code == status.HTTP_200_OK

        # Try to use cursor with different ordering - should raise an error
        with pytest.raises((ValueError, Exception)):
            response = client.get(reverse('conversation-list'), {
                'ordering': 'sentiment',
                'cursor': cursor
            })


@pytest.mark.django_db
class TestConversationRetrieve:
    """Tests for the conversation-detail API endpoint"""

    def test_superuser_can_view_any_conversation(self, client, superuser, conversation,
                                                 another_organization_conversation):
        """
        Test that a superuser can view any conversation across all organizations.
        """
        # Superuser should be able to view any conversation
        client.force_authenticate(user=superuser)
        response = client.get(reverse('conversation-detail', args=[conversation.id]))
        assert response.status_code == status.HTTP_200_OK

        response = client.get(reverse('conversation-detail', args=[another_organization_conversation.id]))
        assert response.status_code == status.HTTP_200_OK

    def test_analyst_can_view_conversation_in_organization(self, client, analyst_user, conversation):
        """
        Test that an analyst can view a conversation within their own organization.
        """
        client.force_authenticate(user=analyst_user)
        response = client.get(reverse('conversation-detail', args=[conversation.id]))
        assert response.status_code == status.HTTP_200_OK

    def test_analyst_cannot_view_conversation_in_other_organization(self, client, analyst_user,
                                                                    another_organization_conversation):
        """
        Test that an analyst cannot view a conversation from another organization.
        """
        client.force_authenticate(user=analyst_user)
        response = client.get(reverse('conversation-detail', args=[another_organization_conversation.id]))
        assert response.status_code == status.HTTP_404_NOT_FOUND  # Not found due to queryset filtering

    def test_agent_can_view_conversation_in_organization(self, client, agent_user, conversation):
        """
        Test that an agent can view a conversation within their own organization.
        """
        client.force_authenticate(user=agent_user)
        response = client.get(reverse('conversation-detail', args=[conversation.id]))
        assert response.status_code == status.HTTP_200_OK

    def test_agent_cannot_view_conversation_in_other_organization(self, client, agent_user,
                                                                  another_organization_conversation):
        """
        Test that an agent cannot view a conversation from another organization.
        """
        client.force_authenticate(user=agent_user)
        response = client.get(reverse('conversation-detail', args=[another_organization_conversation.id]))
        assert response.status_code == status.HTTP_404_NOT_FOUND  # Not found due to queryset filtering

    def test_unauthenticated_user_cannot_view_conversation(self, client, conversation):
        """
        Test that an unauthenticated user cannot view any conversation.
        """
        url = reverse('conversation-detail', args=[conversation.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestConversationTranscript:
    def test_superuser_can_view_any_conversation_transcript(self, client, superuser, conversation,
                                                            another_organization_conversation):
        """
        Test that a superuser can view the transcript of any conversation across all organizations.
        """
        # Superuser should be able to view any conversation transcript
        client.force_authenticate(user=superuser)
        url = reverse('conversation-transcript', args=[conversation.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        url = reverse('conversation-transcript', args=[another_organization_conversation.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_analyst_can_view_conversation_transcript(self, client, analyst_user, conversation):
        """
        Test that an analyst can view the transcript of a conversation within their own organization.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('conversation-transcript', args=[conversation.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) > 0

    def test_analyst_cannot_view_other_organization_conversation_transcript(self, client, analyst_user,
                                                                            another_organization_conversation):
        """
        Test that an analyst cannot view the transcript of a conversation from another organization.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('conversation-transcript', args=[another_organization_conversation.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND  # Not found due to queryset filtering

    def test_agent_can_view_conversation_transcript(self, client, agent_user, conversation):
        """
        Test that an agent can view the transcript of a conversation within their own organization.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('conversation-transcript', args=[conversation.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) > 0

    def test_agent_cannot_view_other_organization_conversation_transcript(self, client, agent_user,
                                                                          another_organization_conversation):
        """
        Test that an agent cannot view the transcript of a conversation from another organization.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('conversation-transcript', args=[another_organization_conversation.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND  # Not found due to queryset filtering

    def test_process_transcript_output(self, client, analyst_user, conversation):
        """
        Test that the process_transcript() method correctly processes the transcript and
        the ViewSet returns the expected paginated response.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('conversation-transcript', args=[conversation.id])

        # Fetch all pages of the transcript
        all_messages = []
        next_url = url
        while next_url:
            response = client.get(next_url)
            assert response.status_code == status.HTTP_200_OK

            # Extract processed transcript from response
            assert 'results' in response.data
            messages = response.data['results']
            all_messages.extend(messages)

            next_url = response.data.get('next')

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

    def test_transcript_pagination(self, client, analyst_user, conversation, settings):
        """
        Test that the processed transcript is paginated correctly based on the PAGE_SIZE setting.
        """
        # Set page size for testing pagination
        settings.REST_FRAMEWORK['PAGE_SIZE'] = 15

        client.force_authenticate(user=analyst_user)
        url = reverse('conversation-transcript', args=[conversation.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # Check that pagination is applied
        assert 'next' in response.data
        assert 'previous' in response.data
        assert len(response.data['results']) == settings.REST_FRAMEWORK['PAGE_SIZE']

        # Fetch next page if available
        next_url = response.data['next']
        if next_url:
            response_next = client.get(next_url)
            assert response_next.status_code == status.HTTP_200_OK
            transcript_data_next = response_next.data
            assert len(transcript_data_next['results']) > 0

    def test_unauthenticated_user_cannot_view_conversation_transcript(self, client, conversation):
        """
        Test that an unauthenticated user can't view the transcript of any conversation.
        """
        url = reverse('conversation-transcript', args=[conversation.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestConversationCreate:
    """Test the creation of a Conversation via its ViewSet"""

    def test_superuser_can_create_conversation(self, client, superuser, agent, customer):
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
            'sentiment': 3.6,
            'topics': [],
            'suggested_topics': [],
            'agent': agent.id,
            'customer': customer.id,
            'input_tokens': 120,
            'output_tokens': 60,
            'revenue_at_stake': 100,
        }
        response = client.post(reverse('conversation-list'), data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Conversation.objects.filter(title='New Conversation').exists()

    def test_organization_admin_cannot_create_conversation(self, client, organization_admin_user, agent, customer):
        """
        Test that an organization admin cannot create a new conversation.
        """
        # Organization admin should not be able to create a conversation
        client.force_authenticate(user=organization_admin_user)
        data = {
            'path': 'path/to/new_conversation',
            'date': datetime.now().isoformat(),
            'duration': 100.0,
            'transcript': 'New transcript',
            'summary': 'New summary',
            'title': 'New Conversation',
            'sentiment': 3.6,
            'topics': [],
            'suggested_topics': [],
            'agent': agent.id,
            'customer': customer.id,
            'input_tokens': 120,
            'output_tokens': 60,
            'revenue_at_stake': 100,
        }
        response = client.post(reverse('conversation-list'), data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyst_cannot_create_conversation(self, client, analyst_user, agent, customer):
        """
        Test that an analyst cannot create a new conversation.
        """
        client.force_authenticate(user=analyst_user)
        data = {
            'path': 'path/to/new_conversation',
            'date': datetime.now().isoformat(),
            'duration': 100.0,
            'transcript': 'New transcript',
            'summary': 'New summary',
            'title': 'New Conversation',
            'sentiment': 3.6,
            'topics': [],
            'suggested_topics': [],
            'agent': agent.id,
            'customer': customer.id,
            'input_tokens': 120,
            'output_tokens': 60,
            'revenue_at_stake': 100,
        }
        response = client.post(reverse('conversation-list'), data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_create_conversation(self, client, agent_user, agent, customer):
        """
        Test that an agent cannot create a new conversation.
        """
        client.force_authenticate(user=agent_user)
        data = {
            'path': 'path/to/new_conversation',
            'date': datetime.now().isoformat(),
            'duration': 100.0,
            'transcript': 'New transcript',
            'summary': 'New summary',
            'title': 'New Conversation',
            'sentiment': 3.6,
            'topics': [],
            'suggested_topics': [],
            'agent': agent.id,
            'customer': customer.id,
            'input_tokens': 120,
            'output_tokens': 60,
            'revenue_at_stake': 100,
        }
        response = client.post(reverse('conversation-list'), data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_another_organization_analyst_cannot_create_conversation(self, client, another_organization_analyst_user,
                                                                     agent,
                                                                     customer):
        """
        Test that another organization's analyst cannot create a new conversation.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        data = {
            'path': 'path/to/new_conversation',
            'date': datetime.now().isoformat(),
            'duration': 100.0,
            'transcript': 'New transcript',
            'summary': 'New summary',
            'title': 'New Conversation',
            'sentiment': 3.6,
            'topics': [],
            'suggested_topics': [],
            'agent': agent.id,
            'customer': customer.id,
            'input_tokens': 120,
            'output_tokens': 60,
            'revenue_at_stake': 100,
        }
        response = client.post(reverse('conversation-list'), data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_create_conversation(self, client, agent, customer):
        """
        Test that an unauthenticated user cannot create a new conversation.
        """
        data = {
            'path': 'path/to/new_conversation',
            'date': datetime.now().isoformat(),
            'duration': 100.0,
            'transcript': 'New transcript',
            'summary': 'New summary',
            'title': 'New Conversation',
            'sentiment': 3.6,
            'topics': [],
            'suggested_topics': [],
            'agent': agent.id,
            'customer': customer.id,
            'input_tokens': 120,
            'output_tokens': 60,
            'revenue_at_stake': 100,
        }
        response = client.post(reverse('conversation-list'), data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_sentiment_score_validation(self, client, superuser, agent, customer):
        """
        Test that an invalid sentiment score raises a validation error when creating a Conversation
        """
        client.force_authenticate(user=superuser)
        data = {
            'path': 'path/to/new_conversation',
            'date': datetime.now().isoformat(),
            'duration': 100.0,
            'transcript': 'New transcript',
            'summary': 'New summary',
            'title': 'New Conversation',
            'sentiment': 87,
            'topics': [],
            'suggested_topics': [],
            'agent': agent.id,
            'customer': customer.id,
            'input_tokens': 120,
            'output_tokens': 60,
            'revenue_at_stake': 100,
        }
        response = client.post(reverse('conversation-list'), data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'sentiment' in response.data

        data = {
            'path': 'path/to/new_conversation',
            'date': datetime.now().isoformat(),
            'duration': 100.0,
            'transcript': 'New transcript',
            'summary': 'New summary',
            'title': 'New Conversation',
            'sentiment': -3,
            'topics': [],
            'suggested_topics': [],
            'agent': agent.id,
            'customer': customer.id,
            'input_tokens': 120,
            'output_tokens': 60,
            'revenue_at_stake': 100,
        }
        response = client.post(reverse('conversation-list'), data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'sentiment' in response.data


@pytest.mark.django_db
class TestConversationUpdate:
    """Test the update of an existing Conversation via the API"""

    def test_superuser_can_update_conversation(self, client, superuser, conversation):
        """
        Test that a superuser can update an existing conversation.
        """
        # Superuser should be able to update a conversation
        client.force_authenticate(user=superuser)
        data = {'title': 'Updated Title'}
        response = client.patch(reverse('conversation-detail', args=[conversation.id]), data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert Conversation.objects.filter(title='Updated Title').exists()

    def test_analyst_cannot_update_conversation(self, client, analyst_user, conversation):
        """
        Test that an analyst cannot update an existing conversation.
        """
        client.force_authenticate(user=analyst_user)
        data = {'title': 'Updated Title'}
        response = client.patch(reverse('conversation-detail', args=[conversation.id]), data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_update_conversation(self, client, agent_user, conversation):
        """
        Test that an agent cannot update an existing conversation.
        """
        client.force_authenticate(user=agent_user)
        data = {'title': 'Updated Title'}
        response = client.patch(reverse('conversation-detail', args=[conversation.id]), data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_another_organization_analyst_cannot_update_conversation(self, client, another_organization_analyst_user,
                                                                     conversation):
        """
        Test that another organization's analyst cannot update an existing conversation.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        data = {'title': 'Updated Title'}
        response = client.patch(reverse('conversation-detail', args=[conversation.id]), data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_update_conversation(self, client, conversation):
        """
        Test that an agent cannot update a conversation.
        """
        data = {'title': 'Updated Title'}
        response = client.patch(reverse('conversation-detail', args=[conversation.id]), data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_sentiment_score_validation(self, client, superuser, conversation):
        """
        Test that an invalid sentiment score raises a validation error when creating a Conversation
        """
        client.force_authenticate(user=superuser)
        data = {'sentiment': 87}
        response = client.patch(reverse('conversation-detail', args=[conversation.id]), data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'sentiment' in response.data

        data = {'sentiment': -3}
        response = client.patch(reverse('conversation-detail', args=[conversation.id]), data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'sentiment' in response.data


@pytest.mark.django_db
class TestConversationDelete:
    """Test the deletion of an existing Conversation"""

    def test_superuser_can_delete_conversation(self, client, superuser, conversation):
        """
        Test that a superuser can delete a conversation.
        """
        # Superuser should be able to delete a conversation
        client.force_authenticate(user=superuser)
        response = client.delete(reverse('conversation-detail', args=[conversation.id]))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_analyst_cannot_delete_conversation(self, client, analyst_user, conversation):
        """
        Test that an analyst cannot delete a conversation.
        """
        client.force_authenticate(user=analyst_user)
        response = client.delete(reverse('conversation-detail', args=[conversation.id]))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_delete_conversation(self, client, agent_user, conversation):
        """
        Test that an agent cannot delete a conversation.
        """
        client.force_authenticate(user=agent_user)
        response = client.delete(reverse('conversation-detail', args=[conversation.id]))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_another_organization_analyst_cannot_delete_conversation(self, client, another_organization_analyst_user,
                                                                     conversation):
        """
        Test that another organization's analyst cannot delete a conversation.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        response = client.delete(reverse('conversation-detail', args=[conversation.id]))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_delete_conversation(self, client, conversation):
        """
        Test that an agent cannot delete a new conversation.
        """
        response = client.delete(reverse('conversation-detail', args=[conversation.id]))
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestConversationSearch:
    """Tests for the conversation search functionality"""
    @staticmethod
    def response_from_search_url(client, search_query: str):
        """
         Helper method to fetch all paginated results given a search query

         :param client: The APIClient instance.
         :param search_query: Search query to construct the first URL from.
         :return: A list containing all results from all pages.
         """
        all_results = []
        next_url = reverse('conversation-search') + f'?query={search_query}'
        while next_url:
            response = client.get(next_url)
            assert response.status_code == status.HTTP_200_OK
            data = response.data
            results = data.get('results', [])
            all_results.extend(results)
            next_url = data.get('next')
        return all_results

    def test_search_by_transcript_content(self, client, analyst_user, conversation):
        """
        Test that conversations can be searched and retrieved based on content in the transcript.
        """
        client.force_authenticate(user=analyst_user)
        search_query = "strange noise"
        results = self.response_from_search_url(client, search_query)
        conversation_ids = [conv['url'].rstrip('/').split('/')[-1] for conv in results]

        assert len(results) >= 1
        assert str(conversation.id) in conversation_ids

    def test_search_by_summary_content(self, client, analyst_user, conversation):
        """
        Test that conversations can be searched and retrieved based on content in the summary.
        """
        client.force_authenticate(user=analyst_user)
        search_query = conversation.summary
        results = self.response_from_search_url(client, search_query)
        conversation_ids = [conv['url'].rstrip('/').split('/')[-1] for conv in results]

        assert len(results) >= 1
        assert str(conversation.id) in conversation_ids

    def test_search_by_topic_name(self, client, analyst_user, conversation, topic):
        """
        Test that conversations can be searched and retrieved based on the topics.
        """
        client.force_authenticate(user=analyst_user)
        search_query = topic.name
        results = self.response_from_search_url(client, search_query)
        conversation_ids = [conv['url'].rstrip('/').split('/')[-1] for conv in results]

        assert len(results) >= 1
        assert str(conversation.id) in conversation_ids

    def test_search_no_duplicates_in_results(self, client, analyst_user, conversation, agent):
        """
        Test that conversations resulting from a query do not contain duplicates.
        """
        client.force_authenticate(user=analyst_user)
        search_query = agent.user.first_name
        results = self.response_from_search_url(client, search_query)
        conversation_ids = [conv['url'].rstrip('/').split('/')[-1] for conv in results]

        assert len(results) >= 1
        assert str(conversation.id) in conversation_ids
        assert len(conversation_ids) == len(set(conversation_ids))

    def test_websearch_query_behavior(self, client, analyst_user, conversation):
        """
        Test that 'websearch' query types can be used and behave as expected.
        """
        client.force_authenticate(user=analyst_user)

        # Test inclusion with OR operator
        search_query = '"strange noise" OR "driving me crazy" -spam'
        results = self.response_from_search_url(client, search_query)
        conversation_ids = [conv['url'].rstrip('/').split('/')[-1] for conv in results]

        assert len(results) >= 1
        assert str(conversation.id) in conversation_ids

        # Test exclusion with NOT operator
        search_query = '"strange noise" -"driving me crazy"'
        results = self.response_from_search_url(client, search_query)
        conversation_ids = [conv['url'].rstrip('/').split('/')[-1] for conv in results]

        assert len(results) >= 1
        assert str(conversation.id) in conversation_ids

    def test_search_no_results(self, client, analyst_user):
        """
        Test the expected response when a query produces no results
        """
        client.force_authenticate(user=analyst_user)
        search_query = "agrearhadfgsdfgfdsgdfg"
        url = reverse('conversation-search') + f'?query={search_query}'
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == 'Your query produced no results.'
