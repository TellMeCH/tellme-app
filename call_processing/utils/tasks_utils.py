import json
import datetime
from django.conf import settings
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import grpc


def create_task(
        process_url: str, file_name: str, organization_id: int, customer_id: str, agent_id: int,
        timestamp: datetime.datetime, logger
):
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
            "url": process_url,
            "headers": {
                "Content-Type": "application/json",
                "Authorization": f"Token {settings.PROCESSING_PIPELINE_KEY}"
            },
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
    client.create_task(parent=parent, task=task)
    logger.info(f'Created task in {settings.CLOUD_TASKS_QUEUE_NAME}')
