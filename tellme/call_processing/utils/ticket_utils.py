import logging
import argparse
import sys
from typing import Tuple, Optional
from jira import JIRA
from jira.exceptions import JIRAError


logger = logging.getLogger(__name__)

def create_ticket(
    ticket_server: str,
    ticket_account: str,
    ticket_api_key: str,
    ticket_project: str,
    ticket_description: str,
    ticket_title: str,
    issue_type: str = "Task"
) -> Tuple[Optional[str], str]:
    """
    Create a Jira ticket using the Jira Python SDK.

    Args:
        ticket_server: The full URL to the instance (e.g. "https://domain.atlassian.net")
        ticket_account: Jira service account email
        ticket_api_key: Jira API token
        ticket_project: Jira project key (e.g., 'PROJ')
        ticket_description: Description/body of the ticket
        ticket_title: Title/summary of the ticket
        issue_type: The issue type name (default: "Task")

    Returns:
        Tuple of (ticket_link, status)
    """
    try:
        # Clean the server URL to avoid double slashes later
        server_url = ticket_server.rstrip('/')

        # Create JIRA client instance
        jira = JIRA(
            server=server_url,
            basic_auth=(ticket_account, ticket_api_key)
        )

        # Prepare the issue payload
        issue_dict = {
            'project': {'key': ticket_project},
            'summary': ticket_title,
            'description': ticket_description,
            'issuetype': {'name': issue_type},
        }

        # Create the issue
        new_issue = jira.create_issue(fields=issue_dict)

        # Build ticket link
        ticket_link = f"{server_url}/browse/{new_issue.key}"
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


def main():
    """
    Main entrypoint for testing execution.
    """
    parser = argparse.ArgumentParser(description="Test Jira Ticket Creation")

    # Required arguments
    parser.add_argument("--server", required=True, help="Jira URL (e.g., https://company.atlassian.net)")
    parser.add_argument("--user", required=True, help="Jira Login Email")
    parser.add_argument("--token", required=True, help="Jira API Token")
    parser.add_argument("--project", required=True, help="Project Key (e.g., KAN)")

    # Optional arguments
    parser.add_argument("--title", default="Test Ticket from Script", help="Ticket Title")
    parser.add_argument("--desc", default="This is a test ticket created via Python.", help="Ticket Description")
    parser.add_argument("--type", default="Task", help="Issue Type (Task, Story, Bug, etc.)")

    args = parser.parse_args()

    print("--- Starting Jira Ticket Test ---")

    link, status = create_ticket(
        ticket_server=args.server,
        ticket_account=args.user,
        ticket_api_key=args.token,
        ticket_project=args.project,
        ticket_description=args.desc,
        ticket_title=args.title,
        issue_type=args.type
    )

    print("-" * 30)
    if status == 'created':
        print(f"✅ SUCCESS: Ticket created at {link}")
        sys.exit(0)
    else:
        print("❌ FAILURE: Could not create ticket. Check logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()