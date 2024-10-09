from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from call_miner.models import Conversation, Organization, Topic, Employee, Agent, Analyst, Customer
from django.contrib.auth.models import User
from call_miner.utils.paginators import CustomFieldCursorPaginator, ListCursorPagination


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


class ConversationTrendsSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

    def get_conversations(self, obj):
        """
        Retrieve conversations related to the object and paginate the results.
        This approach retrieves only necessary fields and paginates efficiently.
        """
        # Ensure request is available in the context
        request = self.context.get('request')
        if not request:
            raise NotFound("Request context is missing")
        # Optimize by only fetching the fields needed and paginating
        conversations_qs, paginator = paginate_queryset(
            obj.conversations_scope.all()
            .order_by('-date')  # Order by descending date
            .values('id', 'title', 'date'),  # Fetch only the needed fields
            self.context['request']
        )

        if conversations_qs is None:
            return []

        # Build the response format (including URLs)
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
            'next': paginator.get_next_link(),  # Separate 'next' link for conversations
            'previous': paginator.get_previous_link()
        }

    def get_conversation_trend(self, obj):
        request = self.context.get('request')
        trend_period = request.query_params.get('trend_period', 'daily')

        conversation_trend = obj.get_conversation_trend(trend_period)
        paginated_qs, paginator = paginate_queryset(
            conversation_trend,
            self.context['request'],
            ['date']
        )
        return {
            'results': paginated_qs,
            'next': paginator.get_next_link(),  # Separate 'next' link for conversations
            'previous': paginator.get_previous_link()
        }

    def get_conversation_topic_trend(self, obj):
        request = self.context.get('request')
        trend_period = request.query_params.get('trend_period', 'daily')  # Default to daily

        topic_trend = obj.get_conversation_trend_per_topic(trend_period)
        paginated_qs, paginator = paginate_queryset(
            topic_trend,
            self.context['request'],
            ['date', 'topic']
        )
        return {
            'results': paginated_qs,
            'next': paginator.get_next_link(),  # Separate 'next' link for conversations
            'previous': paginator.get_previous_link()
        }

    def get_duration_trend(self, obj):
        """
        Determines the trend period based on the query parameter 'trend_period'.
        Defaults to 'daily' if no parameter is provided.
        """
        request = self.context.get('request')
        trend_period = request.query_params.get('trend_period', 'daily')  # Default to daily

        # Fetch the appropriate trend based on the period
        duration_trend = obj.get_avg_for_periods('duration', trend_period)
        paginated_qs, paginator = paginate_queryset(
            duration_trend,
            self.context['request']
        )
        return {
            'results': paginated_qs,
            'next': paginator.get_next_link(),  # Separate 'next' link for conversations
            'previous': paginator.get_previous_link()
        }

    def get_sentiment_trend(self, obj):
        """
        Determines the trend period based on the query parameter 'trend_period'.
        Defaults to 'daily' if no parameter is provided.
        """
        request = self.context.get('request')
        trend_period = request.query_params.get('trend_period', 'daily')  # Default to daily

        # Fetch the appropriate trend based on the period
        sentiment_trend = obj.get_avg_for_periods('sentiment', trend_period)
        paginated_qs, paginator = paginate_queryset(
            sentiment_trend,
            self.context['request']
        )
        return {
            'results': paginated_qs,
            'next': paginator.get_next_link(),  # Separate 'next' link for conversations
            'previous': paginator.get_previous_link()
        }


class MetaSummarySerializer(serializers.ModelSerializer):
    """
    Abstract Serializer class used to produce meta-summary data on the models that allow its creation via
    get_or_create_summary()
    """
    class Meta:
        abstract = True

    @staticmethod
    def get_summary_data(obj):
        obj.get_or_create_summary()
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
    topics = serializers.PrimaryKeyRelatedField(many=True, queryset=Topic.objects.all())
    agent = serializers.PrimaryKeyRelatedField(queryset=Agent.objects.all())
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())

    class Meta:
        model = Conversation
        fields = ['path', 'date', 'duration', 'transcript', 'summary', 'title', 'sentiment', 'topics',
                  'agent', 'customer', 'input_tokens', 'output_tokens']


class ConversationListSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer is used for the GET requests listing all Conversation instances. Here, topics, agents and
    customers are lists with their names and hyperlinks.
    """
    # Retrieve the URL of the related models
    agent = serializers.HyperlinkedRelatedField(view_name='agent-detail', read_only=True)
    customer = serializers.HyperlinkedRelatedField(view_name='customer-detail', read_only=True)
    agent_name = serializers.CharField(source='agent.user.username', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    topic_data = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['url', 'path', 'date', 'duration', 'title', 'sentiment', 'topic_data', 'agent', 'agent_name',
                  'customer', 'customer_name', 'input_tokens', 'output_tokens', 'created']

    def get_topic_data(self, obj):
        # Return a list of topic names and descriptions
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
    This serializer is used when applying a GET detail request on a Conversation instance. Since it inherits from
    ConversationListSerializer, topics, agent and customer are once again lists with their names and hyperlinks.
    However, it also presents the processed transcripts on top.
    """
    pagination_class = ListCursorPagination()

    class Meta:
        model = Conversation
        fields = ['url', 'path', 'date', 'duration', 'summary', 'title', 'sentiment', 'topic_data', 'agent',
                  'agent_name', 'customer', 'customer_name', 'input_tokens', 'output_tokens', 'created']

    def get_processed_transcript(self, obj):
        messages = obj.process_transcript()
        paginated_data, paginator = paginate_list(messages, self.context['request'])
        return {
            'results': paginated_data,
            'next': paginator.get_next_link(),  # Separate 'next' link for conversations
            'previous': paginator.get_previous_link()
        }


