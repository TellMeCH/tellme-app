from django.urls import reverse
from rest_framework import serializers
from call_miner.models import Conversation, Organization, Topic, Agent, Customer


class ConversationPostSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer is used for POST requests creating a new Conversation instance. Note that the conversation's
    topics, agent and customer have to be specified with their primary keys.
    """
    topics = serializers.PrimaryKeyRelatedField(many=True, queryset=Topic.objects.all())
    agent = serializers.PrimaryKeyRelatedField(queryset=Agent.objects.all())
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())

    class Meta:
        model = Conversation
        fields = ['url', 'path', 'date', 'duration', 'transcript', 'summary', 'title', 'sentiment', 'topics',
                  'agent', 'customer', 'input_tokens', 'output_tokens']


class ConversationListSerializer(serializers.HyperlinkedModelSerializer):
    """
    This serializer is used for the GET requests listing all Conversation instances. Here, topics, agents and
    customers are lists with their names and hyperlinks.
    """
    topics = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['url', 'path', 'date', 'duration', 'transcript', 'summary', 'title', 'sentiment', 'topics',
                  'agent', 'customer', 'input_tokens', 'output_tokens']

    @staticmethod
    def get_topics(obj):
        # Return a list of topic names and descriptions
        return [{'name': topic.name, 'description': topic.description} for topic in obj.topics.all()][:3]

    def get_agent(self, obj):
        # Return the agent's name and hyperlink to their detail view
        agent_url = self.context['request'].build_absolute_uri(reverse('agent-detail', args=[obj.agent.pk]))
        return {
            'name': obj.agent.user.username,
            'url': agent_url
        }

    def get_customer(self, obj):
        # Return the customer's name and hyperlink to their detail view
        customer_url = self.context['request'].build_absolute_uri(
            reverse('customer-detail', args=[obj.customer.pk])
        )
        return {
            'name': obj.customer.name,
            'url': customer_url
        }


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
                  'agent', 'customer', 'input_tokens', 'output_tokens', 'processed_transcript']

    @staticmethod
    def get_topics(obj):
        # Return a list of topic names and descriptions
        return [{'name': topic.name, 'description': topic.description} for topic in obj.topics.all()]

    @staticmethod
    def get_processed_transcript(obj):
        return obj.process_transcript()


class ConversationRelationshipSerializer(serializers.HyperlinkedModelSerializer):
    conversations = serializers.SerializerMethodField()
    conversation_trend = serializers.SerializerMethodField()
    conversation_topic_trend = serializers.SerializerMethodField()
    duration_trend = serializers.SerializerMethodField()
    sentiment_trend = serializers.SerializerMethodField()

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


class TopicSerializer(ConversationRelationshipSerializer):
    class Meta:
        model = Topic
        fields = ['url', 'name', 'description', 'summary', 'summary_date', 'summary_call_count',
                  'conversations', 'conversation_trend', 'conversation_topic_trend', 'duration_trend',
                  'sentiment_trend']


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
