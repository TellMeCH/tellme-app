from rest_framework import serializers
from tellme.call_processing.utils.llm_configs import TRANSCRIPTION_METHOD_CHOICES, ENRICHMENT_METHOD_CHOICES


class WebhookProcessingSerializer(serializers.Serializer):
    """
    A serializer for Webhooks notifying of a call event (Provisional)
    """
    call_sid = serializers.CharField(required=True)
    customer_id = serializers.IntegerField(required=False)
    agent_id = serializers.IntegerField(required=True)
    timestamp = serializers.DateTimeField(required=True)
    call_status = serializers.CharField(required=True)


class QueueRecordingSerializer(serializers.Serializer):
    """
    A serializer for requests adding a call processing task to the queue
    """
    customer_id = serializers.CharField(required=False)
    agent_id = serializers.IntegerField(required=True)
    timestamp = serializers.DateTimeField(required=True)
    file = serializers.FileField(required=True)
    duration = serializers.FloatField(required=False, allow_null=True, default=None)


class ProcessRecordingSerializer(serializers.Serializer):
    """
    A serializer for requests from the Cloud Task Manager to process a recording
    """
    file_name = serializers.CharField(required=True)
    organization_id = serializers.IntegerField(required=True)
    customer_id = serializers.CharField(required=False, allow_null=True)
    agent_id = serializers.IntegerField(required=True)
    timestamp = serializers.DateTimeField(required=True)
    transcription_method = serializers.ChoiceField(choices=TRANSCRIPTION_METHOD_CHOICES, required=True)
    enrichment_method = serializers.ChoiceField(choices=ENRICHMENT_METHOD_CHOICES, required=True)


class SummarizationSerializer(serializers.Serializer):
    """
    A serializer for requests from the Cloud Task Manager to create summaries
    """
    object_id = serializers.IntegerField(required=True)
    object_type = serializers.CharField(required=True)
    summary_period = serializers.CharField(required=True)
    rolling_period = serializers.BooleanField(required=True)
    task_id = serializers.CharField(required=False, allow_null=True)
