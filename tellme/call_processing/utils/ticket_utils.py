"""
Utilities for creating Jira tickets via the Jira Python SDK.
"""
from jira import JIRA
from jira.exceptions import JIRAError
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


def create_ticket(
    ticket_account: str,
    ticket_api_key: str,
    ticket_project: str,
    ticket_description: str,
    ticket_title: str
) -> Tuple[str, str]:
    """
    Create a Jira ticket using the Jira Python SDK.

    Args:
        ticket_account: Jira service account email (used to extract Jira domain)
        ticket_api_key: Jira API key for authentication
        ticket_project: Jira project key (e.g., 'PROJ')
        ticket_description: Description/body of the ticket
        ticket_title: Title/summary of the ticket

    Returns:
        Tuple of (ticket_link, status) where:
            - ticket_link: URL to the created ticket, or None if failed
            - status: 'created' or 'failed'
    """
    try:
        # Extract Jira domain from email (assumes format: user@domain.atlassian.net)
        # or use a standard format
        if '@' in ticket_account:
            domain_part = ticket_account.split('@')[1]
            if '.atlassian.net' in domain_part:
                jira_server = f"https://{domain_part.split('.atlassian.net')[0]}.atlassian.net"
            else:
                # Assume the domain before @ is the Jira cloud subdomain
                jira_server = f"https://{ticket_account.split('@')[0]}.atlassian.net"
        else:
            # If account is just a domain/subdomain
            if 'http' in ticket_account:
                jira_server = ticket_account
            else:
                jira_server = f"https://{ticket_account}.atlassian.net"

        # Create JIRA client instance
        jira = JIRA(
            server=jira_server,
            basic_auth=(ticket_account, ticket_api_key)
        )

        # Prepare the issue payload
        issue_dict = {
            'project': {'key': ticket_project},
            'summary': ticket_title,
            'description': ticket_description,
            'issuetype': {'name': 'Task'},
        }

        # Create the issue
        new_issue = jira.create_issue(fields=issue_dict)

        # Build ticket link
        ticket_link = f"{jira_server}/browse/{new_issue.key}"
        logger.info(f"Successfully created Jira ticket: {ticket_link}")
        return ticket_link, 'created'

    except JIRAError as e:
        logger.error(f"Jira API error while creating ticket: {str(e)}")
        if hasattr(e, 'status_code'):
            logger.error(f"Status code: {e.status_code}")
        if hasattr(e, 'text'):
            logger.error(f"Response: {e.text}")
        return None, 'failed'
    except Exception as e:
        logger.error(f"Unexpected error while creating Jira ticket: {str(e)}")
        return None, 'failed'
