"""
Shared utilities for call processing modules.

Contains common methods and retry logic used across multiple processors.
"""

import time
import hashlib
import httpx
import dateparser
import nameparser
from django.conf import settings
from google.genai import errors


def vertexai_retry_logic(error):
    """
    Centralized predicate for tenacity retries on Vertex AI calls.

    Returns ``True`` for HTTP 429s raised by either *httpx* or the
    `google-genai` SDK, allowing the decorator to back off and retry.

    Args:
        error: The exception that occurred

    Returns:
        bool: True if the error should trigger a retry
    """
    case_1 = isinstance(error, httpx.HTTPStatusError) and error.response.status_code == 429
    case_2 = isinstance(error, errors.ClientError) and error.code == 429
    return case_1 or case_2


def create_customer_id(full_name: str, birth_date: str) -> tuple[str, str | None, str | None, str | None]:
    """
    Create a hashed customer ID from name and birth date.

    Args:
        full_name (str): Customer's full name
        birth_date (str): Customer's birth date string

    Returns:
        tuple[str, str | None, str | None, str | None]:
            SHA-256 hashed customer ID, first name, last name, and Django-formatted birth date
    """
    # Generate raw ID for hashing
    raw_id = str(time.time())  # Fallback to timestamp-based ID if no name found
    first_name, last_name, django_formatted_date = None, None, None
    if full_name:
        parsed_name = nameparser.HumanName(full_name)

        if parsed_name.last:
            name_component = f'{parsed_name.first}{parsed_name.last}'
            first_name, last_name = parsed_name.first, parsed_name.last

            if birth_date:
                date_component = dateparser.parse(birth_date).strftime("%d/%m/%Y")
                django_formatted_date = dateparser.parse(birth_date).strftime("%Y-%m-%d")
                raw_id = f'{name_component}{date_component}'
            else:
                raw_id = name_component

    # Return salted hash of the raw ID
    hashed_id = hashlib.sha256((settings.HASH_KEY + raw_id + settings.HASH_KEY).encode('utf8')).hexdigest()
    return hashed_id, first_name, last_name, django_formatted_date