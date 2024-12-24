from rest_framework import serializers


class QueueRecordingSerializer(serializers.Serializer):
    """
    A serializer for requests adding a call processing task to the queue
    """
    organization_id = serializers.IntegerField(required=True)
    customer_id = serializers.CharField(required=True)
    agent_id = serializers.IntegerField(required=True)
    timestamp = serializers.DateTimeField(required=True)
    file = serializers.FileField(required=True)
