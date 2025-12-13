import pytest
from datetime import datetime, timedelta
from django.urls import reverse
from rest_framework import status
from tellme.call_miner.models import Conversation
from django.core.files.uploadedfile import SimpleUploadedFile
from tellme.call_miner.utils.queue_utils import create_summarization_task, check_summarization_tasks


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
        api_client.credentials(HTTP_X_TELLME_API_KEY=f'X-API-KEY {setup_db[5]}')

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
        api_client.credentials(HTTP_X_TELLME_API_KEY=f'X-API-KEY {setup_db[5]}')

        current_payload = valid_payload.copy()
        current_payload["agent_id"] = 99999
        url = reverse("queue")
        response = api_client.post(url, data=current_payload, format="multipart")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock_gcs_utils[0].assert_not_called()
        mock_cloud_tasks.create_processing_task.assert_not_called()

    def test_check_agent_validity_timestamp_overlap(
        self, api_client, setup_db, valid_payload, mock_gcs_utils, mock_cloud_tasks
    ):
        """
        If the agent already has a conversation that hasn't ended by the time the new call starts,
        check_agent_validity() should fail.
        """
        api_client.credentials(HTTP_X_TELLME_API_KEY=f'X-API-KEY {setup_db[5]}')

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
        api_client.credentials(HTTP_X_TELLME_API_KEY=f'X-API-KEY {setup_db[5]}')

        for field in ['agent_id', 'timestamp', 'file']:
            current_payload = valid_payload.copy()
            del current_payload[field]
            url = reverse("queue")
            response = api_client.post(url, data=current_payload, format="multipart")
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            mock_cloud_tasks.create_processing_task.assert_not_called()

    def test_queue_without_customer_id_succeeds(self, api_client, valid_payload, mock_gcs_utils, mock_cloud_tasks, setup_db):
        """
        Test that queue endpoint works correctly when customer_id is not provided.
        The pipeline should be able to generate a customer_id during processing.
        """
        api_client.credentials(HTTP_X_TELLME_API_KEY=f'X-API-KEY {setup_db[5]}')

        # Remove customer_id from payload to test without it
        payload_without_customer = valid_payload.copy()
        del payload_without_customer["customer_id"]

        url = reverse("queue")
        response = api_client.post(url, data=payload_without_customer, format="multipart")

        # Should succeed even without customer_id
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "file_name" in response.data

        # Verify file was uploaded to GCS
        mock_gcs_utils[0].assert_called_once()

        # Verify Cloud Task was created for processing
        mock_cloud_tasks.assert_called_once()

        # Verify the task arguments - customer_id should be None (will be generated during processing)
        task_call_args = mock_cloud_tasks.call_args
        customer_id = task_call_args[0][3]

        assert customer_id is None

    def test_queue_mp3_file_success(self, api_client, valid_payload, mock_gcs_utils, mock_cloud_tasks, setup_db):
        """
        Test that the queue endpoint correctly handles MP3 files and preserves the .mp3 extension.
        """
        api_client.credentials(HTTP_X_TELLME_API_KEY=f'X-API-KEY {setup_db[5]}')

        # Create payload with MP3 file
        mp3_payload = valid_payload.copy()
        mp3_payload["file"] = SimpleUploadedFile(
            "test.mp3",
            b"Fake MP3 File Bytes",
            content_type="audio/mpeg"
        )

        url = reverse("queue")
        response = api_client.post(url, data=mp3_payload, format="multipart")

        # Should succeed with MP3 file
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "file_name" in response.data

        # Verify the file name has .mp3 extension
        file_name = response.data["file_name"]
        assert file_name.endswith('.mp3')

        # Verify file was uploaded to GCS
        mock_gcs_utils[0].assert_called_once()

        # Verify Cloud Task was created for processing
        mock_cloud_tasks.assert_called_once()

    def test_queue_duration_overlap_validation(
        self, api_client, setup_db, valid_payload, mock_gcs_utils, mock_cloud_tasks
    ):
        """
        Test duration-based overlap validation:
        - When duration is provided, calls can be added out of chronological order
        - But they must not have overlapping time ranges with existing calls
        - Tests both directions: new call starting during existing call, and existing call starting during new call
        """
        api_client.credentials(HTTP_X_TELLME_API_KEY=f'X-API-KEY {setup_db[5]}')

        # Create an existing conversation that runs from T+5min to T+7min
        base_time = valid_payload['timestamp']
        existing_conv = Conversation.objects.create(
            agent=setup_db[1],  # setup_db[1] is the agent
            date=base_time + timedelta(minutes=5),
            duration=120.0,  # 2 minutes duration
            transcript="Existing call transcript",
            sentiment=3.0,
            summary="Existing call summary",
            title="Existing call title",
            path="existing_call.wav",
            input_tokens=10,
            output_tokens=10,
            customer=setup_db[4]  # setup_db[4] is the customer
        )
        existing_conv.save()

        queue_url = reverse("queue")

        # Test 1: Queue a call with duration that comes BEFORE the existing call (no overlap)
        # This call is at T+0 with 60s duration, existing call is at T+5min, so no overlap
        payload_no_overlap = valid_payload.copy()
        payload_no_overlap["duration"] = 60.0  # 1 minute
        payload_no_overlap["file"] = SimpleUploadedFile(
            "test1.wav",
            b"Fake File Bytes",
            content_type="audio/wav"
        )
        response = api_client.post(queue_url, data=payload_no_overlap, format="multipart")

        # Should succeed because there's no overlap
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "file_name" in response.data

        # Test 2: Queue a call where new call STARTS during existing call
        # This call starts at T+6min, which is during the existing call (T+5min to T+7min)
        payload_overlap_case1 = valid_payload.copy()
        payload_overlap_case1["duration"] = 60.0
        payload_overlap_case1["timestamp"] = base_time + timedelta(minutes=6)
        payload_overlap_case1["file"] = SimpleUploadedFile(
            "test2.wav",
            b"Fake File Bytes",
            content_type="audio/wav"
        )
        response = api_client.post(queue_url, data=payload_overlap_case1, format="multipart")

        # Should fail because the new call starts during an existing call
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "overlaps" in response.data["message"]

        # Test 3: Queue a call where existing call STARTS during new call
        # This call starts at T+4min with 180s duration (ends at T+7min)
        # The existing call at T+5min starts during this new call
        payload_overlap_case2 = valid_payload.copy()
        payload_overlap_case2["duration"] = 180.0  # 3 minutes
        payload_overlap_case2["timestamp"] = base_time + timedelta(minutes=4)
        payload_overlap_case2["file"] = SimpleUploadedFile(
            "test3.wav",
            b"Fake File Bytes",
            content_type="audio/wav"
        )
        response = api_client.post(queue_url, data=payload_overlap_case2, format="multipart")

        # Should fail because an existing call starts during the new call
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "overlaps" in response.data["message"]


