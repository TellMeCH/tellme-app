from django.urls import reverse
from rest_framework import serializers
from call_miner.models import Conversation, Organization, Topic, Employee, Agent, Customer


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
    topics = serializers.HyperlinkedRelatedField(view_name='topic-detail', many=True, read_only=True)

    # Include human-readable fields for agent, customer, and topics
    agent_name = serializers.CharField(source='agent.user.username', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    topic_names = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['url', 'path', 'date', 'duration', 'transcript', 'summary', 'title', 'sentiment', 'topics',
                  'topic_names', 'agent', 'agent_name', 'customer', 'customer_name', 'input_tokens', 'output_tokens']

    @staticmethod
    def get_topic_names(obj):
        return [topic.name for topic in obj.topics.all()]


class ConversationDetailSerializer(ConversationListSerializer):
    """
    This serializer is used when applying a GET detail request on a Conversation instance. Since it inherits from
    ConversationListSerializer, topics, agent and customer are once again lists with their names and hyperlinks.
    However, it also presents the processed transcripts on top.
    """
    processed_transcript = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['url', 'path', 'date', 'duration', 'transcript', 'summary', 'title', 'sentiment', 'topics',
                  'topic_names', 'agent', 'agent_name', 'customer', 'customer_name', 'input_tokens', 'output_tokens',
                  'processed_transcript']

    @staticmethod
    def get_processed_transcript(obj):
        return obj.process_transcript()


class ConversationRelationshipSerializer(serializers.ModelSerializer):
    conversation_count = serializers.SerializerMethodField()
    conversations = serializers.SerializerMethodField()
    conversation_trend = serializers.SerializerMethodField()
    conversation_topic_trend = serializers.SerializerMethodField()
    duration_trend = serializers.SerializerMethodField()
    sentiment_trend = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    @staticmethod
    def get_conversation_count(obj):
        return obj.conversations.count()

    def get_conversations(self, obj):
        conversation_titles = []  # Pagination will be necessary
        for conversation in obj.conversations.all():
            conversation_titles.append(
                {
                    'title': conversation.title,
                    'url': self.context['request'].build_absolute_uri(
                        reverse('conversation-detail', args=[conversation.pk])
                    )
                }
            )
        return conversation_titles

    @staticmethod
    def get_conversation_trend(obj):
        return obj.get_conversation_trend()  # Pagination will be necessary

    @staticmethod
    def get_conversation_topic_trend(obj):
        return obj.get_conversation_trend_per_topic()  # Pagination will be necessary

    @staticmethod
    def get_duration_trend(obj):
        return obj.get_avg_duration()  # Pagination will be necessary

    @staticmethod
    def get_sentiment_trend(obj):
        return obj.get_avg_sentiment()  # Pagination will be necessary


class OrganizationSerializer(serializers.HyperlinkedModelSerializer, ConversationRelationshipSerializer):
    topics = serializers.HyperlinkedRelatedField(view_name='topic-detail', many=True, read_only=True)
    topic_data = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ['url', 'name', 'topics', 'topic_data', 'conversation_trend', 'conversation_topic_trend',
                  'duration_trend', 'sentiment_trend']

    @staticmethod
    def get_topic_data(obj):
        # Return a list of topic names and descriptions
        topic_data = []
        for topic in obj.topics.all():
            topic_data.append(
                {
                    'name': topic.name,
                    'description': topic.description,
                }
            )
        return topic_data


class TopicModifySerializer(serializers.ModelSerializer):
    """
    This serializer is used for POST, PUT, PATCH and DELETE requests creating or modifying a Topic instance.
    Note that the topic's organization has to be specified with its primary key.
    """
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())

    class Meta:
        model = Topic
        fields = ['name', 'description', 'organization']


class TopicListSerializer(serializers.HyperlinkedModelSerializer, ConversationRelationshipSerializer):
    """
    This serializer is used to list all instances of an organization's topics
    """
    conversation_count = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = ['url', 'name', 'description', 'conversation_count']


class MetaSummarySerializer(serializers.ModelSerializer):
    """
    Abstract Serializer class used to produce meta-summary data on the models that allow its creation via
    get_or_create_summary()
    """
    summary_data = serializers.SerializerMethodField()

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


class TopicDetailSerializer(serializers.HyperlinkedModelSerializer, ConversationRelationshipSerializer,
                            MetaSummarySerializer):
    """
    This serializer is used to present all topic information and statistics, focused on the retrieve() action
    """
    class Meta:
        model = Topic
        fields = ['url', 'name', 'description', 'summary_data', 'conversations', 'conversation_trend',
                  'conversation_topic_trend', 'duration_trend', 'sentiment_trend']


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


class AgentListSerializer(serializers.HyperlinkedModelSerializer, ConversationRelationshipSerializer):
    """
    This serializer simply lists all existing Agents in an organization, as well as their managers and call count.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    manager = serializers.HyperlinkedRelatedField(view_name='agent-detail', read_only=True)
    manager_username = serializers.CharField(source='manager.user.username', read_only=True)
    conversation_count = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = ['url', 'username', 'manager', 'manager_username', 'conversation_count']


class AgentDetailSerializer(serializers.HyperlinkedModelSerializer, ConversationRelationshipSerializer,
                            MetaSummarySerializer):
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
        fields = ['url', 'username', 'manager', 'manager_username', 'summary', 'summary_date', 'summary_call_count',
                  'agents', 'agent_names', 'conversations', 'conversation_trend', 'conversation_topic_trend',
                  'duration_trend', 'sentiment_trend']

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


class CustomerListSerializer(serializers.HyperlinkedModelSerializer, ConversationRelationshipSerializer):
    conversation_count = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['url', 'name', 'conversation_count']


class CustomerDetailSerializer(serializers.HyperlinkedModelSerializer, ConversationRelationshipSerializer,
                               MetaSummarySerializer):
    class Meta:
        model = Customer
        fields = ['url', 'name', 'summary', 'summary_date', 'summary_call_count', 'conversations', 'conversation_trend',
                  'conversation_topic_trend', 'duration_trend', 'sentiment_trend']
