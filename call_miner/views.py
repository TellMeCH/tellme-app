from .models import Conversation, Topic
from call_miner.serializers import ConversationSerializer, TopicSerializer
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        # Get the instance of the Topic model
        topic = self.get_object()

        # Run the get_or_create_summary method before returning the object
        topic.get_or_create_summary()

        # Serialize the topic and return the response
        serializer = self.get_serializer(topic)
        return Response(serializer.data, status=status.HTTP_200_OK)

