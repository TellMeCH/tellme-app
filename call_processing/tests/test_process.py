import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from call_miner.models import Conversation, User


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
            "timestamp": "2024-01-01T12:00:00"
        }

    def test_authentication_success(self, settings, setup_db, api_client):
        settings.PROCESSING_PIPELINE_KEY = "test_pipeline_key"
        settings.PROCESSING_PIPELINE_USER = "pipeline@example.com"

        # Create the user expected by the authentication class
        User.objects.create_user("pipeline", "pipeline@example.com", "password")

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

    def test_process_empty_file(self, api_client, mock_gcs_upload_download, setup_db, valid_task_payload,
                                mock_processing_user):
        mock_gcs_upload_download[1].return_value = b""
        url = reverse("process")
        response = api_client.post(url, data=valid_task_payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "is empty" in response.data["error"]

    @patch("call_processing.views.create_conversation")
    def test_process_success(
            self, mock_create_conversation, api_client, valid_task_payload, setup_db, mock_gcs_upload_download,
            mock_deepgram, mock_openai, mock_pydub, mock_processing_user
    ):
        """
        If everything is valid, the pipeline runs, the conversation is created in DB,
        and we return a 200 OK.
        """
        url = reverse("process")
        response = api_client.post(url, data=valid_task_payload, format="json")
        assert response.status_code == status.HTTP_200_OK
        mock_create_conversation.assert_called_once()
        assert response.data["message"] == "File processed and saved to DB."

    def test_create_conversation_in_db(
            self, api_client, setup_db, valid_task_payload, mock_gcs_upload_download, mock_deepgram, mock_openai,
            mock_pydub, mock_processing_user
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
