"""
Cloud Tasks queue management utilities for call processing.

This module provides functions for creating and managing Google Cloud Tasks
for call processing workflows, including file uploads and task scheduling.
"""

import datetime
import json
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import grpc
from django.conf import settings
from rest_framework import status
from tellme.call_processing.utils import gcs_utils, db_handler


def create_storage_path(
        organization_id: int,
        customer_id: str,
        agent_id: int,
        call_timestamp: datetime.datetime,
        format: str = None
):
    """
    Generate a standardized storage path for call recordings.

    Args:
        organization_id (int): ID of the organization
        customer_id (str): Customer identifier
        agent_id (int): Agent identifier
        call_timestamp (datetime.datetime): Call timestamp
        format (str, optional): File format extension (.wav or .mp3)

    Returns:
        str: Formatted storage path

    Raises:
        ValueError: If format is provided but not .wav or .mp3
    """
    customer_part = customer_id if customer_id is not None else "Unknown"
    if format is not None:
        if format not in ['.wav', '.mp3']:
            raise ValueError(f'Invalid file format "{format}" - must be .wav or .mp3')
    else:
        format = ''
    return f"{organization_id}/{customer_part}_{agent_id}_{call_timestamp.isoformat()}{format}"


def create_task(
        process_url: str, file_name: str, organization_id: int, customer_id: str, agent_id: int,
        timestamp: datetime.datetime, transcription_method: str, enrichment_method: str, logger
):
    """
    Create a Google Cloud Task for processing a call recording.

    Args:
        process_url (str): URL endpoint for processing the recording
        file_name (str): Name/path of the file to process
        organization_id (int): ID of the organization
        customer_id (str): Customer identifier
        agent_id (int): Agent identifier
        timestamp (datetime.datetime): Call timestamp
        transcription_method (str): Method to use for transcription
        enrichment_method (str): Method to use for enrichment
        logger: Logger instance for logging events
    """
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
        settings.PROCESSING_QUEUE_NAME
    )
    logger.info(f'Creating task in queue with parent {parent}')
    client.create_task(parent=parent, task=task)
    logger.info(f'Created task in {settings.PROCESSING_QUEUE_NAME}')


def upload_and_create_task(
        file_name: str,
        agent_id: int,
        customer_id: str,
        organization_id: int,
        call_timestamp: datetime.datetime,
        logger,
        allow_simultaneous_calls: bool = False,
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
        allow_simultaneous_calls (bool, optional): Whether to allow simultaneous agent calls. Defaults to False.
        file_obj: The file object containing the call recording data.

    Returns:
        tuple: A tuple containing:
            - dict: A response dictionary with a success or error message.
            - int: The corresponding HTTP status code.
    """
    # Unless the call explictly overrides the org policy, the org policy is followed
    if allow_simultaneous_calls or db_handler.obtain_simultaneous_call_policy(organization_id):
        agent_valid = True
        validity_message = None
    else:
        # Check Validity of Request
        agent_valid, validity_message = db_handler.check_agent_validity(agent_id, organization_id, call_timestamp)

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
