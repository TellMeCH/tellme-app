import pytest
import json
from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from tellme.call_miner.models import Conversation, User, Organization, Topic, Customer, Agent, PeriodSummary


@pytest.mark.django_db
class TestSummarizationView:
    @pytest.fixture
    def valid_summarization_payload(self):
        return {
            "object_id": 1,
            "object_type": "<class 'tellme.call_miner.models.Topic'>",
            "summary_period": "quarter",
            "rolling_period": True,
            "task_id": "test-task-123"
        }

    def test_authentication_success(self, settings, setup_db, api_client):
        settings.PROCESSING_PIPELINE_KEY = "test_pipeline_key"
        settings.PROCESSING_PIPELINE_USER = "pipeline@example.com"

        # Create the user expected by the authentication class
        User.objects.create_user("pipeline@example.com", "password", 'pipeline', 'executor')

        # Set the authorization header
        url = reverse("summarize")
        api_client.credentials(HTTP_AUTHORIZATION="Token test_pipeline_key")
        response = api_client.post(url, data={}, format="json")

        # Ensure the response shows a failed body payload validation (authentication worked)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_authentication_failure(self, settings, setup_db, api_client):
        settings.PROCESSING_PIPELINE_KEY = "test_pipeline_key"
        settings.PROCESSING_PIPELINE_USER = "pipeline@example.com"

        # Missing user setup
        url = reverse("summarize")
        api_client.credentials(HTTP_AUTHORIZATION="Token wrong_key")
        response = api_client.post(url, data={}, format="json")

        # Ensure authentication failure
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_summarize_missing_object_id(self, api_client, setup_db, mock_processing_user):
        url = reverse("summarize")
        response = api_client.post(url, data={}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_summarize_unsupported_object_type(self, api_client, setup_db, valid_summarization_payload, mock_processing_user):
        payload = valid_summarization_payload.copy()
        payload["object_type"] = "<class 'tellme.call_miner.models.UnsupportedModel'>"

        url = reverse("summarize")
        response = api_client.post(url, data=payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Unsupported object type" in response.data["error"]

    def test_summarize_object_not_found(self, api_client, setup_db, valid_summarization_payload, mock_processing_user):
        payload = valid_summarization_payload.copy()
        payload["object_id"] = 99999  # Non-existent ID

        url = reverse("summarize")
        response = api_client.post(url, data=payload, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.data["error"]

    @patch("tellme.call_processing.views.MetaSummarizer")
    @patch("tellme.call_processing.views.create_periodsummary")
    def test_summarize_topic_success(self, mock_create_periodsummary, mock_summarizer_class, api_client, setup_db, valid_summarization_payload, mock_processing_user):
        """
        Test successful summarization of a Topic object.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Mock the MetaSummarizer instance and its return value
        mock_summarizer = Mock()
        mock_summarizer.allowed_objects = ["<class 'tellme.call_miner.models.Topic'>"]
        mock_summarizer.return_value = (
            {
                "Reasons for Calling": "Billing issues, Technical support",
                "Churn Potential": "Medium risk due to unresolved billing",
                "Suggested Actions": "Improve billing process, faster resolution"
            },
            conversation.date,  # latest_date
            1,  # call_count
            "2025-Q1"  # label
        )
        mock_summarizer_class.return_value = mock_summarizer

        # Mock create_periodsummary to return a mock PeriodSummary
        mock_period_summary = Mock()
        mock_period_summary.id = 123
        mock_create_periodsummary.return_value = mock_period_summary

        payload = valid_summarization_payload.copy()
        payload["object_id"] = topic.id

        url = reverse("summarize")
        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert "call_count" in response.data
        assert "period_label" in response.data
        mock_summarizer.assert_called_once()
        mock_create_periodsummary.assert_called_once()

    @patch("tellme.call_processing.views.MetaSummarizer")
    def test_summarize_customer_success(self, mock_summarizer_class, api_client, setup_db, valid_summarization_payload, mock_processing_user):
        """
        Test successful summarization of a Customer object.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Mock the MetaSummarizer instance
        mock_summarizer = Mock()
        mock_summarizer.allowed_objects = ["<class 'tellme.call_miner.models.Customer'>"]
        mock_summarizer.return_value = (
            {
                "Favorite Products/Services": "Premium subscription",
                "Churn Potential": "Low risk, satisfied customer",
                "Customer Value": "High value customer"
            },
            conversation.date,
            1,
            "2025-Q1"
        )
        mock_summarizer_class.return_value = mock_summarizer

        payload = valid_summarization_payload.copy()
        payload["object_id"] = customer.id
        payload["object_type"] = "<class 'tellme.call_miner.models.Customer'>"

        with patch("tellme.call_processing.views.create_periodsummary") as mock_create_periodsummary:
            mock_period_summary = Mock()
            mock_period_summary.id = 456
            mock_create_periodsummary.return_value = mock_period_summary

            url = reverse("summarize")
            response = api_client.post(url, data=payload, format="json")

            assert response.status_code == status.HTTP_200_OK
            assert "message" in response.data
            mock_summarizer.assert_called_once()

    @patch("tellme.call_processing.views.MetaSummarizer")
    def test_summarize_agent_success(self, mock_summarizer_class, api_client, setup_db, valid_summarization_payload, mock_processing_user):
        """
        Test successful summarization of an Agent object.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Mock the MetaSummarizer instance
        mock_summarizer = Mock()
        mock_summarizer.allowed_objects = ["<class 'tellme.call_miner.models.Agent'>"]
        mock_summarizer.return_value = (
            {
                "Recurring Issues": "Billing and technical support",
                "First Call Resolution Rate": "85%",
                "Language Appropriateness": "Professional and empathetic"
            },
            conversation.date,
            1,
            "2025-Q1"
        )
        mock_summarizer_class.return_value = mock_summarizer

        payload = valid_summarization_payload.copy()
        payload["object_id"] = agent.id
        payload["object_type"] = "<class 'tellme.call_miner.models.Agent'>"

        with patch("tellme.call_processing.views.create_periodsummary") as mock_create_periodsummary:
            mock_period_summary = Mock()
            mock_period_summary.id = 789
            mock_create_periodsummary.return_value = mock_period_summary

            url = reverse("summarize")
            response = api_client.post(url, data=payload, format="json")

            assert response.status_code == status.HTTP_200_OK
            assert "message" in response.data
            mock_summarizer.assert_called_once()

    @patch("tellme.call_processing.views.MetaSummarizer")
    def test_summarize_no_conversations_found(self, mock_summarizer_class, api_client, setup_db, valid_summarization_payload, mock_processing_user):
        """
        Test summarization when no conversations are found for the period.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Mock the MetaSummarizer to return None (no conversations)
        mock_summarizer = Mock()
        mock_summarizer.allowed_objects = ["<class 'tellme.call_miner.models.Topic'>"]
        mock_summarizer.return_value = (None, None, 0, "2025-Q1")
        mock_summarizer_class.return_value = mock_summarizer

        payload = valid_summarization_payload.copy()
        payload["object_id"] = topic.id

        url = reverse("summarize")
        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "No conversations found" in response.data["message"]

    @patch("tellme.call_processing.views.MetaSummarizer")
    def test_summarize_with_task_id(self, mock_summarizer_class, api_client, setup_db, valid_summarization_payload, mock_processing_user):
        """
        Test that task_id is properly passed through the summarization process.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        mock_summarizer = Mock()
        mock_summarizer.allowed_objects = ["<class 'tellme.call_miner.models.Topic'>"]
        mock_summarizer.return_value = ({"summary": "test"}, conversation.date, 1, "2025-Q1")
        mock_summarizer_class.return_value = mock_summarizer

        payload = valid_summarization_payload.copy()
        payload["object_id"] = topic.id
        payload["task_id"] = "unique-task-456"

        with patch("tellme.call_processing.views.create_periodsummary") as mock_create_periodsummary:
            mock_period_summary = Mock()
            mock_period_summary.id = 999
            mock_create_periodsummary.return_value = mock_period_summary

            url = reverse("summarize")
            response = api_client.post(url, data=payload, format="json")

            assert response.status_code == status.HTTP_200_OK

            # Verify the task_id was included in the trace_data
            trace_data = mock_summarizer.call_args[0][3]
            assert trace_data['metadata']['task_id'] == "unique-task-456"

    @patch("tellme.call_processing.views.MetaSummarizer")
    def test_summarize_different_periods(self, mock_summarizer_class, api_client, setup_db, valid_summarization_payload, mock_processing_user):
        """
        Test summarization with different time periods.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        mock_summarizer = Mock()
        mock_summarizer.allowed_objects = ["<class 'tellme.call_miner.models.Topic'>"]
        mock_summarizer.return_value = ({"summary": "test"}, conversation.date, 1, "2025-Q1")
        mock_summarizer_class.return_value = mock_summarizer

        periods = [
            ("week", False),
            ("month", True),
            ("quarter", False)
        ]

        with patch("tellme.call_processing.views.create_periodsummary") as mock_create_periodsummary:
            mock_period_summary = Mock()
            mock_period_summary.id = 111
            mock_create_periodsummary.return_value = mock_period_summary

            for period, rolling in periods:
                payload = valid_summarization_payload.copy()
                payload["object_id"] = topic.id
                payload["summary_period"] = period
                payload["rolling_period"] = rolling

                url = reverse("summarize")
                response = api_client.post(url, data=payload, format="json")

                assert response.status_code == status.HTTP_200_OK

                # Verify the period parameters were passed correctly
                call_args = mock_summarizer.call_args
                assert call_args[0][1] == period  # summary_period
                assert call_args[0][2] == rolling  # rolling_period

    @patch("tellme.call_processing.views.MetaSummarizer")
    def test_summarize_exception_handling(self, mock_summarizer_class, api_client, setup_db, valid_summarization_payload, mock_processing_user):
        """
        Test that exceptions during summarization are properly handled.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Mock the MetaSummarizer to raise an exception
        mock_summarizer = Mock()
        mock_summarizer.allowed_objects = ["<class 'tellme.call_miner.models.Topic'>"]
        mock_summarizer.side_effect = RuntimeError("Summarization failed")
        mock_summarizer_class.return_value = mock_summarizer

        payload = valid_summarization_payload.copy()
        payload["object_id"] = topic.id

        url = reverse("summarize")
        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error" in response.data
        assert "Summarization failed" in response.data["error"]

    @patch("tellme.call_processing.views.MetaSummarizer")
    def test_summarize_trace_data_structure(self, mock_summarizer_class, api_client, setup_db, valid_summarization_payload, mock_processing_user):
        """
        Test that trace_data is structured correctly for Langfuse tracking.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        mock_summarizer = Mock()
        mock_summarizer.allowed_objects = ["<class 'tellme.call_miner.models.Topic'>"]
        mock_summarizer.return_value = ({"summary": "test"}, conversation.date, 1, "2025-Q1")
        mock_summarizer_class.return_value = mock_summarizer

        payload = valid_summarization_payload.copy()
        payload["object_id"] = topic.id

        with patch("tellme.call_processing.views.create_periodsummary") as mock_create_periodsummary:
            mock_period_summary = Mock()
            mock_period_summary.id = 222
            mock_create_periodsummary.return_value = mock_period_summary

            url = reverse("summarize")
            response = api_client.post(url, data=payload, format="json")

            assert response.status_code == status.HTTP_200_OK

            # Verify trace_data structure
            trace_data = mock_summarizer.call_args[0][3]

            assert 'name' in trace_data
            assert 'tags' in trace_data
            assert 'metadata' in trace_data

            metadata = trace_data['metadata']
            assert 'organization' in metadata
            assert 'object' in metadata
            assert 'id' in metadata
            assert 'period' in metadata
            assert 'rolling' in metadata
            assert 'task_id' in metadata

    @patch("tellme.call_processing.views.create_periodsummary")
    @patch("tellme.call_processing.views.MetaSummarizer")
    def test_create_periodsummary_integration(self, mock_summarizer_class, mock_create_periodsummary, api_client, setup_db, valid_summarization_payload, mock_processing_user):
        """
        Test that create_periodsummary is called with correct parameters.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        summary_data = {
            "Reasons for Calling": "Billing issues",
            "Churn Potential": "Medium risk"
        }

        mock_summarizer = Mock()
        mock_summarizer.allowed_objects = ["<class 'tellme.call_miner.models.Topic'>"]
        mock_summarizer.return_value = (summary_data, conversation.date, 5, "2025-Q1")
        mock_summarizer_class.return_value = mock_summarizer

        mock_period_summary = Mock()
        mock_period_summary.id = 555
        mock_create_periodsummary.return_value = mock_period_summary

        payload = valid_summarization_payload.copy()
        payload["object_id"] = topic.id
        payload["summary_period"] = "month"

        url = reverse("summarize")
        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_200_OK

        # Verify create_periodsummary was called with correct parameters
        mock_create_periodsummary.assert_called_once()
        call_args = mock_create_periodsummary.call_args

        assert call_args[1]['obj'] == topic
        assert call_args[1]['summary'] == summary_data
        assert call_args[1]['latest_date'] == conversation.date
        assert call_args[1]['call_count'] == 5
        assert call_args[1]['label'] == "2025-Q1"
        assert call_args[1]['period'] == "month"