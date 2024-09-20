from .models import Conversation, Topic
from call_miner.serializers import ConversationSerializer, TopicSerializer
from call_miner.permissions import IsOrganizationMember, IsAnalyst
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        """
        Return conversations that belong to the user's organization
        """
        print(self.request.user.employee.__dict__)
        if self.request.user.employee.organization:
            return Conversation.objects.filter(agent__organization=self.request.user.employee.organization)
        return Conversation.objects.none()


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember, IsAnalyst]

    def get_queryset(self):
        """
        Return conversations that belong to the user's organization
        """
        if self.request.user.employee.organization:
            return Topic.objects.filter(organization=self.request.user.employee.organization)
        return Conversation.objects.none()

    def retrieve(self, request, *args, **kwargs):
        # Get the instance of the Topic model
        topic = self.get_object()

        # Run the get_or_create_summary method before returning the object
        topic.get_or_create_summary()

        # Serialize the topic and return the response
        serializer = self.get_serializer(topic)
        return Response(serializer.data, status=status.HTTP_200_OK)

