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
from .serializers import QueueRecordingSerializer
from call_processing.utils.gcs_utils import upload_to_gcs, download_from_gcs

logger = logging.getLogger(__name__)


class QueueRecordingView(APIView):
    """
    This API view has the sole purpose of queueing a call processing task on a predefined Cloud Tasks Manager. Moreover,
    it is designed to work in conjunction with a Cloud Tasks Emulator for local development.
    Only API-token bearing requests should have permission to run this view.
    """
    def post(self, request):
        serializer = QueueRecordingSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            organization = data['organization']
            customer_id = data['customer_id']
            agent_id = data['agent_id']
            timestamp = data['timestamp']
            file_obj = data['file']
            file_name = f"{organization}/{customer_id}_{agent_id}_{timestamp.isoformat()}.wav"

            logger.info(f'Execution Time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            logger.info(f"Created: {timestamp}")
            logger.info(f"Organization: {organization}")
            logger.info(f"File: {file_name}")

            # Upload to GCS
            # gcs_uri = upload_to_gcs(file_obj, file_name)

            # Create a task to process this recording
            payload = {
                "file_name": file_name,
                "organization": organization,
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
                {"message": "File queued for processing."}, #, "gcs_uri": gcs_uri},
                status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessRecordingView(APIView):
    """
    Carries out the processing steps on a call recording. These include:
    Only the processing pipeline account (PROCESSING_PIPELINE_USER and PROCESSING_PIPELINE_KEY) should have access
    """
    def post(self, request):
        # The Cloud Task request will contain JSON with file_name and other metadata
        file_name = request.data.get("file_name")
        if not file_name:
            return Response({"error": "file_name not provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Download file from GCS
        # file_data = download_from_gcs(file_name)

        # For now, we do nothing except log that we got it.
        # logger.info(f"Processing file {file_name}, size {len(file_data)} bytes.")

        # Return success
        return Response({"message": "File processed (loaded from GCS)."}, status=status.HTTP_200_OK)
