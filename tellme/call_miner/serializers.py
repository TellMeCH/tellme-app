from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema_field
from django.conf import settings
from tellme.call_miner.models import (
    Conversation, Organization, OrganizationAPIKey, Topic, SuggestedTopic, Employee, Agent, Analyst, Customer, User
)
from tellme.call_miner.utils.paginators import CustomFieldCursorPaginator, ListCursorPagination
from tellme.call_miner.schemas import TOPIC_DATA_RESPONSE_SCHEMA, SUGGESTED_TOPIC_DATA_RESPONSE_SCHEMA


def paginate_queryset(queryset, request, ordering: list[str] = None):
    """
    Paginates a queryset using Django Rest Framework's (DRF) CursorPagination with custom ordering.

    This function leverages a custom cursor paginator to paginate the given queryset
    according to the specified ordering. It uses DRF's CursorPagination class to efficiently
    paginate large datasets and supports cursor-based navigation through results.

    Args:
        queryset (QuerySet): The queryset to paginate.
        request (HttpRequest): The current request object, which contains pagination parameters.
        ordering (list[str]): A list of fields to use for ordering in the cursor pagination.

    Returns:
        tuple: A tuple containing:
            - paginated_qs (QuerySet): The paginated subset of the queryset.
            - paginator (CursorPaginator): The paginator instance used for pagination, useful for
              accessing additional pagination data (like the next and previous cursor).

    Raises:
        ValueError: If the ordering fields are not valid for cursor pagination.

    Example:
        paginated_queryset, paginator = paginate_queryset(my_queryset, request, ['-date'])
    """
    paginator = CustomFieldCursorPaginator()
    if ordering:
        paginator.ordering = ordering

    # Paginate the queryset using DRF's cursor paginator
    paginated_qs = paginator.paginate_queryset(queryset, request)
    return paginated_qs, paginator


def paginate_list(data: list[dict], request):
    """
    Helper function to paginate a list of dictionaries using DRF's CursorPagination.
    """
    paginator = ListCursorPagination()

    # Paginate the list of dicts using DRF's cursor paginator
    paginated_data = paginator.paginate_queryset(data, request)
    return paginated_data, paginator


class ConversationTrendsSerializer(serializers.Serializer):
    """
    This serializer contains a series of methods aimed at describing the temporal evolution of multiple conversation
    statistics, as well as the complete conversation list of an object.
    """
    class Meta:
        abstract = True

    def get_conversations(self, obj):
        """
        Paginated list of conversation data. Each conversation is represented by its title, date, and link.
        """
        request = self.context.get('request')
        if not request:
            raise NotFound("Request context is missing")

        conversations_qs, paginator = paginate_queryset(
            obj.conversations_scope.all()
            .order_by('-date')
            .values('id', 'title', 'date'),
            self.context['request']
        )

        if conversations_qs is None:
            return []

        conversation_titles = [
            {
                'title': conversation['title'],
                'date': conversation['date'],
                'url': self.context['request'].build_absolute_uri(
                    reverse('conversation-detail', args=[conversation['id']])
                )
            }
            for conversation in conversations_qs
        ]
        return {
            'results': conversation_titles,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link()
        }

    def get_trend(self, obj):
        """
        Paginated trend regarding an object's conversations. Expects the request to include at most three parameters:
            period (str): The time period granularity to use for the trend. Must be one of "daily", "weekly", "monthly"
            per_topic (bool): Indicates whether to group by the time period AND the topic, or just by the time period
            field (str): Specifies what field to examine. If none is specified, the call count, average sentiment and
                average duration will be used.
        """
        request = self.context.get('request')
        trend_period = request.query_params.get('trend_period', 'monthly')
        per_topic = request.query_params.get('per_topic', 'false').lower() == 'true'
        field = request.query_params.get('field')

        if per_topic and (not field or field == 'count'):
            order_by = ['-date', '-count']
        else:
            order_by = ['-date']

        trend = obj.get_trend(trend_period, per_topic, field)
        paginated_qs, paginator = paginate_queryset(
            trend,
            self.context['request'],
            order_by
        )
        return {
            'results': paginated_qs,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link()
        }

    def get_overview(self, obj):
        """
        Retrieve an overview of the conversation metrics for the past two months.

        This method reads the 'per_topic' parameter from the request's query parameters to decide whether
        to present aggregated data across all conversations ('general'), or broken down by each topic.
        It then calls the object's `get_overview(per_topic)` method, which returns a nested dictionary
        containing metrics for 'count', 'avg_sentiment', and 'avg_duration' over the last two months, as
        well as the percentage change between those months.

        Args:
            obj: The object whose conversation data we want to summarize (e.g., Organization or Agent).

        Returns:
            dict: A nested dictionary showing last month's and prior month's values for each metric,
                  plus the percentage change between them. Keys are either "general" or the topic names
                  (if per_topic=True).
        """
        request = self.context.get('request')
        per_topic = request.query_params.get('per_topic', 'false').lower() == 'true'
        overview = obj.get_overview(per_topic)
        return overview


