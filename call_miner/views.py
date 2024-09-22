from .models import Conversation, Topic, Agent, Customer
from call_miner.serializers import ConversationSerializer, TopicSerializer, AgentSerializer, CustomerSerializer
from call_miner.permissions import IsOrganizationMember, IsAnalyst, IsManager
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status


"""
Breaking down desired behavior on ViewSet Access:
- ConversationViewSet: viewable by anyone. Anyone can view the details of a single call
- TopicViewSet: topics can be listed by anyone, but only Analysts can view and alter the details of a topic
- AgentViewSet: agents can be listed by anyone, but only an agent or its manager can view the details of the agent
- CustomerViewSet: viewable by anyone. Anyone can view the details of a single customer 
"""


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

    def get_serializer_context(self):
        # Ensure the request context is passed to the serializer
        return {'request': self.request}


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember, IsAnalyst]

    def get_queryset(self):
        """
        Return topics that belong to the user's organization
        """
        if self.request.user.employee.organization:
            return Topic.objects.filter(organization=self.request.user.employee.organization)
        return Topic.objects.none()

    def retrieve(self, request, *args, **kwargs):
        # Get the instance of the Topic model
        topic = self.get_object()

        # Run the get_or_create_summary method before returning the object
        topic.get_or_create_summary()

        # Serialize the topic and return the response
        serializer = self.get_serializer(topic)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AgentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember, IsManager]

    def get_queryset(self):
        """
        Return agents that belong to the user's organization
        """
        if self.request.user.employee.organization:
            return Agent.objects.filter(organization=self.request.user.employee.organization)
        return Agent.objects.none()

    def retrieve(self, request, *args, **kwargs):
        # Get the instance of the Agent model
        agent = self.get_object()

        # Run the get_or_create_summary method before returning the object
        agent.get_or_create_summary()

        # Serialize the topic and return the response
        serializer = self.get_serializer(agent)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        """
        Return agents that belong to the user's organization
        """
        if self.request.user.employee.organization:
            return Customer.objects.filter(organization=self.request.user.employee.organization)
        return Customer.objects.none()

    def retrieve(self, request, *args, **kwargs):
        # Get the instance of the Customer model
        customer = self.get_object()

        # Run the get_or_create_summary method before returning the object
        customer.get_or_create_summary()

        # Serialize the topic and return the response
        serializer = self.get_serializer(customer)
        return Response(serializer.data, status=status.HTTP_200_OK)

