from django.urls import reverse
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from call_miner.models import Conversation, Organization, Topic, Employee, Agent, Customer
from call_miner.utils.paginators import CustomFieldCursorPaginator, ListCursorPagination


def paginate_queryset(queryset, request):
    """
    Helper function to paginate a queryset using DRF's CursorPagination.
    """
    paginator = CustomFieldCursorPaginator()

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


class ConversationStatsSerializer(serializers.ModelSerializer):
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
        conversation_trend = obj.get_conversation_trend()
        paginated_qs, paginator = paginate_queryset(
            conversation_trend,
            self.context['request']
        )
        return {
            'results': paginated_qs,
            'next': paginator.get_next_link(),  # Separate 'next' link for conversations
            'previous': paginator.get_previous_link()
        }

    def get_conversation_topic_trend(self, obj):
        topic_trend = obj.get_conversation_trend_per_topic()
        paginated_qs, paginator = paginate_queryset(
            topic_trend,
            self.context['request']
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
                  'customer', 'customer_name', 'input_tokens', 'output_tokens']

    def get_topic_data(self, obj):
        # Return a list of topic names and descriptions
        topic_data = []
        for i, topic in enumerate(obj.topics.all()):
            topic_data.append(
                {
                    'name': topic.name,
                    'description': topic.description,
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
                  'agent_name', 'customer', 'customer_name', 'input_tokens', 'output_tokens']

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
        fields = ['url', 'name', 'conversation_count']

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
        fields = ['name', 'description', 'organization']


class TopicListSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer is used to list all instances of an organization's topics
    """

    class Meta:
        model = Topic
        fields = ['url', 'name', 'description', 'conversation_count']


class TopicDetailSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer is used to present basic topic information, focused on the retrieve() action
    """
    class Meta:
        model = Topic
        fields = ['url', 'name', 'description', 'conversation_count']


class AgentModifySerializer(serializers.ModelSerializer):
    """
    This serializer is used for POST, PUT, PATCH and DELETE requests creating or modifying an Agent instance.
    Note that the agent's organization and manager have to be specified with its primary key.
    """
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    manager = serializers.PrimaryKeyRelatedField(queryset=Agent.objects.all(), required=False)
    agents = serializers.PrimaryKeyRelatedField(queryset=Agent.objects.all(), required=False, many=True)

    class Meta:
        model = Agent
        fields = ['organization', 'employee', 'manager', 'agents']


class AgentListSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer simply lists all existing Agents in an organization, as well as their managers and call count.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    manager = serializers.HyperlinkedRelatedField(view_name='agent-detail', read_only=True)
    manager_username = serializers.CharField(source='manager.user.username', read_only=True)

    class Meta:
        model = Agent
        fields = ['url', 'username', 'manager', 'manager_username', 'conversation_count']


class AgentDetailSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer shows the detail of a given agent, including all its meta-summary data and trend statistics
    """
    username = serializers.CharField(source='user.username', read_only=True)
    manager = serializers.HyperlinkedRelatedField(view_name='agent-detail', read_only=True)
    manager_username = serializers.CharField(source='manager.user.username', read_only=True)
    agents = serializers.HyperlinkedRelatedField(view_name='agent-detail', many=True, read_only=True)  # Pagination will be necessary
    agent_names = serializers.SerializerMethodField()  # Pagination will be necessary

    class Meta:
        model = Agent
        fields = ['url', 'username', 'manager', 'manager_username', 'agents', 'agent_names', 'conversation_count']

    @staticmethod
    def get_agent_names(obj):
        return [agent.user.username for agent in obj.agents.all()]


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
        fields = ['url', 'name', 'conversation_count']


class CustomerDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Customer
        fields = ['url', 'name', 'conversation_count']
