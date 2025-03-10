import logging
import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from call_processing.serializers import QueueRecordingSerializer, ProcessRecordingSerializer
from call_processing.authentication import OrganizationAPIKeyAuthentication, ProcessingKeyAuthentication
from call_processing.permissions import IsAuthenticatedOrganization
from call_processing.utils import gcs_utils, queue_utils
from call_processing.utils.call_processing import CallProcessingPipeline
from call_processing.utils.db_handler import create_conversation

logger = logging.getLogger('django')


class QueueRecordingView(APIView):
    """
    This API view has the sole purpose of queueing a call processing task on a predefined Cloud Tasks Manager. Moreover,
    it is designed to work in conjunction with a Cloud Tasks Emulator for local development.
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
            customer_id = data['customer_id']
            agent_id = data['agent_id']
            timestamp = data['timestamp']
            file_obj = data['file']
            file_name = f"{organization_id}/{customer_id}_{agent_id}_{timestamp.isoformat()}.wav"

            logger.info(f'Execution Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            logger.info(f"Created: {timestamp}")
            logger.info(f"Organization: {organization_id}")
            logger.info(f"File: {file_name}")

            message, status_code = queue_utils.upload_and_create_task(
                file_name, file_obj, agent_id, customer_id, organization_id, timestamp, logger
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
        file_name = serializer.validated_data["file_name"]
        organization_id = serializer.validated_data.get("organization_id")
        customer_id = serializer.validated_data.get("customer_id")
        agent_id = serializer.validated_data.get("agent_id")
        timestamp = serializer.validated_data.get("timestamp")

        # Download file from GCS
        file_data = gcs_utils.download_from_gcs(file_name)

        if not file_data:
            return Response(
                {"error": f"Specified file {file_name} is empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info(f"Processing file {file_name}, size {len(file_data)} bytes.")
        processing_start = datetime.datetime.now()

        # Enrich data using your pipeline
        enriched_data = self.pipeline(
            file_data,
            {
                "file_name": file_name,
                "organization_id": organization_id,
                "customer_id": customer_id,
                "agent_id": agent_id,
                "timestamp": timestamp
            }
        )

        elapsed_time = (datetime.datetime.now() - processing_start).seconds
        logger.info(f"Processed file {file_name}, required {elapsed_time} seconds")

        # Persist the conversation or any other records as needed
        create_conversation(**enriched_data)

        return Response(
            {"message": "File processed and saved to DB."},
            status=status.HTTP_200_OK
        )
