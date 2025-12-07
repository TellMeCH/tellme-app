import uuid
import grpc
import json
import logging
import datetime
from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
from django.db import models
from django.conf import settings

logger = logging.getLogger(__name__)


# Summary settings constants for default summarization behavior.
DEFAULT_SUMMARY_SETTINGS = {
    'topic': {
        'period': 'quarter',
        'rolling': True
    },
    'customer': {
        'period': 'quarter',
        'rolling': True
    },
    'agent': {
        'period': 'month',
        'rolling': False
    }
}


def get_default_summary_settings():
    """
    Get default summary period and rolling window settings.

    Returns:
        dict: Default settings for each object type
    """
    return DEFAULT_SUMMARY_SETTINGS.copy()


def get_tasks_client_and_parent():
    # Create a Cloud Task Client, using the Cloud Tasks emulator when necessary
    if settings.TASKS_EMULATOR_ADDRESS:
        # Create a gRPC channel to the local emulator
        channel = grpc.insecure_channel(settings.TASKS_EMULATOR_ADDRESS)
        transport = tasks_v2.services.cloud_tasks.transports.CloudTasksGrpcTransport(channel=channel)
        client = tasks_v2.CloudTasksClient(transport=transport)
    else:
        # Use the default CloudTasksClient configuration
        client = tasks_v2.CloudTasksClient()

    # Get the queue path
    parent = client.queue_path(
        settings.GOOGLE_CLOUD_PROJECT,
        settings.REGION,
        settings.SUMMARIZATION_QUEUE_NAME
    )
    return client, parent


def check_summarization_tasks(
        object_id: int,
        object_type: str,
        summary_period: str,
        rolling_period: bool
) -> bool:
    """
    Check if a summarization task with the same parameters already exists in the queue.

    Args:
        object_id (int): ID of the object to summarize
        object_type (str): Type of object ('topic', 'customer', 'agent')
        summary_period (str): Period to use for summarization ('week', 'month', 'quarter')
        rolling_period (bool): Whether to use rolling period

    Returns:
        bool: True if a matching task exists in the queue, False otherwise
    """
    try:
        client, parent = get_tasks_client_and_parent()

        # List tasks in the queue
        tasks = client.list_tasks(parent=parent)

        # Check each task for matching parameters
        for task in tasks:
            if hasattr(task, 'http_request') and task.http_request.body:
                try:
                    # Parse the task payload
                    payload = json.loads(task.http_request.body.decode())

                    # Check if this task matches our parameters
                    if (payload.get('object_id') == object_id and
                        payload.get('object_type') == object_type and
                        payload.get('summary_period') == summary_period and
                        payload.get('rolling_period') == rolling_period):
                        return True

                except (json.JSONDecodeError, UnicodeDecodeError):
                    # Skip tasks with invalid payloads
                    continue

        return False

    except Exception as e:
        logger.error(f'Failed to check summarization tasks: {e}')
        # If we can't check the queue, assume no duplicates (safer to create task)
        return False


def create_summarization_task(
        object_id: int,
        object_type: str,
        summary_period: str,
        rolling_period: bool,
        task_id: str = None
):
    """
    Create a Google Cloud Task for summarizing an object (Topic, Customer, or Agent).

    Args:
        object_id (int): ID of the object to summarize
        object_type (str): Type of object ('topic', 'customer', 'agent')
        summary_period (str): Period to use for summarization ('week', 'month', 'quarter')
        rolling_period (bool): Whether to use rolling period
        task_id (str, optional): Optional task ID for tracking
    """
    if task_id is None:
        task_id = str(uuid.uuid4())

    payload = {
        "object_id": object_id,
        "object_type": object_type,
        "summary_period": summary_period,
        "rolling_period": rolling_period,
        "task_id": task_id
    }

    task = {
        "http_request": {
            "http_method": tasks_v2.HttpMethod.POST,
            "url": settings.SUMMARIZATION_ENDPOINT,
            "headers": {
                "Content-Type": "application/json",
                "X-Tellme-Token": f"Token {settings.PROCESSING_PIPELINE_KEY}"
            },
            "body": json.dumps(payload).encode(),
            "oidc_token": {
                "service_account_email": settings.SERVICE_ACCOUNT_EMAIL,
            }
        }
    }

    # Specify the task schedule time
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromDatetime(datetime.datetime.now(datetime.UTC))
    task['schedule_time'] = timestamp

    client, parent = get_tasks_client_and_parent()
    logger.info(f'Creating summarization task in queue with parent {parent}')
    client.create_task(parent=parent, task=task)
    logger.info(f'Created summarization task in {settings.SUMMARIZATION_QUEUE_NAME} for {object_type} {object_id}')

    return task_id