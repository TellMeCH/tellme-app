"""
CallRedacter handles PII redaction and customer identification.

This module contains all redaction-related functionality including:
- PII redaction via Google Cloud DLP
- Customer ID extraction from redacted transcripts
"""

import re
from collections import defaultdict
from datetime import datetime
from langfuse.decorators import observe, langfuse_context
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception
import httpx
import dateparser
from django.conf import settings
import google.cloud.dlp

from .utils import create_customer_id


class CallRedactor:
    """
    Handles PII redaction and customer identification for call processing.

    This class manages the removal of sensitive information from transcripts
    and optionally extracts customer identifiers from the redaction process.
    """

    def __init__(self, minimum_caller_age=16, max_retries=5, base_delay=5.0, backoff_factor=2):
        """
        Initialize the CallRedacter with necessary clients and configuration.

        Args:
            minimum_caller_age (int): Minimum expected age for birth date identification
            max_retries (int): Maximum retry attempts
            base_delay (float): Base delay for exponential backoff
            backoff_factor (int): Backoff multiplier
        """
        # Initialize DLP client and configuration
        self.dlp_client = google.cloud.dlp_v2.DlpServiceClient()

        # DLP entity types to redact
        dlp_entity_types = ["EMAIL_ADDRESS", "PERSON_NAME", "PHONE_NUMBER", "CREDIT_CARD_NUMBER",
                           "LOCATION", "IBAN_CODE", "PASSPORT", "DATE"]

        self.dlp_config = {
            "parent": f"projects/{settings.GOOGLE_CLOUD_PROJECT}/locations/{settings.REGION}",
            "deidentify_config": {
                "info_type_transformations": {
                    "transformations": [
                        {"primitive_transformation": {"replace_with_info_type_config": {}}}
                    ]
                }
            },
            "inspect_config": {"info_types": [{"name": info_type} for info_type in dlp_entity_types]}
        }

        self.minimum_caller_age = minimum_caller_age
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor

    @observe(as_type="generation")
    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=2, exp_base=2, min=5.0),
        stop=stop_after_attempt(5),
        retry=retry_if_exception(lambda e: isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429)
    )
    def redact_transcript(self, transcript: str, extract_customer_id: bool = False) -> tuple[str, str | None]:
        """
        Remove sensitive information from transcript using Google Cloud DLP API.

        Args:
            transcript (str): The transcript text to redact
            extract_customer_id (bool): Whether to extract customer ID from redaction

        Returns:
            tuple[str, str | None]: Redacted transcript and optional customer ID
        """
        langfuse_context.update_current_observation(
            name="redaction_google_dlp",
            start_time=datetime.now(),
        )

        current_request = self.dlp_config.copy()
        current_request["item"] = {"value": transcript}
        response = self.dlp_client.deidentify_content(request=current_request)
        redacted_transcript = response.item.value

        langfuse_context.update_current_observation(
            end_time=datetime.now(),
            input={"transcript_size": len(transcript)},
            output={"redacted_transcript": redacted_transcript},
            model="dlp-service-client"
        )

        customer_id = None
        if extract_customer_id:
            customer_id = self.extract_customer_id_from_redaction(transcript, redacted_transcript)

        return redacted_transcript, customer_id

    def extract_customer_id_from_redaction(self, transcript: str, redacted_transcript: str) -> str:
        """
        Extract a unique customer identifier from original and redacted transcripts.

        This method uses regex pattern matching to align the original transcript with its
        redacted counterpart, extracting DLP-replaced entities. It generates a customer ID
        based on the first person name found and the first birth date (determined by being
        more than MINIMUM_CALLER_AGE years in the past).

        Args:
            transcript (str): The original, unredacted transcript text
            redacted_transcript (str): The DLP-redacted transcript with [ENTITY_TYPE] placeholders

        Returns:
            str: A SHA-256 hashed customer ID based on extracted name and birth date,
                 or a time-based fallback ID if extraction fails

        Raises:
            ValueError: If the original and redacted transcripts cannot be aligned
        """
        # Tokenize redacted text into alternating LITERAL/TAG parts
        tag_pattern = re.compile(r"\[([A-Z][A-Z0-9_]+)\]")
        tokens = []
        last_pos = 0

        for match in tag_pattern.finditer(redacted_transcript):
            # Add literal text before the tag
            if match.start() > last_pos:
                tokens.append(("LITERAL", redacted_transcript[last_pos:match.start()]))
            # Add the tag
            tokens.append(("TAG", match.group(1)))
            last_pos = match.end()

        # Add remaining literal text after the last tag
        if last_pos < len(redacted_transcript):
            tokens.append(("LITERAL", redacted_transcript[last_pos:]))

        # Build regex pattern that mirrors the redacted text structure
        regex_parts = []
        group_mapping = []
        tag_counters = defaultdict(int)

        for token_type, value in tokens:
            if token_type == "LITERAL":
                regex_parts.append(re.escape(value))
            else:  # TAG
                tag_counters[value] += 1
                group_name = f"{value}__{tag_counters[value]}"
                regex_parts.append(f"(?P<{group_name}>.+?)")  # Non-greedy capture
                group_mapping.append((value, group_name))

        # Compile full pattern and match against original transcript
        pattern = re.compile(f"^{''.join(regex_parts)}$", re.DOTALL)
        match = pattern.fullmatch(transcript)

        if not match:
            raise ValueError("Original and redacted transcripts do not align.")

        # Group extracted values by tag type
        extracted_entities = defaultdict(list)
        for tag, group_name in group_mapping:
            extracted_entities[tag].append(match.group(group_name))

        # Extract customer name (first PERSON_NAME found)
        raw_customer_name = extracted_entities['PERSON_NAME'][0] if extracted_entities['PERSON_NAME'] else ''

        # Find first valid birth date (more than MINIMUM_CALLER_AGE years in the past)
        birth_date = self._find_valid_birth_date(extracted_entities['DATE'])

        return create_customer_id(raw_customer_name, birth_date)

    def _find_valid_birth_date(self, date_strings: list[str]) -> str:
        """
        Find the first date string that represents a plausible birth date.

        A valid birth date must be more than MINIMUM_CALLER_AGE years in the past
        to filter out relative dates like 'today', 'yesterday', etc.

        Args:
            date_strings (list[str]): List of date strings extracted from transcript

        Returns:
            str: The first valid birth date string, or empty string if none found
        """
        today = datetime.now()
        minimum_birth_date = datetime(today.year - self.minimum_caller_age, today.month, today.day)

        for date_str in date_strings:
            try:
                parsed_date = dateparser.parse(date_str.strip())
                if parsed_date and parsed_date < minimum_birth_date:
                    return date_str.strip()
            except (ValueError, TypeError):
                continue

        return ''