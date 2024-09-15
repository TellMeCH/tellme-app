from rest_framework import serializers
from call_miner.models import Conversation, Topic


class ConversationSerializer(serializers.HyperlinkedModelSerializer):
    processed_transcript = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['url', 'path', 'date', 'duration', 'transcript', 'summary', 'sentiment', 'topics', 'input_tokens',
                  'output_tokens', 'processed_transcript']

    @staticmethod
    def get_processed_transcript(obj):
        return obj.process_transcript()


class TopicSerializer(serializers.HyperlinkedModelSerializer):
    conversations = serializers.HyperlinkedRelatedField(many=True, view_name='conversation-detail', read_only=True)
    conversation_trend = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = ['url', 'name', 'description', 'slug', 'summary', 'summary_date', 'summary_call_count',
                  'conversations', 'conversation_trend']

    @staticmethod
    def get_conversation_trend(obj):
        return obj.get_conversation_trend()