@pytest.mark.django_db
class TestSummarizationQueue:
    """Test the summarization queue functionality."""

    def test_create_summarization_task_success(self, mock_summarization_tasks, setup_db):
        """
        Test that create_summarization_task creates a task with correct parameters.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        task_id = create_summarization_task(
            object_id=topic.id,
            object_type='topic',
            summary_period='quarter',
            rolling_period=True
        )

        # Verify task was created and returned task ID
        assert task_id == "test-task-id-12345"
        mock_summarization_tasks.assert_called_once()

        # Verify the call arguments
        call_args = mock_summarization_tasks.call_args
        assert call_args[1]['object_id'] == topic.id
        assert call_args[1]['object_type'] == 'topic'
        assert call_args[1]['summary_period'] == 'quarter'
        assert call_args[1]['rolling_period'] is True

    def test_create_summarization_task_different_object_types(self, mock_summarization_tasks, setup_db):
        """
        Test create_summarization_task with different object types (topic, customer, agent).
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        test_cases = [
            (topic.id, 'topic', 'quarter', True),
            (customer.id, 'customer', 'quarter', True),
            (agent.id, 'agent', 'month', False)
        ]

        for object_id, object_type, period, rolling in test_cases:
            mock_summarization_tasks.reset_mock()

            task_id = create_summarization_task(
                object_id=object_id,
                object_type=object_type,
                summary_period=period,
                rolling_period=rolling
            )

            assert task_id == "test-task-id-12345"
            mock_summarization_tasks.assert_called_once()

            # Verify correct parameters were passed
            call_args = mock_summarization_tasks.call_args
            assert call_args[1]['object_id'] == object_id
            assert call_args[1]['object_type'] == object_type
            assert call_args[1]['summary_period'] == period
            assert call_args[1]['rolling_period'] == rolling

    def test_create_summarization_task_with_custom_task_id(self, mock_summarization_tasks, setup_db):
        """
        Test create_summarization_task with a custom task ID.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        custom_task_id = "custom-task-id-789"

        task_id = create_summarization_task(
            object_id=topic.id,
            object_type='topic',
            summary_period='month',
            rolling_period=False,
            task_id=custom_task_id
        )

        # Should return the mocked task ID
        assert task_id == "test-task-id-12345"
        mock_summarization_tasks.assert_called_once()


@pytest.mark.django_db
class TestCheckSummarizationTasks:
    """Test the check_summarization_tasks function."""

    def test_check_no_matching_tasks_in_empty_queue(self, setup_db):
        """
        Test that check_summarization_tasks returns False when queue is empty.
        """
        from unittest.mock import patch, MagicMock

        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        with patch('tellme.call_miner.utils.summary_utils.get_tasks_client_and_parent') as mock_get_client:
            mock_client = MagicMock()
            mock_parent = "projects/test/locations/us-central1/queues/test-queue"
            mock_get_client.return_value = (mock_client, mock_parent)

            # Mock empty task list
            mock_client.list_tasks.return_value = []

            result = check_summarization_tasks(
                object_id=topic.id,
                object_type=str(type(topic)),
                summary_period='quarter',
                rolling_period=True
            )

            assert result is False
            mock_client.list_tasks.assert_called_once_with(parent=mock_parent)

    def test_check_matching_task_exists_returns_true(self, setup_db):
        """
        Test that check_summarization_tasks returns True when matching task exists.
        """
        from unittest.mock import patch, MagicMock
        import json

        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        with patch('tellme.call_miner.utils.summary_utils.get_tasks_client_and_parent') as mock_get_client:
            mock_client = MagicMock()
            mock_parent = "projects/test/locations/us-central1/queues/test-queue"
            mock_get_client.return_value = (mock_client, mock_parent)

            # Create mock task that matches our parameters
            matching_payload = {
                'object_id': topic.id,
                'object_type': str(type(topic)),
                'summary_period': 'quarter',
                'rolling_period': True,
                'task_id': 'test-task-123'
            }

            mock_task = MagicMock()
            mock_task.http_request.body = json.dumps(matching_payload).encode()
            mock_client.list_tasks.return_value = [mock_task]

            result = check_summarization_tasks(
                object_id=topic.id,
                object_type=str(type(topic)),
                summary_period='quarter',
                rolling_period=True
            )

            assert result is True

    def test_check_non_matching_tasks_returns_false(self, setup_db):
        """
        Test that check_summarization_tasks returns False when tasks exist but don't match.
        """
        from unittest.mock import patch, MagicMock
        import json

        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        with patch('tellme.call_miner.utils.summary_utils.get_tasks_client_and_parent') as mock_get_client:
            mock_client = MagicMock()
            mock_parent = "projects/test/locations/us-central1/queues/test-queue"
            mock_get_client.return_value = (mock_client, mock_parent)

            # Create mock tasks that don't match our parameters
            non_matching_payloads = [
                {
                    'object_id': topic.id + 1,  # Different object_id
                    'object_type': str(type(topic)),
                    'summary_period': 'quarter',
                    'rolling_period': True,
                    'task_id': 'test-task-123'
                },
                {
                    'object_id': topic.id,
                    'object_type': str(type(customer)),  # Different object_type
                    'summary_period': 'quarter',
                    'rolling_period': True,
                    'task_id': 'test-task-456'
                },
                {
                    'object_id': topic.id,
                    'object_type': str(type(topic)),
                    'summary_period': 'month',  # Different period
                    'rolling_period': True,
                    'task_id': 'test-task-789'
                },
                {
                    'object_id': topic.id,
                    'object_type': str(type(topic)),
                    'summary_period': 'quarter',
                    'rolling_period': False,  # Different rolling setting
                    'task_id': 'test-task-101'
                }
            ]

            mock_tasks = []
            for payload in non_matching_payloads:
                mock_task = MagicMock()
                mock_task.http_request.body = json.dumps(payload).encode()
                mock_tasks.append(mock_task)

            mock_client.list_tasks.return_value = mock_tasks

            result = check_summarization_tasks(
                object_id=topic.id,
                object_type=str(type(topic)),
                summary_period='quarter',
                rolling_period=True
            )

            assert result is False

    def test_check_handles_invalid_task_payloads(self, setup_db):
        """
        Test that check_summarization_tasks handles tasks with invalid JSON payloads gracefully.
        """
        from unittest.mock import patch, MagicMock

        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        with patch('tellme.call_miner.utils.summary_utils.get_tasks_client_and_parent') as mock_get_client:
            mock_client = MagicMock()
            mock_parent = "projects/test/locations/us-central1/queues/test-queue"
            mock_get_client.return_value = (mock_client, mock_parent)

            # Create mock tasks with invalid payloads
            invalid_task1 = MagicMock()
            invalid_task1.http_request.body = b"invalid json"

            invalid_task2 = MagicMock()
            invalid_task2.http_request.body = b""

            # Task without http_request
            invalid_task3 = MagicMock()
            del invalid_task3.http_request

            mock_client.list_tasks.return_value = [invalid_task1, invalid_task2, invalid_task3]

            result = check_summarization_tasks(
                object_id=topic.id,
                object_type=str(type(topic)),
                summary_period='quarter',
                rolling_period=True
            )

            # Should return False and not crash
            assert result is False

    def test_check_handles_api_errors_gracefully(self, setup_db):
        """
        Test that check_summarization_tasks handles Cloud Tasks API errors gracefully.
        """
        from unittest.mock import patch

        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        with patch('tellme.call_miner.utils.summary_utils.get_tasks_client_and_parent') as mock_get_client:
            # Mock API error when getting client
            mock_get_client.side_effect = Exception("Cloud Tasks API error")

            result = check_summarization_tasks(
                object_id=topic.id,
                object_type=str(type(topic)),
                summary_period='quarter',
                rolling_period=True
            )

            # Should return False (safer to allow task creation) and not crash
            assert result is False

# A brief summary of summarization testing
# - test_queue: Tests create_summarization_task in call_miner/utils/summary_utils.py
# - test_agents, test_customers, test_topics: Test the whole summary-data view, as well as get_or_create_summary
# - test_db_handler: Tests call_processing/utils/db_handler.py's trigger_summarization_tasks
# - test_models: Tests check_and_create_summarization_task, which gets a call from both get_or_create_summary and trigger_summarization_tasks