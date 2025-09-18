import pytest
from datetime import datetime, timedelta
from django.urls import reverse
from rest_framework import status
from tellme.call_miner.models import Conversation, OrganizationAPIKey
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
class TestQueueView:
    @pytest.fixture
    def valid_payload(self):
        return {
            "customer_id": "CUST123",
            "agent_id": 123,
            "timestamp": datetime.now(),
            "file": SimpleUploadedFile(
                "test.wav",
                b"Fake File Bytes",
                content_type="audio/wav"
            )
        }

    def test_queue_success(self, api_client, valid_payload, mock_gcs_utils, mock_cloud_tasks,
                           setup_db):
        """
        If the payload is valid, we should get a 202 response and a valid GCS URI in the response.
        A Cloud Task should also be created.
        """
        api_client.credentials(HTTP_AUTHORIZATION=f'X-API-KEY {setup_db[5]}')

        url = reverse("queue")
        response = api_client.post(url, data=valid_payload, format="multipart")

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "file_name" in response.data
        mock_gcs_utils[0].assert_called_once()
        mock_cloud_tasks.assert_called_once()

    def test_unauthenticated_fails(self, api_client, valid_payload, mock_gcs_utils, mock_cloud_tasks,
                                   setup_db):
        """
        If the caller is not authenticated with an API key, the call should be forbidden
        """

        url = reverse("queue")
        response = api_client.post(url, data=valid_payload, format="multipart")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_queue_invalid_agent(self, api_client, valid_payload, mock_gcs_utils, mock_cloud_tasks, setup_db):
        """
        Agent does not exist in the DB, so the request is invalid.
        """
        api_client.credentials(HTTP_AUTHORIZATION=f'X-API-KEY {setup_db[5]}')

        current_payload = valid_payload.copy()
        current_payload["agent_id"] = 99999
        url = reverse("queue")
        response = api_client.post(url, data=current_payload, format="multipart")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock_gcs_utils[0].assert_not_called()
        mock_cloud_tasks.create_task.assert_not_called()

    def test_check_agent_validity_timestamp_overlap(
        self, api_client, setup_db, valid_payload, mock_gcs_utils, mock_deepgram, mock_groq, mock_openai
    ):
        """
        If the agent already has a conversation that hasn't ended by the time the new call starts,
        check_agent_validity() should fail.
        """
        api_client.credentials(HTTP_AUTHORIZATION=f'X-API-KEY {setup_db[5]}')

        # Create a conversation that ends *after* 2024-01-01T12:00:00, such that the creation of a new one starting
        # at that time will be blocked
        overlapping_conv = Conversation.objects.create(
            agent=setup_db[1],
            date=valid_payload['timestamp'] - timedelta(minutes=1),
            duration=120.0,
            transcript="...",
            sentiment=0.0,
            summary="...",
            title="...",
            path="old_file.wav",
            input_tokens=10,
            output_tokens=10,
            customer=setup_db[4]
        )
        overlapping_conv.save()

        queue_url = reverse("queue")
        response = api_client.post(queue_url, data=valid_payload, format="multipart")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid agent. This agent's last call was still taking place" in response.data["message"]

    def test_queue_missing_field(self, api_client, valid_payload, mock_cloud_tasks, setup_db):
        """
        If any required field is missing, the serializer should fail and return a 400.
        """
        api_client.credentials(HTTP_AUTHORIZATION=f'X-API-KEY {setup_db[5]}')

        for field in ['customer_id', 'agent_id', 'timestamp', 'file']:
            current_payload = valid_payload.copy()
            del current_payload[field]
            url = reverse("queue")
            response = api_client.post(url, data=current_payload, format="multipart")
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            mock_cloud_tasks.create_task.assert_not_called()
