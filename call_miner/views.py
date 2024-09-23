from .models import Conversation, Organization, Topic, Agent, Customer
from call_miner.serializers import (
    ConversationModifySerializer, ConversationListSerializer, ConversationDetailSerializer, OrganizationSerializer,
    TopicModifySerializer, TopicListSerializer, TopicDetailSerializer, AgentSerializer, CustomerSerializer
)
from call_miner.permissions import IsSuperUserToModify, IsOrganizationMember, IsAnalyst, IsManager
from rest_framework import viewsets, mixins
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status


"""
Breaking down desired behavior on ViewSet Access:
- ConversationViewSet: viewable by anyone in the org. Anyone can view the details of a single call
- OrganizationViewSet: Users can only list and view their own organization
- TopicViewSet: topics can be listed by anyone in the org, but only Analysts can view and alter the details of a topic
- AgentViewSet: agents can be listed by anyone in the org, but only an agent or its manager can view the details of the agent
- CustomerViewSet: viewable by anyone in the org. Anyone can view the details of a single customer 
"""


class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsSuperUserToModify, IsOrganizationMember]

    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        elif self.action == 'retrieve':
            return ConversationDetailSerializer
        elif self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return ConversationModifySerializer
        return ConversationListSerializer

    def get_queryset(self):
        """
        Return conversations that belong to the user's organization
        """
        if self.request.user.employee.organization:
            return Conversation.objects.filter(agent__organization=self.request.user.employee.organization)
        return Conversation.objects.none()

    def get_serializer_context(self):
        # Ensure the request context is passed to the serializer
        return {'request': self.request}


class OrganizationViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember, IsAnalyst]

    def get_queryset(self):
        if self.request.user.employee.organization:
            return Organization.objects.filter(pk=self.request.user.employee.organization.pk)
        return Organization.objects.none()

    def get_serializer_context(self):
        # Ensure the request context is passed to the serializer
        return {'request': self.request}


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember, IsAnalyst]

    def get_serializer_class(self):
        if self.action == 'list':
            return TopicListSerializer
        elif self.action == 'retrieve':
            return TopicDetailSerializer
        elif self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return TopicModifySerializer
        return TopicListSerializer

    def get_queryset(self):
        """
        Return topics that belong to the user's organization
        """
        if self.request.user.employee.organization:
            return Topic.objects.filter(organization=self.request.user.employee.organization)
        return Topic.objects.none()

    def get_serializer_context(self):
        # Ensure the request context is passed to the serializer
        return {'request': self.request}


class AgentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AgentSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserToModify, IsOrganizationMember, IsManager]

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

    def get_serializer_context(self):
        # Ensure the request context is passed to the serializer
        return {'request': self.request}


class CustomerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUserToModify, IsOrganizationMember]

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

    def get_serializer_context(self):
        # Ensure the request context is passed to the serializer
        return {'request': self.request}