class OrganizationDetailSerializer(serializers.HyperlinkedModelSerializer):
    conversation_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ['url', 'name', 'conversation_count', 'max_user_count', 'created', 'updated']

    @staticmethod
    def get_conversation_count(obj):
        return obj.conversations_scope.count()


class TopicModifySerializer(serializers.ModelSerializer):
    """
    This serializer is used for POST, PUT, PATCH and DELETE requests creating or modifying a Topic instance.
    Note that the topic's organization has to be specified with its primary key.
    """
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())

    class Meta:
        model = Topic
        fields = ['name', 'description', 'organization', 'is_active']


class TopicListSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer is used to list all instances of an organization's topics
    """

    class Meta:
        model = Topic
        fields = ['url', 'name', 'description', 'conversation_count', 'first_conversation_date',
                  'last_conversation_date', 'is_active', 'created', 'updated']


class TopicDetailSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer is used to present basic topic information, focused on the retrieve() action
    """
    class Meta:
        model = Topic
        fields = ['url', 'name', 'description', 'conversation_count', 'first_conversation_date',
                  'last_conversation_date', 'is_active', 'created', 'updated']


class AgentListSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer simply lists all existing Agents in an organization, as well as their managers and call count.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    manager = serializers.HyperlinkedRelatedField(view_name='agent-detail', read_only=True)
    manager_username = serializers.CharField(source='manager.user.username', read_only=True)

    class Meta:
        model = Agent
        fields = ['url', 'username', 'manager', 'manager_username', 'conversation_count', 'first_conversation_date',
                  'last_conversation_date', 'created', 'updated']


class AgentDetailSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer shows the detail of a given agent, including all its meta-summary data and trend statistics
    """
    username = serializers.CharField(source='user.username', read_only=True)
    manager = serializers.HyperlinkedRelatedField(view_name='agent-detail', read_only=True)
    manager_username = serializers.CharField(source='manager.user.username', read_only=True)

    class Meta:
        model = Agent
        fields = ['url', 'username', 'manager', 'manager_username', 'conversation_count',
                  'first_conversation_date', 'last_conversation_date', 'created', 'updated']

    def get_agent_data(self, obj):
        # Return a list of agent names and links
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
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())

    class Meta:
        model = Customer
        fields = ['organization', 'name']


class CustomerListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Customer
        fields = ['url', 'name', 'conversation_count', 'first_conversation_date', 'last_conversation_date', 'created']


class CustomerDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Customer
        fields = ['url', 'name', 'conversation_count', 'first_conversation_date', 'last_conversation_date', 'created']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        # Update User instance
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class EmployeeListSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()
    organization = serializers.HyperlinkedRelatedField(view_name='organization-detail', read_only=True)
    manager = serializers.HyperlinkedRelatedField(view_name='employee-detail', read_only=True)

    class Meta:
        model = Employee
        fields = ('url', 'organization', 'user', 'role', 'manager', 'is_organization_admin', 'created', 'updated')
        read_only_fields = ('created', 'updated')


class EmployeeModifySerializer(serializers.ModelSerializer):
    user = UserSerializer()
    organization = serializers.PrimaryKeyRelatedField(read_only=True)
    manager = serializers.PrimaryKeyRelatedField(queryset=Agent.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Employee
        fields = ('id', 'organization', 'user', 'role', 'manager', 'is_organization_admin', 'created', 'updated')
        read_only_fields = ('created', 'updated')

    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            current_user = request.user

            # Make sure current user has an associated organization
            if not hasattr(current_user, 'employee'):
                raise serializers.ValidationError("Current user is not associated with an Employee profile.")

            user_organization = current_user.employee.organization
            data['organization'] = user_organization  # Enforce the request user's organization

            # If manager is specified, check that they are in the same organization
            manager = data.get('manager')
            if manager and manager.organization != user_organization:
                raise serializers.ValidationError({
                    'manager': 'Manager must belong to the same organization as the current user.'
                })

            if manager and data.get('role') == 'ANALYST':
                raise serializers.ValidationError({
                    'role': "Analysts can't have managers."
                })
        else:
            raise serializers.ValidationError("Request user is not available.")

        return data

    def create(self, validated_data):
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
        except Exception:
            user.delete()
            raise

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        manager = validated_data.pop('manager', None)

        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        # Update Employee fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle role change
        role = validated_data.get('role', instance.role)
        if role != instance.role:
            raise serializers.ValidationError(f'Could not update Employee. It is not possible to change role from {instance.role} to {role}.')
        else:
            if isinstance(instance, Agent) and manager is not None:
                instance.manager = manager
            instance.save()
        return instance
