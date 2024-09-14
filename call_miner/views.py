from .models import Conversation
from call_miner.serializers import ConversationSerializer
from rest_framework import viewsets
from rest_framework import permissions


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
