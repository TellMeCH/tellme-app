import pytest
import json
from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework import status
from tellme.call_miner.models import Conversation, User, Organization, Topic, SuggestedTopic


@pytest.mark.django_db
@pytest.mark.usefixtures('mock_dlp')
class TestProcessRecordingView:
    @pytest.fixture
    def valid_task_payload(self):
        return {
            "file_name": "1/CUST123_123_2024-01-01T12:00:00.wav",
            "organization_id": 1,
            "customer_id": "CUST123",
            "agent_id": 123,
            "timestamp": "2024-01-01T12:00:00",
            "transcription_method": "deepgram",
            "enrichment_method": "openai"
        }

    def test_authentication_success(self, settings, setup_db, api_client):
        settings.PROCESSING_PIPELINE_KEY = "test_pipeline_key"
        settings.PROCESSING_PIPELINE_USER = "pipeline@example.com"

        # Create the user expected by the authentication class
        User.objects.create_user("pipeline@example.com", "password", 'pipeline', 'executor')

        # Set the authorization header
        url = reverse("process")
        api_client.credentials(HTTP_AUTHORIZATION="Token test_pipeline_key")
        response = api_client.post(url, data={}, format="json")

        # Ensure the response shows a failed body payload validation (authentication worked)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_authentication_failure(self, settings, setup_db, api_client):
        settings.PROCESSING_PIPELINE_KEY = "test_pipeline_key"
        settings.PROCESSING_PIPELINE_USER = "pipeline@example.com"

        # Missing user setup
        url = reverse("process")
        api_client.credentials(HTTP_AUTHORIZATION="Token wrong_key")
        response = api_client.post(url, data={}, format="json")

        # Ensure authentication failure
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_process_missing_file_name(self, api_client, setup_db, mock_processing_user):
        url = reverse("process")
        response = api_client.post(url, data={}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_process_empty_file(self, api_client, mock_gcs_utils, setup_db, valid_task_payload,
                                mock_processing_user):
        mock_gcs_utils[1].return_value = b""
        url = reverse("process")
        response = api_client.post(url, data=valid_task_payload, format="json")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "is empty" in response.data["error"]

    @patch("tellme.call_processing.views.create_conversation")
    @patch("tellme.call_processing.views.create_suggested_topics")
    def test_process_success(
            self, mock_create_suggested_topics, mock_create_conversation, api_client, valid_task_payload, setup_db,
            mock_gcs_utils, mock_deepgram, mock_groq, mock_openai, mock_pydub, mock_processing_user
    ):
        """
        If everything is valid, the pipeline runs, the conversation is created in DB,
        and we return a 200 OK.
        """
        url = reverse("process")
        response = api_client.post(url, data=valid_task_payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        mock_create_conversation.assert_called_once()
        mock_create_suggested_topics.assert_called_once()
        assert response.data["message"] == "File processed and saved to DB."

    def test_create_conversation_in_db(
            self, api_client, setup_db, valid_task_payload, mock_gcs_utils, mock_deepgram, mock_groq,
            mock_openai, mock_pydub, mock_processing_user
    ):
        """
        Instead of patching create_conversation, let's confirm that a Conversation object is
        actually created in the DB upon successful processing.
        """
        url = reverse("process")
        response = api_client.post(url, data=valid_task_payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        conv = Conversation.objects.last()
        assert conv is not None
        assert conv.path == valid_task_payload["file_name"]
        assert conv.agent.id == valid_task_payload["agent_id"]
        assert conv.customer.external_id == valid_task_payload["customer_id"]
        assert conv.transcript is not None
        assert conv.title == "Test Call"
        assert conv.summary == "Short summary"

    def test_create_conversation_with_suggested_topics(
        self, api_client, setup_db, valid_task_payload, mock_gcs_utils, mock_deepgram, 
        mock_groq, mock_openai, mock_pydub, mock_processing_user
    ):
        """
        Test that conversations are created with suggested topics when provided by enrichment.
        """
        url = reverse("process")
        response = api_client.post(url, data=valid_task_payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        
        conv = Conversation.objects.last()
        assert conv is not None
        
        # Check that suggested topics are linked
        suggested_topics = conv.suggested_topics.all()
        assert suggested_topics.count() > 0
        
        # Check that the suggested topic has the expected structure
        first_suggested = suggested_topics.first()
        assert first_suggested.name is not None
        assert first_suggested.description is not None
        assert first_suggested.organization == conv.agent.organization

    @patch("tellme.call_processing.views.create_suggested_topics")
    def test_new_topics_trigger_suggested_topics_creation(
        self, mock_create_suggested_topics, api_client, setup_db, valid_task_payload,
        mock_gcs_utils, mock_deepgram, mock_groq, mock_openai, mock_pydub, mock_processing_user
    ):
        """
        Test that new_topics from enrichment trigger the create_suggested_topics function.
        """
        url = reverse("process")
        response = api_client.post(url, data=valid_task_payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify create_suggested_topics was called with new topics
        mock_create_suggested_topics.assert_called_once()
        call_args = mock_create_suggested_topics.call_args
        
        # Check the arguments passed to create_suggested_topics
        new_topics_arg = call_args[0][0]  # First positional argument
        conversation_file_arg = call_args[0][1]  # Second positional argument
        org_id_arg = call_args[0][2]  # Third positional argument
        
        assert isinstance(new_topics_arg, list)
        assert conversation_file_arg == valid_task_payload["file_name"]
        assert org_id_arg == valid_task_payload["organization_id"]

    @patch("tellme.call_processing.views.create_suggested_topics")
    def test_process_with_empty_new_topics(
        self, mock_create_suggested_topics, api_client, setup_db, valid_task_payload, mock_gcs_utils, 
        mock_deepgram, mock_groq, mock_openai, mock_pydub, mock_processing_user
    ):
        """
        Test processing when enrichment returns empty new_topics list.
        """
        # Modify the existing mock_openai to return empty new_topics
        mock_openai.chat.completions.create.return_value.choices[0].message.content = json.dumps({
            "agent_speaker_labels": ["Speaker 0"],
            "customer_speaker_labels": ["Speaker 1"],
            "topics": ["Billing"],
            "suggested_topics": ["Technical Support"],
            "new_topics": [],  # Empty new topics
            "summary": "Short summary",
            "title": "Test Call",
            "sentiment": 4
        })
        
        url = reverse("process")
        response = api_client.post(url, data=valid_task_payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        
        # Should still create conversation successfully
        conv = Conversation.objects.last()
        assert conv is not None
        
        # Verify create_suggested_topics was called with empty list
        mock_create_suggested_topics.assert_called_once_with(
            [], valid_task_payload["file_name"], valid_task_payload["organization_id"]
        )

    @patch("tellme.call_processing.views.create_suggested_topics")
    def test_process_with_multiple_new_topics(
        self, mock_create_suggested_topics, api_client, setup_db, valid_task_payload, mock_gcs_utils, 
        mock_deepgram, mock_groq, mock_openai, mock_pydub, mock_processing_user
    ):
        """
        Test processing when enrichment returns multiple new topics.
        """
        # Modify the existing mock_openai to return multiple new_topics
        mock_openai.chat.completions.create.return_value.choices[0].message.content = json.dumps({
            "agent_speaker_labels": ["Speaker 0"],
            "customer_speaker_labels": ["Speaker 1"],
            "topics": ["Billing"],
            "suggested_topics": ["Technical Support"],
            "new_topics": [  # Multiple new topics
                {"name": "Product Inquiry", "description": "Customer asking about product features"},
                {"name": "Order Status", "description": "Customer checking on order status"},
                {"name": "Shipping Issue", "description": "Problems with delivery"}
            ],
            "summary": "Short summary",
            "title": "Test Call",
            "sentiment": 4
        })
        
        url = reverse("process")
        response = api_client.post(url, data=valid_task_payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        
        # Verify create_suggested_topics was called with multiple topics
        mock_create_suggested_topics.assert_called_once()
        new_topics_arg = mock_create_suggested_topics.call_args[0][0]
        assert len(new_topics_arg) == 3
        assert new_topics_arg[0]["name"] == "Product Inquiry"
        assert new_topics_arg[1]["name"] == "Order Status"
        assert new_topics_arg[2]["name"] == "Shipping Issue"

    @patch("tellme.call_processing.views.create_suggested_topics")
    def test_create_suggested_topics_error_handling(
        self, mock_create_suggested_topics, api_client, setup_db, valid_task_payload,
        mock_gcs_utils, mock_deepgram, mock_groq, mock_openai, mock_pydub, mock_processing_user
    ):
        """
        Test that errors in create_suggested_topics affect the main processing.
        """
        # Make create_suggested_topics raise an exception
        mock_create_suggested_topics.side_effect = RuntimeError("Suggested topics creation failed")
        
        url = reverse("process")
        response = api_client.post(url, data=valid_task_payload, format="json")
        
        # Processing should still succeed despite suggested topics error
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Conversation should still be created
        conv = Conversation.objects.last()
        assert conv is not None
        assert conv.path == valid_task_payload["file_name"]

    @patch("tellme.call_processing.views.create_suggested_topics")
    def test_process_with_all_topic_types(
        self, mock_create_suggested_topics, api_client, setup_db, valid_task_payload, mock_gcs_utils, 
        mock_deepgram, mock_groq, mock_openai, mock_pydub, mock_processing_user
    ):
        """
        Test processing with all three types of topics: regular, suggested, and new.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db
        
        # Modify the existing mock_openai to return all topic types
        mock_openai.chat.completions.create.return_value.choices[0].message.content = json.dumps({
            "agent_speaker_labels": ["Speaker 0"],
            "customer_speaker_labels": ["Speaker 1"],
            "topics": ["Billing"],  # Existing regular topic
            "suggested_topics": ["Technical Support"],  # Existing suggested topic
            "new_topics": [  # New suggested topics to be created
                {"name": "Product Demo", "description": "Customer requesting product demo"}
            ],
            "summary": "Short summary",
            "title": "Test Call",
            "sentiment": 4
        })
        
        url = reverse("process")
        response = api_client.post(url, data=valid_task_payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        
        # Check the conversation has existing topic types
        conv = Conversation.objects.last()
        assert conv.topics.filter(name="Billing").exists()
        assert conv.suggested_topics.filter(name="Technical Support").exists()
        
        # Verify create_suggested_topics was called with new topic data
        mock_create_suggested_topics.assert_called_once()
        new_topics_arg = mock_create_suggested_topics.call_args[0][0]
        assert len(new_topics_arg) == 1
        assert new_topics_arg[0]["name"] == "Product Demo"
        assert new_topics_arg[0]["description"] == "Customer requesting product demo"

    def test_conversation_stats_updated_after_processing(
        self, api_client, setup_db, valid_task_payload, mock_gcs_utils, mock_deepgram,
        mock_groq, mock_openai, mock_pydub, mock_processing_user
    ):
        """
        Test that topic conversation stats are updated after processing.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Initial stats should be zero
        assert topic.conversation_count == 0
        assert suggested_topic.conversation_count == 0

        url = reverse("process")
        response = api_client.post(url, data=valid_task_payload, format="json")
        assert response.status_code == status.HTTP_200_OK

        # Stats should be updated after processing
        topic.refresh_from_db()
        suggested_topic.refresh_from_db()

        assert topic.conversation_count == 1
        assert suggested_topic.conversation_count == 1

    def test_process_without_customer_id_generates_new_customer(
        self, api_client, setup_db, valid_task_payload, mock_gcs_utils, mock_deepgram,
        mock_groq, mock_openai, mock_pydub, mock_processing_user, mock_dlp
    ):
        """
        Test that processing runs smoothly when customer_id is not provided,
        and that a conversation is created with a generated customer_id.
        """
        # Remove customer_id from the payload to test customer ID generation
        payload_without_customer = valid_task_payload.copy()
        del payload_without_customer["customer_id"]

        # Modify the DLP mock to return a transcript with redacted customer info
        mock_dlp.deidentify_content.return_value.item.value = """
            Speaker 0: My name is [PERSON_NAME] and I was born on [DATE].
            Speaker 1: What? My phone number is [PHONE_NUMBER]
        """

        # Modify the OpenAI mock to include customer_info in the response
        mock_openai.chat.completions.create.return_value.choices[0].message.content = json.dumps({
            "agent_speaker_labels": ["Speaker 0"],
            "customer_speaker_labels": ["Speaker 1"],
            "topics": ["Billing"],
            "suggested_topics": ["Technical Support"],
            "new_topics": [{"name": "Product Inquiry", "description": "Customer asking about product features"}],
            "customer_info": {
                "full_name": "John Doe",
                "birth_date": "1990-01-15"
            },
            "summary": "Short summary",
            "title": "Test Call",
            "sentiment": 4
        })

        url = reverse("process")
        response = api_client.post(url, data=payload_without_customer, format="json")

        # Verify processing succeeds
        assert response.status_code == status.HTTP_200_OK
        assert response.data["message"] == "File processed and saved to DB."

        # Verify conversation was created
        conv = Conversation.objects.last()
        assert conv is not None
        assert conv.path == payload_without_customer["file_name"]
        assert conv.agent.id == payload_without_customer["agent_id"]

        # Verify customer was created with generated customer_id
        assert conv.customer is not None
        assert conv.customer.external_id is not None
        assert len(conv.customer.external_id) == 64  # SHA-256 hash length

        # Verify other conversation details
        assert conv.transcript is not None
        assert conv.title == "Test Call"
        assert conv.summary == "Short summary"
        assert conv.sentiment == 4
