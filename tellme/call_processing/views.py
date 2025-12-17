import logging
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from tellme.call_processing.serializers import (WebhookProcessingSerializer, QueueRecordingSerializer,
                                         ProcessRecordingSerializer, SummarizationSerializer,
                                         TicketCreationSerializer)
from tellme.call_processing.authentication import OrganizationAPIKeyAuthentication, ProcessingKeyAuthentication
from tellme.call_processing.permissions import IsAuthenticatedOrganization
from tellme.call_processing.utils import processing_utils, ticket_utils
from tellme.call_processing.utils.call_processing import CallProcessingPipeline
from tellme.call_processing.utils.meta_summarization import MetaSummarizer
from tellme.call_processing.utils.db_handler import (
    check_same_path_conversations, create_conversation, create_suggested_topics, trigger_summarization_tasks,
    get_object_by_class_string_and_id, create_periodsummary, retrieve_data_for_ticket
)
from tellme.call_processing.utils.webhook_processing import process_webhook_recordings

logger = logging.getLogger('django')


class WebhookProcessingView(APIView):
    """
    Handle incoming webhook notifications for finalized calls.

    This view processes webhook notifications indicating a finalized call, then calls the respective API
    (e.g., the Avaya Communications API) to download the recordings of the call. Once the call recordings
    are downloaded, they are uploaded to GCS and queued for processing.
    """
    authentication_classes = [OrganizationAPIKeyAuthentication]
    permission_classes = [IsAuthenticatedOrganization]
    serializer_class = WebhookProcessingSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        call_sid = data.get("call_sid")
        customer_id = data.get("customer_id")
        agent_id = data.get("agent_id")
        timestamp = data.get("timestamp")
        call_status = data.get("call_status", "").lower()

        organization = request.user
        logger.info(f"Received webhook. Organization: {organization.id}, CallSid: {call_sid}")

        # Check call_status to ensure the call is indeed finalized
        if call_status not in ("completed", "finalized"):
            logger.info(f"Call {call_sid} not finalized yet (status={call_status}). Skipping.")
            return Response({"message": f"Call not finalized (status={call_status})."},
                            status=status.HTTP_200_OK)

        # Delegate processing logic, passing the organization object
        try:
            recordings_folder = process_webhook_recordings(
                call_sid=call_sid,
                organization=organization,
                customer_id=customer_id,
                agent_id=agent_id,
                timestamp=timestamp,
                logger=logger
            )
        except RuntimeError as exc:
            logger.error(f"process_webhook_recordings() failed: {str(exc)}")
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Queue processing with the downloaded data
        message, status_code = processing_utils.upload_file_and_create_processing_task(
            recordings_folder,
            agent_id,
            customer_id,
            organization.id,
            timestamp,
            logger,
        )

        return Response(message, status=status_code)