class MetaSummarySerializer(serializers.Serializer):
    """
    Abstract Serializer class used to produce meta-summary data on the models that allow its creation via
    get_or_create_summary()
    """
    class Meta:
        abstract = True

    def get_summary_data(self, obj):
        """
        Summary of all conversation summaries (for a given period) of the object. Includes also the date of this
        summarization and the number of calls that were taken into account for this summary.
        """
        trace_data = self.context.get('trace_data', {})
        period = self.context.get('period')
        rolling = self.context.get('rolling')
        if isinstance(rolling, str):
            rolling = rolling.lower() == 'true'
        summary, summary_date, call_count, period_label = obj.get_or_create_summary(period, rolling, trace_data)
        return {
            'summary': summary,
            'summary_date': summary_date,
            'summary_call_count': call_count,
            'period_label': period_label
        }


class ConversationModifySerializer(serializers.ModelSerializer):
    """
    This serializer is used for POST requests creating a new Conversation instance. Note that the conversation's
    topics, agent and customer have to be specified with their primary keys.
    """
    topics = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Topic.objects.all(),
        help_text='Primary keys of the topics associated with the conversation'
    )
    suggested_topics = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=SuggestedTopic.objects.all(),
        help_text='Primary keys of the suggested topics associated with the conversation'
    )
    agent = serializers.PrimaryKeyRelatedField(
        queryset=Agent.objects.all(),
        help_text='Primary key of the related agent'
    )
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        help_text='Primary key of the related customer'
    )

    class Meta:
        model = Conversation
        fields = ['id', 'created', 'path', 'date', 'duration', 'transcript', 'summary', 'title', 'sentiment', 'topics',
                  'suggested_topics', 'agent', 'customer', 'input_tokens', 'output_tokens', 'revenue_at_stake']

    def validate(self, data):
        """
        Validates the data provided for the creation or modification of a Conversation. In particular, check that the
        provided sentiment score is between 0 and 5
        """
        sentiment = data.get('sentiment')
        if sentiment:
            if not (0 <= sentiment <= 5):
                raise serializers.ValidationError(
                    detail={'sentiment': f'Sentiment score must be between 0 and 5. Provided value was {sentiment}'}
                )
        return data


class ConversationListSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer is used for the GET requests listing all Conversation instances. Here, topics, agents and
    customers are lists with their names and hyperlinks.
    """
    agent = serializers.HyperlinkedRelatedField(
        view_name='agent-detail',
        read_only=True,
        help_text='Link to the conversation agent'
    )
    customer = serializers.HyperlinkedRelatedField(
        view_name='customer-detail',
        read_only=True,
        help_text='Link to the conversation customer'
    )
    agent_email = serializers.CharField(
        source='agent.user.email',
        read_only=True,
        help_text='Email of the related agent'
    )
    customer_id = serializers.CharField(
        source='customer.external_id',
        read_only=True,
        help_text='Name of the related customer'
    )
    topic_data = serializers.SerializerMethodField(
        help_text='List of associated topics, including their name, description, status, and link.'
    )
    suggested_topic_data = serializers.SerializerMethodField(
        help_text='Obtains a list of associated topic suggestions, with their name, description and conversation count.'
    )

    class Meta:
        model = Conversation
        fields = ['url', 'path', 'date', 'duration', 'title', 'sentiment', 'topic_data', 'suggested_topic_data',
                  'agent', 'agent_email', 'customer', 'customer_id', 'input_tokens', 'output_tokens', 'created']

    @extend_schema_field(TOPIC_DATA_RESPONSE_SCHEMA)
    def get_topic_data(self, obj):
        """
        Obtains a list of associated topics, including their name, description, status, and link.
        """
        topic_data = []
        for i, topic in enumerate(obj.topics.all()):
            topic_data.append(
                {
                    'name': topic.name,
                    'description': topic.description,
                    'is_active': topic.is_active,
                    'url': self.context['request'].build_absolute_uri(
                        reverse('topic-detail', args=[topic.id])
                    ),
                }
            )
        return topic_data

    @extend_schema_field(SUGGESTED_TOPIC_DATA_RESPONSE_SCHEMA)
    def get_suggested_topic_data(self, obj):
        """
        Obtains a list of associated topic suggestions, including their name, description and conversation count.
        """
        topic_data = []
        for i, topic in enumerate(obj.suggested_topics.all()):
            topic_data.append(
                {
                    'name': topic.name,
                    'description': topic.description,
                    'conversation_count': topic.conversation_count
                }
            )
        return topic_data


class ConversationDetailSerializer(ConversationListSerializer):
    """
    Serializer to retrieve a single Conversation instance. Since it inherits from ConversationListSerializer, topics,
    agent and customer are once again lists with their names and hyperlinks.
    However, it also presents the processed transcripts on top.
    """
    pagination_class = ListCursorPagination()
    agent_first_name = serializers.CharField(
        source='agent.user.first_name',
        read_only=True,
        help_text='First name of the related agent'
    )
    agent_last_name = serializers.CharField(
        source='agent.user.last_name',
        read_only=True,
        help_text='Last name of the related agent'
    )

    class Meta:
        model = Conversation
        fields = ['url', 'path', 'date', 'duration', 'summary', 'title', 'sentiment', 'topic_data',
                  'suggested_topic_data', 'agent', 'agent_email', 'agent_first_name', 'agent_last_name', 'customer',
                  'customer_id', 'revenue_at_stake', 'input_tokens', 'output_tokens', 'created']

    def get_processed_transcript(self, obj):
        """
        Obtains a paginated list of the processed conversation transcript, separating each speaker's message accordingly
        """
        messages = obj.process_transcript()
        paginated_data, paginator = paginate_list(messages, self.context['request'])
        return {
            'results': paginated_data,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link()
        }


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer to retrieve a single Organization instance.
    """
    conversation_count = serializers.SerializerMethodField(
        help_text='Count of conversations associated to the organization'
    )
    employee_count = serializers.SerializerMethodField(
        help_text='Count of employees associated to the organization'
    )

    class Meta:
        model = Organization
        fields = [
            'url', 'name', 'conversation_count', 'max_user_count', 'max_topic_count', 'created', 'updated', 'transcription_method',
            'enrichment_method', 'revenue_search_prefix', 'language', 'employee_count'
        ]

    @staticmethod
    @extend_schema_field({'type': 'integer'})
    def get_conversation_count(obj):
        return obj.conversations_scope.count()

    @staticmethod
    @extend_schema_field({'type': 'integer'})
    def get_employee_count(obj):
        return obj.employees.count()


class OrganizationAPIKeyModifySerializer(serializers.ModelSerializer):
    """
    Serializer for creating and deleting an API key. Accepts the name of the key and the organization ID.
    """
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,
        default=None,
        help_text='Primary key of the associated organization'
    )
    plain_key = serializers.CharField(
        required=False,
        help_text='Plain text view of the API key, visible only at creation'
    )

    class Meta:
        model = OrganizationAPIKey
        fields = ['id', 'name', 'organization', 'plain_key', 'created']
        read_only_fields = ['plain_key']

    def validate(self, data):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError("Request user is not available.")

        current_user = request.user

        if self.instance is None:  # Checks when creating a new key
            # For superusers, make sure that the creation has specified an organization
            if current_user.is_superuser:
                if not data.get('organization'):
                    raise serializers.ValidationError({
                        "organization": "Superusers must provide an organization when creating an API Key."
                    })
            else:  # For non-superusers, enforce the organization
                if not hasattr(current_user, 'employee'):
                    raise serializers.ValidationError("Current user is not associated with an Employee profile.")

                # Non-superusers should not specify an organization
                if 'organization' in data:
                    if data['organization'] is not None:
                        raise serializers.ValidationError({
                            "organization": f"Users should not provide an organization when creating an API Key."
                        })

                # Enforce the user's organization
                data['organization'] = current_user.employee.organization

            # Check if creating a new API Key would exceed the organization's MAX_KEYS_PER_ORG
            current_key_count = OrganizationAPIKey.objects.filter(organization=data['organization']).count()
            if current_key_count >= OrganizationAPIKey.MAX_KEYS_PER_ORG:
                raise serializers.ValidationError(
                    {"non_field_errors": ["Cannot add more API keys to this organization; max key count reached."]}
                )

            # Check that no key with the same name already exists in the same organization
            if OrganizationAPIKey.objects.filter(organization=data['organization'], name=data['name']).exists():
                raise serializers.ValidationError({
                    "name": "An API key with this name already exists in this organization."
                })
        return data

    def create(self, validated_data):
        name = validated_data['name']
        organization = validated_data['organization']

        plain_key = OrganizationAPIKey.create_key(
            organization=organization,
            name=name
        )

        return {
            'name': name,
            'organization': organization,
            'plain_key': plain_key
        }


class OrganizationAPIKeyListSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for listing or retrieving existing API keys. Only exposes name, created, expires.
    """
    class Meta:
        model = OrganizationAPIKey
        fields = ['id', 'name', 'created', 'expires']
        read_only_fields = fields


class TopicModifySerializer(serializers.ModelSerializer):
    """
    This serializer is used for POST, PUT, PATCH and DELETE requests creating or modifying a Topic instance.
    Note that the topic's organization has to be specified with its primary key.
    """
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,
        default=None,
        help_text='Primary key of the associated organization'
    )

    class Meta:
        model = Topic
        fields = ['id', 'created', 'name', 'description', 'organization', 'is_active']

    def validate(self, data):
        """
        Validates the provided request data, in particular the specified organization. Superusers are expected to
        provide an organization, whereas non-superusers can only create Topics in their own organization.
        """
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError("Request user is not available.")

        current_user = request.user

        # For superusers, make sure that the creation has specified an organization
        if current_user.is_superuser:
            if self.instance is None:
                if not data.get('organization'):
                    raise serializers.ValidationError({
                        "organization": "Superusers must provide an organization when creating a Topic."
                    })
        else:  # For non-superusers, enforce the organization
            if not hasattr(current_user, 'employee'):
                raise serializers.ValidationError("Current user is not associated with an Employee profile.")

            # Non-superusers should not specify an organization
            if 'organization' in data:
                if data['organization'] is not None:
                    raise serializers.ValidationError({
                        "organization": f"Analysts should not provide an organization when modifying a Topic."
                    })

            # Enforce the user's organization
            data['organization'] = current_user.employee.organization

        if self.instance is None:
            # Check if creating a new topic would exceed the organization's max_topic_count
            current_topic_count = Topic.objects.filter(organization=data['organization']).count()
            if current_topic_count >= data['organization'].max_topic_count:
                raise serializers.ValidationError(
                    {"non_field_errors": ["Cannot add more topics to this organization; max topic count reached."]}
                )

            # Check whether a topic with the same name and organization already exists
            # Note: If the request data contains an 'organization', the default UniqueTogetherValidator will raise error
            existing_topic = Topic.objects.filter(organization=data['organization'], name__iexact=data['name'])
            if existing_topic.exists():
                raise serializers.ValidationError(
                    {'name': ['A topic with this same name already exists in this Organization.']}
                )
        return data


class TopicListSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer is used to view instances of an organization's topics
    """

    class Meta:
        model = Topic
        fields = ['url', 'name', 'description', 'conversation_count', 'first_conversation_date',
                  'last_conversation_date', 'is_active', 'created', 'updated']


class SuggestedTopicAcceptSerializer(serializers.Serializer):
    """Non-model serializer for accepting suggested topics"""

    def accept(self):
        """Accept the suggested topic and return the new topic data"""
        if not hasattr(self, 'instance') or self.instance is None:
            raise serializers.ValidationError("No suggested topic instance provided")

        # Validate that accepting this topic won't exceed the organization's limit
        organization = self.instance.organization
        current_topic_count = Topic.objects.filter(organization=organization).count()
        if current_topic_count >= organization.max_topic_count:
            raise serializers.ValidationError(
                {"non_field_errors": ["Cannot add more topics to this organization; maximum topic count reached."]}
            )

        # Call the model's accept method
        new_topic = self.instance.accept()

        # Return serialized data of the new topic
        return TopicListSerializer(new_topic, context=self.context).data


