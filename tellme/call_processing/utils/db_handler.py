import datetime
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from tellme.call_miner.models import Agent, Conversation, Customer, Organization, Topic, SuggestedTopic


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


def retrieve_organization_processing_methods(organization_id: int) -> (str, str):
    """
    Returns the organization transcription and enrichment methods

    Args:
        organization_id (int): ID of the organization to query

    Returns:
        transcription_method: str, Identifies provider used for transcription
        enrichment_method: str, Identifies provider used for enrichment
    """
    org = Organization.objects.get(id=organization_id)
    return org.transcription_method, org.enrichment_method


def retrieve_organization_search_prefix(organization_id: int) -> str:
    """
    Returns the organization's revenue search prefix

    Args:
        organization_id (int): ID of the organization to query

    Returns:
        str: The search prefix for revenue queries (e.g., 'pkz.ch/de/')
    """
    org = Organization.objects.get(id=organization_id)
    return org.revenue_search_prefix


def retrieve_organization_language(organization_id: int) -> str:
    """
    Returns the organization's language code

    Args:
        organization_id (int): ID of the organization to query

    Returns:
        str: The language for the organization (e.g., 'English', 'German')
    """
    LANGUAGE_MAPPING = {
        'en': 'English',
        'de': 'German',
        'fr': 'French',
        'it': 'Italian',
        'es': 'Spanish',
    }  # Note: At some point this might have to be scaled
    org = Organization.objects.get(id=organization_id)
    return LANGUAGE_MAPPING.get(org.language)


def obtain_active_topics(organization_id: int):
    """
    Query the call_miner data model to extract all active topics from the organization.

    Args:
        organization_id (int): ID of the organization to query

    Returns:
        str: A string enumerating the names and descriptions of all active topics
    """
    active_topics = '\n'
    for topic in Topic.objects.filter(organization=organization_id, is_active=True):
        active_topics += f'\t - {topic.name}: {topic.description}\n'
    return active_topics


def obtain_suggested_topics(organization_id: int):
    """
    Query the call_miner data model to extract all suggested topics from the organization.

    Args:
        organization_id (int): ID of the organization to query

    Returns:
        str: A string enumerating the names and descriptions of all active topics
    """
    suggested_topics = '\n'
    for topic in SuggestedTopic.objects.filter(organization=organization_id):
        suggested_topics += f'\t - {topic.name}: {topic.description}\n'
    return suggested_topics


def obtain_simultaneous_call_policy(organization_id: int) -> bool:
    """
    Retrieves the organization's policy on whether to allow simultaneous calls from the same agent.

    This function queries the organization's `allow_simultaneous_calls` setting to determine
    whether agent overlap validation should be enforced. When this policy is enabled (True),
    agents can have overlapping calls without validation errors. When disabled (False),
    the system enforces that agents cannot have simultaneous calls.

    Args:
        organization_id (int): ID of the organization to query

    Returns:
        bool: True if the organization allows simultaneous calls for agents,
              False if agent call overlap should be prevented
    """
    org = Organization.objects.get(id=organization_id)
    return org.allow_simultaneous_calls

def check_same_path_conversations(path: str):
    """
    Checks to see whether any conversation has been created for the audio file in the specified path.
    :param path: str, Audio file path
    :return: bool, True if the conversation has been created
    """
    conversation_qs = Conversation.objects.filter(path=path)
    return conversation_qs.exists()


