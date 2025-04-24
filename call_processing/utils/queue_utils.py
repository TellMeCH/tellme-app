import datetime
import json
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import grpc
from django.conf import settings
from rest_framework import status
from call_processing.utils import gcs_utils, db_handler


def create_storage_path(organization_id: int, customer_id: str, agent_id: int, call_timestamp: datetime.datetime):
    return f"{organization_id}/{customer_id}_{agent_id}_{call_timestamp.isoformat()}"


def create_task(
        process_url: str, file_name: str, organization_id: int, customer_id: str, agent_id: int,
        timestamp: datetime.datetime, transcription_method: str, enrichment_method: str, logger
):
    payload = {
        "file_name": file_name,
        "organization_id": organization_id,
        "customer_id": customer_id,
        "agent_id": agent_id,
        "timestamp": timestamp.isoformat(),
        "transcription_method": transcription_method,
        "enrichment_method": enrichment_method
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


def upload_and_create_task(
        file_name: str,
        agent_id: int,
        customer_id: str,
        organization_id: int,
        call_timestamp: datetime.datetime,
        logger,
        check_agent: bool = True,
        file_obj=None
):
    """
    Uploads a call recording to Google Cloud Storage (GCS) and creates a processing task.

    This function first verifies the agent's validity if required. If valid, and a recording was provided, it uploads it
    to GCS. Then, it schedules a background task to process the file. If the agent is invalid and validation is enabled,
     an error response is returned.

    Args:
        file_name (str): The name of the file to be uploaded.
        agent_id (int): The ID of the agent associated with the call.
        customer_id (str): The ID of the customer involved in the call.
        organization_id (int): The ID of the organization.
        call_timestamp (datetime.datetime): The timestamp of the call.
        logger: Logger instance for logging events.
        check_agent (bool, optional): Whether to validate the agent before processing. Defaults to True.
        file_obj: The file object containing the call recording data.

    Returns:
        tuple: A tuple containing:
            - dict: A response dictionary with a success or error message.
            - int: The corresponding HTTP status code.
    """

    if check_agent:
        # Check Validity of Request
        agent_valid, validity_message = db_handler.check_agent_validity(agent_id, organization_id, call_timestamp)
    else:
        agent_valid = True
        validity_message = None

    if agent_valid:
        # Upload to GCS
        if file_obj is not None:
            gcs_uri = gcs_utils.upload_to_gcs(file_obj, file_name)
            logger.info(f"Uploaded local file to GCS ({gcs_uri})")

        # Determine the Organization's Transcription Method
        transcription_method, enrichment_method = db_handler.retrieve_organization_processing_methods(organization_id)

        # Create a task to process this recording
        process_url = settings.CALL_PROCESSING_ENDPOINT
        logger.info(f'Creating an HTTP Task Targeting: {process_url}')
        create_task(
            process_url,
            file_name,
            organization_id,
            customer_id,
            agent_id,
            call_timestamp,
            transcription_method,
            enrichment_method,
            logger
        )
        response = {"message": "Recording(s) queued for processing.", "file_name": file_name}
        status_code = status.HTTP_202_ACCEPTED
    else:
        response = {"message": f"Invalid agent. {validity_message}"}
        status_code = status.HTTP_400_BAD_REQUEST

    return response, status_code