class QueueRecordingView(APIView):
    """
    Queue call recordings for processing via Cloud Tasks.

    This API view has the sole purpose of queueing a call processing task on a predefined Cloud Tasks Manager.
    The view expects a recording file in the provided data and uploads it to GCS before queueing.
    Only API-token bearing requests should have permission to run this view.
    """
    serializer_class = QueueRecordingSerializer
    authentication_classes = [OrganizationAPIKeyAuthentication]
    permission_classes = [IsAuthenticatedOrganization]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            organization_id = request.user.id
            customer_id = data.get('customer_id')
            agent_id = data.get('agent_id')
            timestamp = data.get('timestamp')
            file_obj = data.get('file')
            duration = data.get('duration')
            file_format = '.' + file_obj.name.split('.')[-1].lower() if '.' in file_obj.name else None
            file_name = processing_utils.create_storage_path(organization_id, customer_id, agent_id, timestamp, file_format)

            logger.info(f'Execution Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            logger.info(f"Created: {timestamp}")
            logger.info(f"Organization: {organization_id}")
            logger.info(f"File: {file_name}")

            message, status_code = processing_utils.upload_file_and_create_processing_task(
                file_name, agent_id, customer_id, organization_id, timestamp, logger, duration=duration, file_obj=file_obj
            )
            return Response(message, status=status_code)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessRecordingView(APIView):
    """
    Execute the full call processing pipeline on a recording.

    This view carries out all processing steps on a call recording including transcription,
    redaction, enrichment, and revenue analysis. It then persists the results to the database.
    Only the processing pipeline service account should have access to this endpoint.
    """
    serializer_class = ProcessRecordingSerializer
    authentication_classes = [ProcessingKeyAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pipeline = CallProcessingPipeline()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated data
        file_name = serializer.validated_data.get("file_name")
        organization_id = serializer.validated_data.get("organization_id")
        customer_id = serializer.validated_data.get("customer_id")
        agent_id = serializer.validated_data.get("agent_id")
        timestamp = serializer.validated_data.get("timestamp")
        transcription_method = serializer.validated_data.get("transcription_method")
        enrichment_method = serializer.validated_data.get("enrichment_method")

        logger.info(f"Processing file {file_name}")
        processing_start = datetime.datetime.now()

        already_exists = check_same_path_conversations(file_name)
        if already_exists:
            return Response(
                {"message": "File has already been processed and saved to DB."},
                status=status.HTTP_200_OK
            )

        try:
            enriched_data = self.pipeline(
                file_name=file_name,
                organization_id=organization_id,
                customer_id=customer_id,
                agent_id=agent_id,
                timestamp=timestamp,
                transcription_method=transcription_method,
                enrichment_method=enrichment_method
            )
        except RuntimeError as exc:
            logger.error(f"Processing Pipeline Failed: {str(exc)}")
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elapsed_time = (datetime.datetime.now() - processing_start).seconds
        logger.info(f"Processed file {file_name}, required {elapsed_time} seconds")

        try:
            # Persist the conversation or any other records as needed
            conversation = create_conversation(**enriched_data)

            # Handle new suggested topics
            create_suggested_topics(enriched_data['new_topics'], file_name, organization_id)

            # Trigger summarization tasks for associated objects
            trigger_summarization_tasks(conversation)
        except RuntimeError as exc:
            logger.error(f"Could not store results of Processing Pipeline: {str(exc)}")
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {"message": "File processed and saved to DB."},
            status=status.HTTP_200_OK
        )


class SummarizationView(APIView):
    """
    Execute summarization for a specific object (Topic, Customer, or Agent).

    This view carries out summarization for the specified object using the existing
    summary mining logic. It checks for newer tasks in the queue before proceeding
    and only creates summaries if they need to be refreshed.
    """
    serializer_class = SummarizationSerializer
    authentication_classes = [ProcessingKeyAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.summarizer = MetaSummarizer()

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        logger.debug(f"Received payload: {request.data}")
        serializer.is_valid(raise_exception=True)

        # Extract validated data
        object_id = serializer.validated_data.get("object_id")
        object_type = serializer.validated_data.get("object_type")  # str(type(obj))
        summary_period = serializer.validated_data.get("summary_period")
        rolling_period = serializer.validated_data.get("rolling_period")
        task_id = serializer.validated_data.get("task_id")

        logger.info(f"Processing summarization for {object_type} {object_id}")

        if object_type not in self.summarizer.allowed_objects:
            message = f"Unsupported object type: {object_type}"
            logger.error(message)
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

        # Get the object instance
        try:
            obj = get_object_by_class_string_and_id(object_type, object_id)
        except ObjectDoesNotExist:
            message = f"Object with id {object_id} not found for type {object_type}"
            logger.error(message)
            return Response({"error": message}, status=status.HTTP_404_NOT_FOUND)
        except ContentType.DoesNotExist:
            message = f"Unsupported object type: {object_type}"
            logger.error(message)
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create trace data for langfuse tracking
            trace_data = {
                'name': 'get_summary_data',
                'tags': [settings.TELLME_ENV],
                'metadata': {
                    'organization': obj.organization,
                    'object': object_type,
                    'id': object_id,
                    'period': summary_period,
                    'rolling': rolling_period,
                    'task_id': task_id
                }
            }

            # Call the summarization method
            summary, latest_date, call_count, label = self.summarizer(obj, summary_period, rolling_period, trace_data)

            if summary is None:
                message = f"No conversations found for {object_type} {object_id} in period {label}"
                logger.info(message)
                return Response({"message": message}, status=status.HTTP_200_OK)

            # Save the summary to the database
            period_summary = create_periodsummary(
                obj=obj,
                summary=summary,
                latest_date=latest_date,
                call_count=call_count,
                label=label,
                period=summary_period
            )

            message = f"Summary created/updated for {object_type} {object_id} (period: {label}, calls: {call_count})"
            logger.info(message)

            return Response({
                "message": message,
                "object_type": object_type,
                "object_id": object_id,
                "call_count": call_count,
                "period_label": label
            }, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.error(f"Summarization failed for {object_type} {object_id}: {str(exc)}")
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TicketCreationView(APIView):
    """
    Create a Jira ticket for a specific customer based on their summary data.

    This view retrieves a customer's summary data and creates a Jira ticket
    using the organization's configured Jira credentials.
    """
    serializer_class = TicketCreationSerializer
    authentication_classes = [ProcessingKeyAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Extract validated data
        customer_id = serializer.validated_data.get("customer_id")
        requester_id = serializer.validated_data.get("requester_id")
        logger.info(f"Processing ticket creation for customer {customer_id}")

        try:
            # Retrieve all necessary data for ticket creation
            customer, organization, ticket_title, ticket_description, summary_date, ticket_api_key, requester_email = retrieve_data_for_ticket(customer_id, requester_id)

            # Create the Jira ticket
            ticket_link, ticket_status = ticket_utils.create_ticket(
                ticket_server=organization.ticket_server,
                ticket_account=requester_email,
                ticket_api_key=ticket_api_key,
                ticket_project=organization.ticket_project,
                ticket_description=ticket_description,
                ticket_title=ticket_title
            )

            # Update customer with ticket information
            if ticket_status == 'created':
                customer.ticket_link = ticket_link
                customer.ticket_date = summary_date
                customer.save()

                message = f"Ticket created successfully for customer {customer_id}: {ticket_link}"
                logger.info(message)

                return Response({
                    "message": message,
                    "customer_id": customer_id,
                    "ticket_link": ticket_link,
                    "ticket_status": ticket_status
                }, status=status.HTTP_200_OK)
            else:
                message = f"Failed to create ticket for customer {customer_id}"
                logger.error(message)
                return Response({
                    "error": message,
                    "customer_id": customer_id,
                    "ticket_status": ticket_status
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except ValueError as exc:
            logger.error(str(exc))
            if 'not found' in str(exc):
                status_code = status.HTTP_404_NOT_FOUND
            else:
                status_code = status.HTTP_400_BAD_REQUEST
            return Response({"error": str(exc)}, status=status_code)
        except Exception as exc:
            logger.error(f"Ticket creation failed for customer {customer_id}: {str(exc)}")
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