class SuggestedTopicListSerializer(serializers.ModelSerializer):
    """
    This serializer is used to view instances of an organization's suggested topics
    """

    class Meta:
        model = SuggestedTopic
        fields = ['id', 'name', 'description', 'conversation_count', 'first_conversation_date',
                  'last_conversation_date', 'created', 'updated']


class AgentListSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer simply lists all existing Agents in an organization, as well as their managers and call count.
    """
    email = serializers.CharField(source='user.email', read_only=True, help_text='Agent email')
    manager = serializers.HyperlinkedRelatedField(
        view_name='agent-detail',
        read_only=True,
        help_text="Link to the agent's manager"
    )
    manager_email = serializers.CharField(
        source='manager.user.email',
        read_only=True,
        help_text="Email of the agent's manager"
    )

    class Meta:
        model = Agent
        fields = ['url', 'email', 'manager', 'manager_email', 'conversation_count', 'first_conversation_date',
                  'last_conversation_date', 'created', 'updated']


class AgentDetailSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer shows the detail of a given agent, including all its meta-summary data and trend statistics
    """
    email = serializers.CharField(source='user.email', read_only=True, help_text='Agent email')
    manager = serializers.HyperlinkedRelatedField(
        view_name='agent-detail',
        read_only=True,
        help_text="Link to the agent's manager"
    )
    manager_email = serializers.CharField(
        source='manager.user.email',
        read_only=True,
        help_text="Email of the agent's manager"
    )

    class Meta:
        model = Agent
        fields = ['url', 'email', 'manager', 'manager_email', 'conversation_count',
                  'first_conversation_date', 'last_conversation_date', 'created', 'updated']

    def get_agent_data(self, obj):
        """
        Obtain a paginated list of all the associated agents under a manager. For each agent, shows the id, email,
        link, conversation count, and first and last conversation dates.
        """
        agent_data = []
        for i, agent in enumerate(obj.agents.all()):
            agent_data.append(
                {
                    'id': i,
                    'email': agent.user.email,
                    'url': self.context['request'].build_absolute_uri(
                        reverse('agent-detail', args=[agent.id])
                    ),
                    'conversation_count': agent.conversation_count,
                    'first_conversation_date': agent.first_conversation_date,
                    'last_conversation_date': agent.last_conversation_date,
                }
            )
        paginated_data, paginator = paginate_list(agent_data, self.context['request'])
        return {
            'results': paginated_data,
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link()
        }


class CustomerModifySerializer(serializers.ModelSerializer):
    """
    This serializer is used for POST, PUT, PATCH and DELETE requests creating or modifying a Customer instance.
    Note that the customer's organization has to be specified with its primary key.
    """
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        help_text='Organization primary key'
    )

    class Meta:
        model = Customer
        fields = ['id', 'created', 'organization', 'external_id']


class CustomerListSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer used to list Customer instances
    """
    class Meta:
        model = Customer
        fields = ['url', 'external_id', 'conversation_count', 'first_conversation_date', 'last_conversation_date',
                  'created']


class UserSerializer(serializers.ModelSerializer):
    """
    This serializer is used to manage User instances.
    """
    class Meta:
        model = User
        fields = ('email', 'auth_type', 'first_name', 'last_name')

    def validate(self, data):
        if data.get('email') == settings.PROCESSING_PIPELINE_USER:
            raise serializers.ValidationError({"email": "Provided user email is protected."})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            auth_type=validated_data['auth_type']
        )
        return user

    def update(self, instance, validated_data):
        auth_type = validated_data.get('auth_type')

        # If changing the authentication type to 'password', send onboarding email
        if auth_type is not None and auth_type != instance.auth_type:
            if auth_type == 'password':
                instance.send_onboarding_email()
            else:
                raise serializers.ValidationError(
                    {'auth_type': "Can't change auth_type to something other than 'password'"}
                )

        email = validated_data.get('email')
        if email is not None and email != instance.email:
            raise serializers.ValidationError({"email": "Can't change user email"})

        # Update instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()


class EmployeeModifySerializer(serializers.ModelSerializer):
    """
    This serializer is used for superusers and organization admins to create new Employees. It contains separate methods
    for validating, creating, and updating an Employee.
    """
    user = UserSerializer()
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,
        default=None,
        help_text='Primary key of associated organization'
    )
    manager = serializers.PrimaryKeyRelatedField(
        queryset=Agent.objects.all(),
        required=False,
        allow_null=True,
        help_text='Primary key of associated manager'
    )

    class Meta:
        model = Employee
        fields = ['id', 'organization', 'user', 'role', 'manager', 'is_organization_admin', 'created', 'updated']
        read_only_fields = ['created', 'updated']

    def validate(self, data):
        """
        Validates the provided request data. It assumes that superusers don't need validation, whereas organization
        admins' requests are checked to ensure that:
        - The resulting employee will have the same organization as the organization admin (this is enforced)
        - If a manager is specified, it belongs to the same organization as the organization admin and the Employee
        - If a manager is specified, the Employee role is not 'ANALYST'.
        """
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            raise serializers.ValidationError("Request user is not available.")

        current_user = request.user

        # For superusers, make sure that the creation has specified an organization
        if current_user.is_superuser:
            if self.instance is None:
                if not data.get('organization'):
                    raise serializers.ValidationError({
                        "organization": "Superusers must provide an organization when creating an Employee."
                    })
                else:
                    organization = data.get('organization')
            else:
                organization = self.instance.organization
        else:
            if not hasattr(current_user, 'employee'):
                raise serializers.ValidationError("Current user is not associated with an Employee profile.")

            # Non-superusers should not specify an organization
            if 'organization' in data:
                if data['organization'] is not None:
                    raise serializers.ValidationError({
                        "organization": f"Org Admins should not provide an organization when modifying an Employee."
                    })
            # Enforce the organization from the current user's employee profile
            user_organization = current_user.employee.organization
            data['organization'] = user_organization
            organization = user_organization

        # Check if creating a new employee would exceed the organization's max_user_count
        current_employee_count = Employee.objects.filter(organization=organization).count()
        if self.instance is None:
            if current_employee_count >= organization.max_user_count:
                raise serializers.ValidationError(
                    {"non_field_errors": ["Cannot add more users to this organization; max user count reached."]}
                )

        # If manager is specified, check that they are in the same organization
        manager = data.get('manager')
        if manager and manager.organization != organization:
            raise serializers.ValidationError({
                'manager': 'Manager must belong to the same organization as the current user.'
            })

        # Check that no manager was mistakenly assigned to an analyst
        if manager and data.get('role') == 'ANALYST':
            raise serializers.ValidationError({
                'role': "Analysts can't have managers."
            })
        return data

    def create(self, validated_data):
        """
        Based on the validated data, create a new User, and depending on the specified role, a new Analyst or Agent.
        """
        user_data = validated_data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()

        try:
            role = validated_data.get('role')
            validated_data['user'] = user

            manager = validated_data.pop('manager', None)
            if role == 'ANALYST':
                employee = Analyst.objects.create(**validated_data)

                # Only onboard analyst users
                user.send_onboarding_email()
            elif role in ['AGENT', 'MANAGER']:
                employee = Agent.objects.create(manager=manager, **validated_data)
            else:
                raise serializers.ValidationError(f'Could not create new Employee. Invalid role: {role}')
            return employee
        except Exception as e:
            user.delete()
            raise e

    def update(self, instance, validated_data):
        """
        Update an already existing Employee. If this update involves a role change, this will not be allowed, to ensure
        data consistency.
        """
        user_data = validated_data.pop('user', None)

        # Handle role change
        role = validated_data.get('role')
        if role is not None and role != instance.role:
            raise serializers.ValidationError(
                f'Could not update Employee. It is not possible to change role from {instance.role} to {role}.')

        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # Update Employee fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update Manager only if 'manager' is provided in the request data
        if 'manager' in self.initial_data and hasattr(instance, 'agent'):
            manager = validated_data.pop('manager', None)
            instance.agent.manager = manager
            instance.agent.save()
        return instance


class EmployeeListSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer user to list Employee instances.
    """
    user = UserSerializer()
    organization = serializers.HyperlinkedRelatedField(
        view_name='organization-detail',
        read_only=True,
        help_text='Link to associated organization'
    )
    manager = serializers.HyperlinkedRelatedField(
        view_name='employee-detail',
        read_only=True,
        help_text='Link to employee manager'
    )

    class Meta:
        model = Employee
        fields = ['url', 'organization', 'user', 'role', 'manager', 'is_organization_admin', 'created', 'updated']
        read_only_fields = ['created', 'updated']