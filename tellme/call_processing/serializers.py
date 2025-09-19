from rest_framework import serializers
from tellme.call_processing.utils.llm_configs import TRANSCRIPTION_METHOD_CHOICES, ENRICHMENT_METHOD_CHOICES


class WebhookProcessingSerializer(serializers.Serializer):
    """
    A serializer for Webhooks notifying of a call event (Provisional)
    """
    call_sid = serializers.CharField(required=True)
    customer_id = serializers.IntegerField(required=True)
    agent_id = serializers.IntegerField(required=True)
    timestamp = serializers.DateTimeField(required=True)
    call_status = serializers.CharField(required=True)


class QueueRecordingSerializer(serializers.Serializer):
    """
    A serializer for requests adding a call processing task to the queue
    """
    customer_id = serializers.CharField(required=True)
    agent_id = serializers.IntegerField(required=True)
    timestamp = serializers.DateTimeField(required=True)
    file = serializers.FileField(required=True)


class ProcessRecordingSerializer(serializers.Serializer):
    """
    A serializer for requests from the Cloud Task Manager to process a recording
    """
    file_name = serializers.CharField(required=True)
    organization_id = serializers.IntegerField(required=True)
    customer_id = serializers.CharField(required=True)
    agent_id = serializers.IntegerField(required=True)
    timestamp = serializers.DateTimeField(required=True)
    transcription_method = serializers.ChoiceField(choices=TRANSCRIPTION_METHOD_CHOICES, required=True)
    enrichment_method = serializers.ChoiceField(choices=ENRICHMENT_METHOD_CHOICES, required=True)
