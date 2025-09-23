import logging
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from tellme.call_processing.serializers import (WebhookProcessingSerializer, QueueRecordingSerializer,
                                         ProcessRecordingSerializer)
from tellme.call_processing.authentication import OrganizationAPIKeyAuthentication, ProcessingKeyAuthentication
from tellme.call_processing.permissions import IsAuthenticatedOrganization
from tellme.call_processing.utils import queue_utils
from tellme.call_processing.utils.call_processing import CallProcessingPipeline
from tellme.call_processing.utils.db_handler import create_conversation, create_suggested_topics
from tellme.call_processing.utils.webhook_processing import process_webhook_recordings

logger = logging.getLogger('django')


class WebhookProcessingView(APIView):
    """
    This view processes an incoming Webhook notification indicating a finalized call, and then calls the respecitve API
    (f.e. the Avaya Communications API) to download the recordings of the call. Once the call recordings are downloaded,
    they are uploaded to GCS and queued for processing.
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
        message, status_code = queue_utils.upload_and_create_task(
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
    This API view has the sole purpose of queueing a call processing task on a predefined Cloud Tasks Manager.
    The view expects a recording in the provided data.
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
            file_name = queue_utils.create_storage_path(organization_id, customer_id, agent_id, timestamp)

            logger.info(f'Execution Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            logger.info(f"Created: {timestamp}")
            logger.info(f"Organization: {organization_id}")
            logger.info(f"File: {file_name}")

            message, status_code = queue_utils.upload_and_create_task(
                file_name, agent_id, customer_id, organization_id, timestamp, logger, file_obj=file_obj
            )
            return Response(message, status=status_code)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessRecordingView(APIView):
    """
    Carries out the processing steps on a call recording.
    Only the processing pipeline account (PROCESSING_PIPELINE_USER and PROCESSING_PIPELINE_KEY) should have access
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
            create_conversation(**enriched_data)

            # Handle new suggested topics
            create_suggested_topics(enriched_data['new_topics'], file_name, organization_id)
        except RuntimeError as exc:
            logger.error(f"Could not store results of Processing Pipeline: {str(exc)}")
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(
            {"message": "File processed and saved to DB."},
            status=status.HTTP_200_OK
        )
