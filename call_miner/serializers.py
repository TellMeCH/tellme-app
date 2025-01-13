from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema_field
from django.conf import settings
from call_miner.models import (
    Conversation, Organization, OrganizationAPIKey, Topic, Employee, Agent, Analyst, Customer, User
)
from call_miner.utils.paginators import CustomFieldCursorPaginator, ListCursorPagination
from call_miner.schemas import TOPIC_DATA_RESPONSE_SCHEMA


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


class MetaSummarySerializer(serializers.Serializer):
    """
    Abstract Serializer class used to produce meta-summary data on the models that allow its creation via
    get_or_create_summary()
    """
    class Meta:
        abstract = True

    def get_summary_data(self, obj):
        """
        Summary of all conversation summaries of the object. Includes also the date of this summarization and the
        number of calls that was taken into account for this summary.
        """
        trace_data = self.context.get('trace_data', {})
        obj.get_or_create_summary(trace_data)
        return {
            'summary': obj.summary,
            'summary_date': obj.summary_date,
            'summary_call_count': obj.summary_call_count
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
                  'agent', 'customer', 'input_tokens', 'output_tokens']

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
    agent_name = serializers.CharField(
        source='agent.user.username',
        read_only=True,
        help_text='Username of the related agent'
    )
    customer_name = serializers.CharField(
        source='customer.name',
        read_only=True,
        help_text='Name of the related customer'
    )
    topic_data = serializers.SerializerMethodField(
        help_text='List of associated topics, including their name, description, status, and link.'
    )

    class Meta:
        model = Conversation
        fields = ['url', 'path', 'date', 'duration', 'title', 'sentiment', 'topic_data', 'agent', 'agent_name',
                  'customer', 'customer_name', 'input_tokens', 'output_tokens', 'created']

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


class ConversationDetailSerializer(ConversationListSerializer):
    """
    Serializer to retrieve a single Conversation instance. Since it inherits from ConversationListSerializer, topics,
    agent and customer are once again lists with their names and hyperlinks.
    However, it also presents the processed transcripts on top.
    """
    pagination_class = ListCursorPagination()

    class Meta:
        model = Conversation
        fields = ['url', 'path', 'date', 'duration', 'summary', 'title', 'sentiment', 'topic_data', 'agent',
                  'agent_name', 'customer', 'customer_name', 'input_tokens', 'output_tokens', 'created']

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

    class Meta:
        model = Organization
        fields = ['url', 'name', 'conversation_count', 'max_user_count', 'created', 'updated']

    @staticmethod
    @extend_schema_field({'type': 'integer'})
    def get_conversation_count(obj):
        return obj.conversations_scope.count()


class OrganizationAPIKeyListSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for listing or retrieving existing API keys. Only exposes name, created, expires.
    """
    class Meta:
        model = OrganizationAPIKey
        fields = ['id', 'name', 'created', 'expires']
        read_only_fields = fields


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

        # Check if creating a new topic would exceed the organization's max_topic_count
        if self.instance is None:
            current_topic_count = Topic.objects.filter(organization=data['organization']).count()
            if current_topic_count >= data['organization'].max_topic_count:
                raise serializers.ValidationError(
                    {"non_field_errors": ["Cannot add more topics to this organization; max topic count reached."]}
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


class AgentListSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer simply lists all existing Agents in an organization, as well as their managers and call count.
    """
    username = serializers.CharField(source='user.username', read_only=True, help_text='Agent username')
    manager = serializers.HyperlinkedRelatedField(
        view_name='agent-detail',
        read_only=True,
        help_text="Link to the agent's manager"
    )
    manager_username = serializers.CharField(
        source='manager.user.username',
        read_only=True,
        help_text="Username of the agent's manager"
    )

    class Meta:
        model = Agent
        fields = ['url', 'username', 'manager', 'manager_username', 'conversation_count', 'first_conversation_date',
                  'last_conversation_date', 'created', 'updated']


class AgentDetailSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer shows the detail of a given agent, including all its meta-summary data and trend statistics
    """
    username = serializers.CharField(source='user.username', read_only=True, help_text='Agent username')
    manager = serializers.HyperlinkedRelatedField(
        view_name='agent-detail',
        read_only=True,
        help_text="Link to the agent's manager"
    )
    manager_username = serializers.CharField(
        source='manager.user.username',
        read_only=True,
        help_text="Username of the agent's manager"
    )

    class Meta:
        model = Agent
        fields = ['url', 'username', 'manager', 'manager_username', 'conversation_count',
                  'first_conversation_date', 'last_conversation_date', 'created', 'updated']

    def get_agent_data(self, obj):
        """
        Obtain a paginated list of all the associated agents under a manager. For each agent, shows the id, username,
        link, conversation count, and first and last conversation dates.
        """
        agent_data = []
        for i, agent in enumerate(obj.agents.all()):
            agent_data.append(
                {
                    'id': i,
                    'name': agent.user.username,
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
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data.get('email') == settings.PROCESSING_PIPELINE_USER:
            raise serializers.ValidationError({
                "email": "Provided user email is protected."
            })
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()
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
