import pytest
from unittest.mock import patch, Mock
from django.urls import reverse
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from tellme.call_miner.models import User, Organization, Customer, Agent, PeriodSummary, Conversation
from datetime import datetime
import zoneinfo


@pytest.mark.django_db
class TestTicketCreationView:
    @pytest.fixture
    def valid_ticket_payload(self):
        return {
            "customer_id": 1,
            "task_id": "test-task-123"
        }

    @pytest.fixture
    def organization_with_jira_config(self, setup_db):
        """Create an organization with Jira configuration."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db
        org.ticket_account = "test@example.atlassian.net"
        org.ticket_project = "PROJ"
        org.store_ticket_key("test-api-key-123")
        org.save()
        return org, customer, conversation

    def test_authentication_success(self, settings, setup_db, api_client):
        settings.PROCESSING_PIPELINE_KEY = "test_pipeline_key"
        settings.PROCESSING_PIPELINE_USER = "pipeline@example.com"

        # Create the user expected by the authentication class
        User.objects.create_user("pipeline@example.com", "password", 'pipeline', 'executor')

        # Set the authorization header
        url = reverse("create_ticket")
        api_client.credentials(HTTP_X_TELLME_TOKEN="Token test_pipeline_key")
        response = api_client.post(url, data={}, format="json")

        # Ensure the response shows a failed body payload validation (authentication worked)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_authentication_failure(self, settings, setup_db, api_client):
        settings.PROCESSING_PIPELINE_KEY = "test_pipeline_key"
        settings.PROCESSING_PIPELINE_USER = "pipeline@example.com"

        # Missing user setup
        url = reverse("create_ticket")
        api_client.credentials(HTTP_X_TELLME_TOKEN="Token wrong_key")
        response = api_client.post(url, data={}, format="json")

        # Ensure authentication failure
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_ticket_creation_missing_customer_id(self, api_client, setup_db, mock_processing_user):
        url = reverse("create_ticket")
        response = api_client.post(url, data={}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_ticket_creation_customer_not_found(self, api_client, setup_db, valid_ticket_payload, mock_processing_user):
        payload = valid_ticket_payload.copy()
        payload["customer_id"] = 99999  # Non-existent ID

        url = reverse("create_ticket")
        response = api_client.post(url, data=payload, format="json")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.data["error"]

    def test_ticket_creation_no_jira_config(self, api_client, setup_db, valid_ticket_payload, mock_processing_user):
        """Test that ticket creation fails when organization has no Jira credentials."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        payload = valid_ticket_payload.copy()
        payload["customer_id"] = customer.id

        url = reverse("create_ticket")
        response = api_client.post(url, data=payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "does not have Jira credentials configured" in response.data["error"]

    @patch("tellme.call_processing.utils.ticket_utils.create_ticket")
    def test_ticket_creation_success(
        self, mock_create_ticket, api_client, organization_with_jira_config, mock_processing_user
    ):
        """Test successful ticket creation."""
        org, customer, conversation = organization_with_jira_config

        # Create summary with Jira ticket fields
        content_type = ContentType.objects.get_for_model(customer.__class__)
        summary_data = {
            'Customer Value': 'High value customer',
            'Churn Potential': 'High risk',
            'Jira Ticket Title': 'Customer Issue - Test',
            'Jira Ticket Body': 'Customer needs immediate attention'
        }
        PeriodSummary.objects.create(
            content_type=content_type,
            object_id=customer.id,
            period_type='eternity',
            period_label='eternity',
            summary=summary_data,
            last_call_at=conversation.date,
            call_count=1
        )

        # Mock successful ticket creation
        mock_create_ticket.return_value = (
            "https://jira.example.com/browse/PROJ-123",
            "created"
        )

        payload = {
            "customer_id": customer.id,
            "task_id": "test-task-123"
        }

        url = reverse("create_ticket")
        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "Ticket created successfully" in response.data["message"]
        assert response.data["ticket_link"] == "https://jira.example.com/browse/PROJ-123"
        assert response.data["ticket_status"] == "created"
        assert response.data["customer_id"] == customer.id

        # Verify ticket was created with correct parameters
        mock_create_ticket.assert_called_once()
        call_args = mock_create_ticket.call_args[1]
        assert call_args["ticket_account"] == "test@example.atlassian.net"
        assert call_args["ticket_project"] == "PROJ"
        assert call_args["ticket_title"] == "Customer Issue - Test"
        assert call_args["ticket_description"] == "Customer needs immediate attention"

        # Verify customer was updated
        customer.refresh_from_db()
        conversation.refresh_from_db()
        assert customer.ticket_link == "https://jira.example.com/browse/PROJ-123"
        assert customer.ticket_date == conversation.date

    @patch("tellme.call_processing.utils.ticket_utils.create_ticket")
    def test_ticket_creation_failure(
        self, mock_create_ticket, api_client, organization_with_jira_config, mock_processing_user
    ):
        """Test failed ticket creation."""
        org, customer, conversation = organization_with_jira_config

        # Create summary with Jira ticket fields
        content_type = ContentType.objects.get_for_model(customer.__class__)
        summary_data = {
            'Customer Value': 'High value customer',
            'Jira Ticket Title': 'Customer Issue',
            'Jira Ticket Body': 'Customer needs help'
        }
        PeriodSummary.objects.create(
            content_type=content_type,
            object_id=customer.id,
            period_type='eternity',
            period_label='eternity',
            summary=summary_data,
            last_call_at=conversation.date,
            call_count=1
        )

        # Mock failed ticket creation
        mock_create_ticket.return_value = (None, "failed")

        payload = {
            "customer_id": customer.id,
            "task_id": "test-task-123"
        }

        url = reverse("create_ticket")
        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to create ticket" in response.data["error"]
        assert response.data["ticket_status"] == "failed"

        # Verify customer was NOT updated
        customer.refresh_from_db()
        assert customer.ticket_link is None
        assert customer.ticket_date is None

    def test_ticket_creation_no_ticket_data_in_summary(
        self, api_client, organization_with_jira_config, mock_processing_user
    ):
        """Test that ticket creation fails when summary has no ticket_data field."""
        org, customer, conversation = organization_with_jira_config

        # Create summary WITHOUT ticket_data
        content_type = ContentType.objects.get_for_model(customer.__class__)
        summary_data = {
            'Customer Value': 'High value customer',
            'Churn Potential': 'Low risk'
        }
        PeriodSummary.objects.create(
            content_type=content_type,
            object_id=customer.id,
            period_type='eternity',
            period_label='eternity',
            summary=summary_data,
            last_call_at=conversation.date,
            call_count=1
        )

        payload = {
            "customer_id": customer.id,
            "task_id": "test-task-123"
        }

        url = reverse("create_ticket")
        response = api_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No valid ticket data found in customer summary for customer" in response.data["error"]


@pytest.mark.django_db
class TestTicketUtilsCreateTicket:
    """Unit tests for the create_ticket utility function."""

    @patch("tellme.call_processing.utils.ticket_utils.JIRA")
    def test_create_ticket_success(self, mock_jira_class):
        """Test successful ticket creation using Jira SDK."""
        from tellme.call_processing.utils.ticket_utils import create_ticket

        # Mock the JIRA instance and created issue
        mock_jira_instance = Mock()
        mock_jira_class.return_value = mock_jira_instance

        mock_issue = Mock()
        mock_issue.key = "PROJ-123"
        mock_jira_instance.create_issue.return_value = mock_issue

        # Call create_ticket
        ticket_link, status = create_ticket(
            ticket_account="test@example.atlassian.net",
            ticket_api_key="test-api-key",
            ticket_project="PROJ",
            ticket_description="Test description",
            ticket_title="Test ticket"
        )

        # Verify JIRA was initialized correctly
        mock_jira_class.assert_called_once_with(
            server="https://example.atlassian.net",
            basic_auth=("test@example.atlassian.net", "test-api-key")
        )

        # Verify create_issue was called with correct parameters
        mock_jira_instance.create_issue.assert_called_once_with(
            fields={
                'project': {'key': 'PROJ'},
                'summary': 'Test ticket',
                'description': 'Test description',
                'issuetype': {'name': 'Task'},
            }
        )

        # Verify return values
        assert ticket_link == "https://example.atlassian.net/browse/PROJ-123"
        assert status == "created"

    @patch("tellme.call_processing.utils.ticket_utils.JIRA")
    def test_create_ticket_jira_error(self, mock_jira_class):
        """Test ticket creation failure due to Jira API error."""
        from tellme.call_processing.utils.ticket_utils import create_ticket
        from jira.exceptions import JIRAError

        # Mock JIRA to raise JIRAError
        mock_jira_instance = Mock()
        mock_jira_class.return_value = mock_jira_instance

        jira_error = JIRAError("Authentication failed")
        jira_error.status_code = 401
        jira_error.text = "Invalid credentials"
        mock_jira_instance.create_issue.side_effect = jira_error

        # Call create_ticket
        ticket_link, status = create_ticket(
            ticket_account="test@example.atlassian.net",
            ticket_api_key="invalid-key",
            ticket_project="PROJ",
            ticket_description="Test description",
            ticket_title="Test ticket"
        )

        # Verify failure
        assert ticket_link is None
        assert status == "failed"

    @patch("tellme.call_processing.utils.ticket_utils.JIRA")
    def test_create_ticket_unexpected_error(self, mock_jira_class):
        """Test ticket creation failure due to unexpected error."""
        from tellme.call_processing.utils.ticket_utils import create_ticket

        # Mock JIRA to raise unexpected exception
        mock_jira_class.side_effect = Exception("Network error")

        # Call create_ticket
        ticket_link, status = create_ticket(
            ticket_account="test@example.atlassian.net",
            ticket_api_key="test-api-key",
            ticket_project="PROJ",
            ticket_description="Test description",
            ticket_title="Test ticket"
        )

        # Verify failure
        assert ticket_link is None
        assert status == "failed"

    @patch("tellme.call_processing.utils.ticket_utils.JIRA")
    def test_create_ticket_domain_extraction_variants(self, mock_jira_class):
        """Test various formats of ticket_account for domain extraction."""
        from tellme.call_processing.utils.ticket_utils import create_ticket

        # Mock the JIRA instance
        mock_jira_instance = Mock()
        mock_jira_class.return_value = mock_jira_instance
        mock_issue = Mock()
        mock_issue.key = "TEST-1"
        mock_jira_instance.create_issue.return_value = mock_issue

        test_cases = [
            ("user@mycompany.atlassian.net", "https://mycompany.atlassian.net"),
            ("mycompany@gmail.com", "https://mycompany.atlassian.net"),
            ("https://custom.atlassian.net", "https://custom.atlassian.net"),
            ("mycompany", "https://mycompany.atlassian.net"),
        ]

        for account, expected_server in test_cases:
            mock_jira_class.reset_mock()

            create_ticket(
                ticket_account=account,
                ticket_api_key="test-key",
                ticket_project="TEST",
                ticket_description="desc",
                ticket_title="title"
            )

            # Verify the server URL was extracted correctly
            call_args = mock_jira_class.call_args
            assert call_args[1]['server'] == expected_server
