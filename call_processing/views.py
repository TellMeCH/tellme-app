import json
import grpc
import logging
import datetime
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from call_processing.serializers import QueueRecordingSerializer, ProcessRecordingSerializer
from call_processing.authentication import OrganizationAPIKeyAuthentication
from call_processing.utils.gcs_utils import upload_to_gcs, download_from_gcs
from call_processing.utils.call_processing import CallProcessingPipeline
from call_processing.utils.db_handler import check_agent_validity, create_conversation

logger = logging.getLogger('django')


class QueueRecordingView(APIView):
    """
    This API view has the sole purpose of queueing a call processing task on a predefined Cloud Tasks Manager. Moreover,
    it is designed to work in conjunction with a Cloud Tasks Emulator for local development.
    Only API-token bearing requests should have permission to run this view.
    """
    serializer_class = QueueRecordingSerializer
    authentication_class = OrganizationAPIKeyAuthentication

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            organization_id = request.user
            customer_id = data['customer_id']
            agent_id = data['agent_id']
            timestamp = data['timestamp']
            file_obj = data['file']
            file_name = f"{organization_id}/{customer_id}_{agent_id}_{timestamp.isoformat()}.wav"

            logger.info(f'Execution Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            logger.info(f"Created: {timestamp}")
            logger.info(f"Organization: {organization_id}")
            logger.info(f"File: {file_name}")

            # Check Validity of Request
            agent_valid, validity_message = check_agent_validity(agent_id, organization_id, timestamp)

            if agent_valid:
                # Upload to GCS
                gcs_uri = upload_to_gcs(file_obj, file_name)

                # Create a task to process this recording
                payload = {
                    "file_name": file_name,
                    "organization_id": organization_id,
                    "customer_id": customer_id,
                    "agent_id": agent_id,
                    "timestamp": timestamp.isoformat()
                }
                task = {
                    "http_request": {
                        "http_method": tasks_v2.HttpMethod.POST,
                        "url": settings.CALL_PROCESSING_ENDPOINT,
                        "headers": {"Content-Type": "application/json"},
                        "body": json.dumps(payload).encode()
                    }
                }
                # Specify the task schedule time
                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromDatetime(datetime.datetime.now(datetime.UTC))
                task['schedule_time'] = timestamp

                # Create a Cloud Task Client, using the Cloud Tasks emulator when necessary
                if settings.TASKS_EMULATOR_ADDRESS:
                    # Create a gRPC channel to the local emulator
                    channel = grpc.insecure_channel(settings.TASKS_EMULATOR_ADDRESS)
                    transport = tasks_v2.services.cloud_tasks.transports.CloudTasksGrpcTransport(channel=channel)
                    client = tasks_v2.CloudTasksClient(transport=transport)
                else:
                    # Use the default CloudTasksClient configuration
                    client = tasks_v2.CloudTasksClient()

                # Create the task in its parent
                parent = client.queue_path(
                    settings.GOOGLE_CLOUD_PROJECT,
                    settings.REGION,
                    settings.CLOUD_TASKS_QUEUE_NAME
                )
                logger.info(f'Creating task in queue with parent {parent}')
                _ = client.create_task(parent=parent, task=task)
                logger.info(f'Created task in {settings.CLOUD_TASKS_QUEUE_NAME}')
                return Response(
                    {"message": "File queued for processing.", "gcs_uri": gcs_uri}, status=status.HTTP_202_ACCEPTED
                )
            else:
                return Response({"message": f"Invalid agent. {validity_message}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessRecordingView(APIView):
    """
    Carries out the processing steps on a call recording.
    Only the processing pipeline account (PROCESSING_PIPELINE_USER and PROCESSING_PIPELINE_KEY) should have access
    """
    serializer_class = ProcessRecordingSerializer

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
        file_data = download_from_gcs(file_name)

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
