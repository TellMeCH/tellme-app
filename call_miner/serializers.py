from django.urls import reverse
from rest_framework import serializers
from call_miner.models import Conversation, Topic, Agent, Customer


class ConversationSerializer(serializers.HyperlinkedModelSerializer):
    topics = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    processed_transcript = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['url', 'path', 'date', 'duration', 'transcript', 'summary', 'title', 'sentiment', 'topics',
                  'agent', 'customer', 'input_tokens', 'output_tokens', 'processed_transcript']

    def __init__(self, *args, **kwargs):
        super(ConversationSerializer, self).__init__(*args, **kwargs)

        # Check the request method from the context
        if self.context.get('request').method == 'POST':
            # For POST requests, use PrimaryKeyRelatedField for topics, agent, and customer
            self.fields['topics'] = serializers.PrimaryKeyRelatedField(many=True, queryset=Topic.objects.all())
            self.fields['agent'] = serializers.PrimaryKeyRelatedField(queryset=Agent.objects.all())
            self.fields['customer'] = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
        else:
            # For GET requests, return topics, agent, and customer with their names and URLs
            self.fields['topics'] = serializers.SerializerMethodField()
            self.fields['agent'] = serializers.SerializerMethodField()
            self.fields['customer'] = serializers.SerializerMethodField()

    def get_topics(self, obj):
        # Return a list of topic names and descriptions
        return [{'name': topic.name, 'description': topic.description} for topic in obj.topics.all()]

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

    @staticmethod
    def get_processed_transcript(obj):
        return obj.process_transcript()


class ConversationRelationshipSerializer(serializers.HyperlinkedModelSerializer):
    conversations = serializers.SerializerMethodField()
    conversation_trend = serializers.SerializerMethodField()

    @staticmethod
    def get_conversation_trend(obj):
        return obj.get_conversation_trend()

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


class TopicSerializer(ConversationRelationshipSerializer):
    class Meta:
        model = Topic
        fields = ['url', 'name', 'description', 'summary', 'summary_date', 'summary_call_count',
                  'conversations', 'conversation_trend']


class AgentSerializer(ConversationRelationshipSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    manager = serializers.HyperlinkedRelatedField(view_name='agent-detail', read_only=True)
    manager_username = serializers.CharField(source='manager.user.username', read_only=True)

    class Meta:
        model = Agent
        fields = ['url', 'username', 'manager', 'manager_username', 'summary', 'summary_date', 'summary_call_count',
                  'conversations', 'conversation_trend']


class CustomerSerializer(ConversationRelationshipSerializer):
    class Meta:
        model = Customer
        fields = ['url', 'name', 'summary', 'summary_date', 'summary_call_count', 'conversations', 'conversation_trend']
