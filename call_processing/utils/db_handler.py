import datetime
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from call_miner.models import Agent, Conversation, Customer, Organization, Topic


def check_agent_validity(agent_id: int, organization_id: int, call_timestamp: datetime.datetime) -> (bool, str):
    """
    Checks whether the agent exists in the specified organization and 
    whether the newly pushed call does not overlap with the agent's last call.
    """

    is_valid = False
    message = "Agent was not found. Please create agent before pushing associated call recordings."

    # Attempt to fetch the agent directly
    try:
        _ = Agent.objects.get(organization=organization_id, id=agent_id)
    except Agent.DoesNotExist:
        return is_valid, message

    # Check if the agent already has conversations
    conversation_qs = Conversation.objects.filter(agent=agent_id)
    if conversation_qs.exists():
        latest_call = conversation_qs.latest('date')
        latest_call_end_time = latest_call.date + datetime.timedelta(seconds=latest_call.duration)

        # If the new call timestamp is strictly after the last call ended, we consider the agent "valid."
        if latest_call_end_time < call_timestamp:
            is_valid = True
            message = "Valid agent."
        else:
            message = "This agent's last call was still taking place when the pushed call recording was taken."
    else:
        # If the agent has no conversations, this is their first call
        is_valid = True
        message = "Valid agent. This is their first call."

    return is_valid, message


def retrieve_organization_transcription_method(organization_id: int):
    """
    Returns the organization transcription method
    """
    org = Organization.objects.get(id=organization_id)
    return org.transcription_method


def obtain_active_topics(organization_id: int):
    """
    Query the call_miner data model to extract all active topics from the organization.

    Args:
        organization_id (int): ID of the organization to query

    Returns:
        str: A string enumerating the names and descriptions of all active topics
    """
    active_topics = ''
    for topic in Topic.objects.filter(organization=organization_id, is_active=True):
        active_topics += f'{topic.name}: {topic.description}, '
    return active_topics


def create_conversation(
    customer_id: str,
    organization_id: int,
    agent_id: int,
    topics: list[str],
    file_name: str,
    timestamp: str,
    duration: float,
    transcript: str,
    sentiment: float,
    summary: str,
    title: str,
    input_tokens: int,
    output_tokens: int,
    **kwargs
):
    """
    Creates and saves a new Conversation instance using:
      - a Customer fetched (or created) by external_customer_id + organization_id
      - an Agent fetched by agent_id
      - a list of Topics fetched by their names
    Raises ValueError if Agent or Topics do not match the Organization.
    """

    org = Organization.objects.get(id=organization_id)
    customer, _ = Customer.objects.get_or_create(
        organization=org,
        external_id=customer_id
    )
    agent = Agent.objects.get(id=agent_id)

    # Instantiate the Topics based on their names, filtering by this org
    topics_qs = Topic.objects.filter(name__in=topics, organization=org)
    if len(topics_qs) != len(topics):
        missing = set(topics) - set(t.name for t in topics_qs)
        raise Warning(f"Some topics were not found in org {organization_id}: {missing}")

    # Convert date_str to a timezone-aware DateTime
    if timestamp is None:
        raise ValueError(f"Could not parse datetime from '{timestamp}'")
    if isinstance(timestamp, str):
        dt = parse_datetime(timestamp)
    else:
        dt = timestamp
    if dt.tzinfo is None:
        dt = timezone.make_aware(dt)

    # Create and save the Conversation
    conversation = Conversation(
        path=file_name,
        date=dt,
        duration=duration,
        transcript=transcript,
        sentiment=sentiment,
        summary=summary,
        title=title,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        customer=customer,
        agent=agent
    )
    conversation.save()
    conversation.topics.set(topics_qs)

