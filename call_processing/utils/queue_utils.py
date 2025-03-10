import datetime
from django.conf import settings
from rest_framework import status
from call_processing.utils import gcs_utils, tasks_utils
from call_processing.utils.db_handler import check_agent_validity


def upload_and_create_task(
        file_name: str,
        file_obj,
        agent_id: int,
        customer_id: str,
        organization_id: int,
        call_timestamp: datetime.datetime,
        logger,
        check_agent: bool = True
):
    """
    Uploads a call recording to Google Cloud Storage (GCS) and creates a processing task.

    This function first verifies the agent's validity if required. If valid, it uploads the
    recording to GCS and then schedules a background task to process the file. If the agent
    is invalid and validation is enabled, an error response is returned.

    Args:
        file_name (str): The name of the file to be uploaded.
        file_obj: The file object containing the call recording data.
        agent_id (int): The ID of the agent associated with the call.
        customer_id (str): The ID of the customer involved in the call.
        organization_id (int): The ID of the organization.
        call_timestamp (datetime.datetime): The timestamp of the call.
        logger: Logger instance for logging events.
        check_agent (bool, optional): Whether to validate the agent before processing. Defaults to True.

    Returns:
        tuple: A tuple containing:
            - dict: A response dictionary with a success or error message.
            - int: The corresponding HTTP status code.
    """
    agent_valid = False
    validity_message = None
    response = {}
    status_code = None

    if check_agent:
        # Check Validity of Request
        agent_valid, validity_message = check_agent_validity(agent_id, organization_id, call_timestamp)

    if agent_valid or not check_agent:
        # Upload to GCS
        gcs_uri = gcs_utils.upload_to_gcs(file_obj, file_name)
        logger.info(f"Uploaded local file to GCS ({gcs_uri})")

        # Create a task to process this recording
        process_url = settings.CALL_PROCESSING_ENDPOINT
        logger.info(f'Creating an HTTP Task Targeting: {process_url}')
        tasks_utils.create_task(
            process_url, file_name, organization_id, customer_id, agent_id, call_timestamp, logger
        )
        response = {"message": "File queued for processing.", "gcs_uri": gcs_uri}
        status_code = status.HTTP_202_ACCEPTED

    if not agent_valid and check_agent:
        response = {"message": f"Invalid agent. {validity_message}"}
        status_code = status.HTTP_400_BAD_REQUEST

    return response, status_code

