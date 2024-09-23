from django.urls import reverse
from rest_framework import serializers
from call_miner.models import Conversation, Organization, Topic, Agent, Customer


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
    agent = serializers.HyperlinkedRelatedField(view_name='agent-detail', queryset=Agent.objects.all())
    customer = serializers.HyperlinkedRelatedField(view_name='customer-detail', queryset=Customer.objects.all())
    topics = serializers.HyperlinkedRelatedField(view_name='topic-detail', many=True, queryset=Topic.objects.all())

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
    conversations = serializers.SerializerMethodField()
    conversation_trend = serializers.SerializerMethodField()
    conversation_topic_trend = serializers.SerializerMethodField()
    duration_trend = serializers.SerializerMethodField()
    sentiment_trend = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def get_conversations(self, obj):
        conversation_titles = []
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
        return obj.get_conversation_trend()

    @staticmethod
    def get_conversation_topic_trend(obj):
        return obj.get_conversation_trend_per_topic()

    @staticmethod
    def get_duration_trend(obj):
        return obj.get_avg_duration()

    @staticmethod
    def get_sentiment_trend(obj):
        return obj.get_avg_sentiment()


class OrganizationSerializer(ConversationRelationshipSerializer):
    topics = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ['url', 'name', 'topics', 'conversation_trend', 'conversation_topic_trend', 'duration_trend',
                  'sentiment_trend']

    def get_topics(self, obj):
        # Return a list of topic names and descriptions
        topics = []
        for topic in obj.topics.all():
            topics.append(
                {
                    'name': topic.name,
                    'description': topic.description,
                    'url': self.context['request'].build_absolute_uri(reverse('topic-detail', args=[topic.pk]))
                }
            )
        return topics


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
    organization = serializers.HyperlinkedRelatedField(view_name='organization-detail', read_only=True)

    class Meta:
        model = Topic
        fields = ['url', 'name', 'description', 'organization']


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
    class Meta:
        model = Topic
        fields = ['url', 'name', 'description', 'summary_data', 'conversations', 'conversation_trend',
                  'conversation_topic_trend', 'duration_trend', 'sentiment_trend']


class AgentSerializer(ConversationRelationshipSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    manager = serializers.HyperlinkedRelatedField(view_name='agent-detail', read_only=True)
    manager_username = serializers.CharField(source='manager.user.username', read_only=True)
    agents = serializers.SerializerMethodField()

    class Meta:
        model = Agent
        fields = ['url', 'username', 'manager', 'manager_username', 'summary', 'summary_date', 'summary_call_count',
                  'agents', 'conversations', 'conversation_trend', 'conversation_topic_trend', 'duration_trend',
                  'sentiment_trend']

    def get_agents(self, obj):
        # Return a list of a manager's agents
        agents = []
        for agent in obj.agents.all():
            agents.append(
                {
                    'name': agent.user.username,
                    'summary': agent.summary,
                    'url': self.context['request'].build_absolute_uri(reverse('agent-detail', args=[agent.pk]))
                }
            )
        return agents


class CustomerSerializer(ConversationRelationshipSerializer):
    class Meta:
        model = Customer
        fields = ['url', 'name', 'summary', 'summary_date', 'summary_call_count', 'conversations', 'conversation_trend',
                  'conversation_topic_trend', 'duration_trend', 'sentiment_trend']