def create_conversation(
    customer_id: str,
    organization_id: int,
    agent_id: int,
    topics: list[str],
    suggested_topics: list[str],
    file_name: str,
    timestamp: str,
    duration: float,
    transcript: str,
    sentiment: float,
    starting_sentiment: float,
    ending_sentiment: float,
    summary: str,
    title: str,
    input_tokens: int,
    output_tokens: int,
    resolved: bool,
    revenue_at_stake: float = None,
    customer_first_name: str = None,
    customer_last_name: str = None,
    customer_birth_date: str = None,
    customer_postcode: str = None,
    customer_loyalty_number: str = None,
    **kwargs
):
    """
    Creates and saves a new Conversation instance with associated customer and agent data.

    This function creates a conversation record by:
    - Creating or retrieving a Customer by external_id and organization
    - Retrieving the Agent by agent_id
    - Associating topics and suggested topics by their names
    - Creating the conversation with all provided metadata including customer demographics

    Args:
        customer_id (str): External customer identifier
        organization_id (int): ID of the organization
        agent_id (int): ID of the agent handling the call
        topics (list[str]): List of topic names to associate
        suggested_topics (list[str]): List of suggested topic names to associate
        file_name (str): Path to the audio file
        timestamp (str): Call timestamp
        duration (float): Call duration in seconds
        transcript (str): Full call transcript
        sentiment (float): Overall sentiment score (1-5)
        starting_sentiment (float): Customer's sentiment at the beginning of the call (1-5)
        ending_sentiment (float): Customer's sentiment at the end of the call (1-5)
        summary (str): AI-generated call summary
        title (str): AI-generated call title
        input_tokens (int): Number of input tokens used
        output_tokens (int): Number of output tokens generated
        resolved (bool): Whether the call issue was resolved
        revenue_at_stake (float, optional): Estimated revenue value
        customer_first_name (str, optional): Customer's first name
        customer_last_name (str, optional): Customer's last name
        customer_birth_date (str, optional): Customer's birth date in YYYY-MM-DD format
        customer_postcode (str, optional): Customer's postcode
        customer_loyalty_number (str, optional): Customer's loyalty number
        **kwargs: Additional keyword arguments

    Raises:
        ValueError: If Agent or Topics do not match the Organization
    """

    org = Organization.objects.get(id=organization_id)
    customer, _ = Customer.objects.get_or_create(
        organization=org,
        external_id=customer_id,
        defaults={
            'first_name': customer_first_name,
            'last_name': customer_last_name,
            'birth_date': customer_birth_date,
            'postcode': customer_postcode,
            'loyalty_number': customer_loyalty_number,
        }
    )
    agent = Agent.objects.get(id=agent_id)

    # Instantiate the Topics based on their names, filtering by this org
    topics_qs = Topic.objects.filter(name__in=topics, organization=org)
    if len(topics_qs) != len(topics):
        missing = set(topics) - set(t.name for t in topics_qs)
        print(f"Some topics were not found in org {organization_id}: {missing}")

    # Instantiate the SuggestedTopics based on their names, filtering by this org
    suggested_topics_qs = SuggestedTopic.objects.filter(name__in=suggested_topics, organization=org)
    if len(suggested_topics_qs) != len(suggested_topics):
        missing = set(suggested_topics) - set(t.name for t in suggested_topics_qs)
        print(f"Some suggested topics were not found in org {organization_id}: {missing}")

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
        starting_sentiment=starting_sentiment,
        ending_sentiment=ending_sentiment,
        summary=summary,
        title=title,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        revenue_at_stake=revenue_at_stake,
        resolved=resolved,
        customer=customer,
        agent=agent
    )
    conversation.save()
    conversation.topics.set(topics_qs)
    conversation.suggested_topics.set(suggested_topics_qs)


def create_suggested_topics(
        new_topics: list[dict[str, str]],
        conversation_file_name: str,
        organization_id: int
):
    """
    Creates new SuggestedTopic instances while respecting organization limits.
    
    This function intelligently manages suggested topics by:
    - Creating new topics when there's available space
    - Replacing old, unpopular topics (conversation_count=1) when at capacity
    - Avoiding duplicates with existing suggested topics and regular topics
    - Maintaining the organization's max_topic_count limit
    
    The replacement strategy prioritizes oldest topics first (FIFO) and only
    replaces topics that have exactly one linked conversation, preserving
    popular suggested topics that are associated with multiple conversations.
    
    Args:
        new_topics: List of dictionaries containing 'name' and 'description' keys
        conversation_file_name: Path of the conversation that triggered these suggestions
        organization_id: ID of the organization to create suggested topics for
        
    Returns:
        None: Function performs database operations and returns nothing
        
    Example:
        new_topics = [
            {'name': 'Technical Support', 'description': 'Hardware troubleshooting calls'},
            {'name': 'Billing Issues', 'description': 'Payment and invoice inquiries'}
        ]
        create_suggested_topics(new_topics, 'call_123.wav', organization_id=5)
    """

    # First off, retrieve the conversation that triggered these topics
    conversation_qs = Conversation.objects.filter(path=conversation_file_name)
    if len(conversation_qs) == 1:
        conversation = conversation_qs.first()
    elif len(conversation_qs) > 1:
        raise ValueError(f"More than one Conversation instance matches path = {conversation_file_name}")
    else:
        raise ValueError(f"Could not find a Conversation instance with path = {conversation_file_name}")

    # Then, retrieve the existing suggested topics
    org = Organization.objects.get(id=organization_id)
    existing_suggested = SuggestedTopic.objects.filter(organization=org)
    existing_regular = Topic.objects.filter(organization=org)
    
    # Pre-filter new topics for duplicates and validation
    valid_new_topics = []
    existing_names = (
        set(existing_suggested.values_list('name', flat=True)) |
        set(existing_regular.values_list('name', flat=True))
    )
    
    for topic in new_topics:
        if not topic.get('name') or not topic.get('description'):
            continue
        if topic['name'] in existing_names:
            continue  # Skip duplicates
        valid_new_topics.append(topic)
    
    if not valid_new_topics:
        return  # Nothing to create
    
    # Calculate how many we can create
    current_count = len(existing_suggested)
    available_space = max(0, org.max_topic_count - current_count)
    can_replace = existing_suggested.filter(conversation_count=1).count()
    max_creatable = min(len(valid_new_topics), available_space + can_replace)
    
    if max_creatable == 0:
        return  # Can't create any
    
    # Determine how many to replace vs create in available space
    to_create_count = min(max_creatable, len(valid_new_topics))
    to_replace_count = max(0, to_create_count - available_space)
    
    # Get topics to replace (oldest first)
    to_replace_candidates = existing_suggested.filter(conversation_count=1).order_by('created')[:to_replace_count]
    
    # Delete old topics first to avoid exceeding max
    if to_replace_candidates:
        # Convert sliced QuerySet to list of IDs, then delete by IDs
        topic_ids_to_delete = list(to_replace_candidates.values_list('id', flat=True))
        if topic_ids_to_delete:
            SuggestedTopic.objects.filter(id__in=topic_ids_to_delete).delete()
    
    # Create new topics
    for topic in valid_new_topics[:to_create_count]:
        suggested_topic = SuggestedTopic(
            name=topic["name"],
            description=topic["description"],
            organization=org
        )
        suggested_topic.save()
        conversation.suggested_topics.add(suggested_topic)


