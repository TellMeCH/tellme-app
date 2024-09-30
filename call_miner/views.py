from .models import Conversation, Organization, Topic, Agent, Customer
from rest_framework import viewsets, permissions, decorators, response
from call_miner.serializers import (
    ConversationModifySerializer, ConversationListSerializer, ConversationDetailSerializer,
    OrganizationDetailSerializer, ConversationStatsSerializer, MetaSummarySerializer, TopicModifySerializer,
    TopicListSerializer, TopicDetailSerializer, AgentModifySerializer, AgentListSerializer, AgentDetailSerializer,
    CustomerModifySerializer, CustomerListSerializer, CustomerDetailSerializer
)
from call_miner.permissions import IsSuperUserToModify, IsOrganizationMember, IsAnalyst, IsManager
from call_miner.utils.paginators import CustomListViewPaginator


"""
Breaking down desired behavior on ViewSet Access:
- ConversationViewSet: viewable by anyone in the org. Anyone can view the details of a single call
- OrganizationViewSet: Users can only list and view their own organization
- TopicViewSet: topics can be listed by anyone in the org, but only Analysts can view and alter the details of a topic
- AgentViewSet: agents can be listed by anyone in the org, but only an agent or its manager can view the agent details
- CustomerViewSet: viewable by anyone in the org. Anyone can view the details of a single customer 
"""


class SummaryActionsViewSet(viewsets.ReadOnlyModelViewSet):
    @decorators.action(detail=True, methods=['get'])
    def summary_data(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return response.Response({'summary_data': serializer.get_summary_data(obj)})


class StatisticsActionsViewSet(viewsets.ReadOnlyModelViewSet):
    @decorators.action(detail=True, methods=['get'])
    def conversations(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return response.Response({'conversations': serializer.get_conversations(obj)})

    @decorators.action(detail=True, methods=['get'])
    def conversation_trend(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return response.Response({'conversation_trend': serializer.get_conversation_trend(obj)})

    @decorators.action(detail=True, methods=['get'])
    def conversation_topic_trend(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return response.Response({'conversation_topic_trend': serializer.get_conversation_topic_trend(obj)})

    @decorators.action(detail=True, methods=['get'])
    def duration_trend(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return response.Response({'duration_trend': serializer.get_duration_trend(obj)})

    @decorators.action(detail=True, methods=['get'])
    def sentiment_trend(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return response.Response({'sentiment_trend': serializer.get_sentiment_trend(obj)})


class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsSuperUserToModify, IsOrganizationMember]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['-date']

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


class OrganizationViewSet(StatisticsActionsViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember, IsAnalyst]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['name']

    def get_serializer_class(self):
        if self.action in ['retrieve', 'topics']:
            return OrganizationDetailSerializer
        elif self.action in ['conversations', 'conversation_trend', 'conversation_topic_trend', 'duration_trend',
                             'sentiment_trend']:
            return ConversationStatsSerializer
        return OrganizationDetailSerializer

    def get_queryset(self):
        if self.request.user.employee.organization:
            return Organization.objects.filter(pk=self.request.user.employee.organization.pk)
        return Organization.objects.none()

    def get_serializer_context(self):
        # Ensure the request context is passed to the serializer
        return {'request': self.request}

    @decorators.action(detail=True, methods=['get'])
    def topics(self, request, pk=None):
        org = self.get_object()
        serializer = self.get_serializer(org)
        return response.Response({'topics': serializer.get_topic_data(org)})


class TopicViewSet(StatisticsActionsViewSet, SummaryActionsViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember, IsAnalyst]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['-name']

    def get_serializer_class(self):
        if self.action == 'list':
            return TopicListSerializer
        elif self.action == 'retrieve':
            return TopicDetailSerializer
        elif self.action in ['summary_data']:
            return MetaSummarySerializer
        elif self.action in ['conversations', 'conversation_trend', 'duration_trend', 'sentiment_trend']:
            return ConversationStatsSerializer
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
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

    def conversation_topic_trend(self, request, *args, **kwargs):
        # This action will not appear in the API schema
        pass


class AgentViewSet(StatisticsActionsViewSet, SummaryActionsViewSet):
    permission_classes = [permissions.IsAuthenticated, IsSuperUserToModify, IsOrganizationMember, IsManager]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['-user_id']

    def get_serializer_class(self):
        if self.action == 'list':
            return AgentListSerializer
        elif self.action == 'retrieve':
            return AgentDetailSerializer
        elif self.action in ['summary_data']:
            return MetaSummarySerializer
        elif self.action in ['conversations', 'conversation_trend', 'conversation_topic_trend', 'duration_trend',
                             'sentiment_trend']:
            return ConversationStatsSerializer
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return AgentModifySerializer
        return AgentListSerializer

    def get_queryset(self):
        """
        Return agents that belong to the user's organization
        """
        if self.request.user.employee.organization:
            return Agent.objects.filter(organization=self.request.user.employee.organization)
        return Agent.objects.none()

    def get_serializer_context(self):
        # Ensure the request context is passed to the serializer
        return {'request': self.request}


class CustomerViewSet(StatisticsActionsViewSet, SummaryActionsViewSet):
    permission_classes = [permissions.IsAuthenticated, IsSuperUserToModify, IsOrganizationMember]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['-name']

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        elif self.action == 'retrieve':
            return CustomerDetailSerializer
        elif self.action in ['summary_data']:
            return MetaSummarySerializer
        elif self.action in ['conversations', 'conversation_trend', 'conversation_topic_trend', 'duration_trend',
                             'sentiment_trend']:
            return ConversationStatsSerializer
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return CustomerModifySerializer
        return CustomerListSerializer

    def get_queryset(self):
        """
        Return agents that belong to the user's organization
        """
        if self.request.user.employee.organization:
            return Customer.objects.filter(organization=self.request.user.employee.organization)
        return Customer.objects.none()

    def get_serializer_context(self):
        # Ensure the request context is passed to the serializer
        return {'request': self.request}
