from rest_framework import serializers
from call_miner.models import Conversation


class ConversationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Conversation
        fields = ['url', 'path', 'date', 'duration', 'transcript', 'sentiment', 'summary', 'input_tokens',
                  'output_tokens', 'processed_messages']