def trigger_summarization_tasks(conversation, logger):
    """
    Trigger summarization tasks for the associated topics, customer, and agent
    after a new conversation is created.

    This function checks if summaries need to be refreshed based on the same logic
    as MetaSummaryAbstractModel._needs_refresh, and creates summarization tasks
    for objects that need updates.

    Args:
        conversation: The newly created Conversation object
        logger: Logger instance for logging events
    """
    from tellme.call_processing.utils.summarization import needs_refresh
    from tellme.call_processing.utils.queue_utils import create_summarization_task
    from tellme.call_miner.utils.period_utils import period_bounds
    from tellme.call_miner.models import PeriodSummary
    from django.contrib.contenttypes.models import ContentType
    from django.conf import settings

    # Get summarization parameters from ViewSet defaults
    # Topic summarization parameters (from TopicViewSet)
    topic_period = 'quarter'
    topic_rolling = True

    # Customer summarization parameters (from CustomerViewSet)
    customer_period = 'quarter'
    customer_rolling = True

    # Agent summarization parameters (from MetaSummaryAbstractViewSet)
    agent_period = 'month'
    agent_rolling = False

    summarize_url = f"{settings.CALL_PROCESSING_ENDPOINT.rstrip('/')}/summarize/"

    # Check topics
    for topic in conversation.topics.all():
        _check_and_create_summarization_task(
            obj=topic,
            obj_type='topic',
            period=topic_period,
            rolling=topic_rolling,
            summarize_url=summarize_url,
            logger=logger
        )

    # Check customer
    _check_and_create_summarization_task(
        obj=conversation.customer,
        obj_type='customer',
        period=customer_period,
        rolling=customer_rolling,
        summarize_url=summarize_url,
        logger=logger
    )

    # Check agent
    _check_and_create_summarization_task(
        obj=conversation.agent,
        obj_type='agent',
        period=agent_period,
        rolling=agent_rolling,
        summarize_url=summarize_url,
        logger=logger
    )


def _check_and_create_summarization_task(obj, obj_type, period, rolling, summarize_url, logger):
    """
    Check if an object needs summarization and create a task if needed.

    Args:
        obj: The object (Topic, Customer, or Agent) to check
        obj_type: String type ('topic', 'customer', 'agent')
        period: Period to use for summarization
        rolling: Whether to use rolling period
        summarize_url: URL for the summarization endpoint
        logger: Logger instance
    """
    from tellme.call_processing.utils.summarization import needs_refresh
    from tellme.call_processing.utils.queue_utils import create_summarization_task
    from tellme.call_miner.utils.period_utils import period_bounds
    from tellme.call_miner.models import PeriodSummary
    from django.contrib.contenttypes.models import ContentType

    try:
        start, end, label = period_bounds(period, rolling)

        # Get conversations in the relevant time period
        conversations = obj.conversations.filter(date__gte=start, date__lt=end)
        if not conversations.exists():
            logger.debug(f"No conversations found for {obj_type} {obj.id} in period {label}")
            return

        # Check if there's an existing summary
        content_type = ContentType.objects.get_for_model(obj.__class__)
        try:
            summary_obj = PeriodSummary.objects.get(
                content_type=content_type,
                object_id=obj.pk,
                period_type=period,
                period_label=label
            )

            # Check if refresh is needed
            refresh_needed, call_count = needs_refresh(summary_obj, conversations, rolling, start)

            if not refresh_needed:
                logger.debug(f"Summary for {obj_type} {obj.id} does not need refresh")
                return

        except PeriodSummary.DoesNotExist:
            # No existing summary, create task
            logger.info(f"No existing summary for {obj_type} {obj.id}, creating summarization task")

        # Create summarization task
        task_id = create_summarization_task(
            summarize_url=summarize_url,
            object_id=obj.id,
            object_type=obj_type,
            summary_period=period,
            summary_rolling_period=rolling,
            logger=logger
        )

        logger.info(f"Created summarization task {task_id} for {obj_type} {obj.id}")

    except Exception as e:
        logger.error(f"Error checking summarization for {obj_type} {obj.id}: {str(e)}")
        # Don't raise the exception to avoid breaking conversation creation
