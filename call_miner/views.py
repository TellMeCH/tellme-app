from rest_framework import viewsets, decorators, response, status
from .models import Conversation, Organization, Topic, Employee, Agent, Customer
from call_miner.serializers import (
    ConversationModifySerializer, ConversationListSerializer, ConversationDetailSerializer,
    OrganizationDetailSerializer, ConversationTrendsSerializer, MetaSummarySerializer, TopicModifySerializer,
    TopicListSerializer, AgentListSerializer, AgentDetailSerializer, CustomerModifySerializer, CustomerListSerializer,
    EmployeeListSerializer, EmployeeModifySerializer
)
from call_miner.permissions import (ConversationPermission, OrganizationPermission, TopicPermission, AgentPermission,
                                    CustomerPermission, EmployeePermission)
from call_miner.utils.paginators import CustomListViewPaginator
from call_miner.authentication import FirebaseAuthentication


class SummaryActionsViewSet(viewsets.ReadOnlyModelViewSet):
    @decorators.action(detail=True, methods=['get'])
    def summary_data(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        try:
            return response.Response({'summary_data': serializer.get_summary_data(obj)})
        except ValueError as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TrendsActionsViewSet(viewsets.ReadOnlyModelViewSet):
    @decorators.action(detail=True, methods=['get'])
    def conversations(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        try:
            return response.Response({'conversations': serializer.get_conversations(obj)})
        except ValueError as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=True, methods=['get'])
    def conversation_trend(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        try:
            return response.Response({'conversation_trend': serializer.get_conversation_trend(obj)})
        except ValueError as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=True, methods=['get'])
    def conversation_topic_trend(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        try:
            return response.Response({'conversation_topic_trend': serializer.get_conversation_topic_trend(obj)})
        except ValueError as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=True, methods=['get'])
    def duration_trend(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        try:
            return response.Response({'duration_trend': serializer.get_duration_trend(obj)})
        except ValueError as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(detail=True, methods=['get'])
    def sentiment_trend(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        try:
            return response.Response({'sentiment_trend': serializer.get_sentiment_trend(obj)})
        except ValueError as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_context(self):
        # Ensure the request context is passed to the serializer
        return {'request': self.request}


class ConversationViewSet(viewsets.ModelViewSet):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [ConversationPermission]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['-date']

    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        elif self.action in ['retrieve', 'transcript']:
            return ConversationDetailSerializer
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return ConversationModifySerializer
        return ConversationListSerializer

    def get_queryset(self):
        """
        Return conversations that belong to the user's organization
        """
        if self.request.user.is_superuser:
            return Conversation.objects.all()
        if self.request.user.employee.organization:
            return Conversation.objects.filter(agent__organization=self.request.user.employee.organization)
        return Conversation.objects.none()

    @decorators.action(detail=True, methods=['get'])
    def transcript(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return response.Response({'transcript': serializer.get_processed_transcript(obj)})

    def get_serializer_context(self):
        # Ensure the request context is passed to the serializer
        return {'request': self.request}


class OrganizationViewSet(viewsets.ModelViewSet, TrendsActionsViewSet):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [OrganizationPermission]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['name']

    def get_serializer_class(self):
        if self.action in ['retrieve']:
            return OrganizationDetailSerializer
        elif self.action in ['conversations', 'conversation_trend', 'conversation_topic_trend', 'duration_trend',
                             'sentiment_trend']:
            return ConversationTrendsSerializer
        return OrganizationDetailSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Organization.objects.all()
        if self.request.user.employee.organization:
            return Organization.objects.filter(pk=self.request.user.employee.organization.pk)
        return Organization.objects.none()


class TopicViewSet(viewsets.ModelViewSet, TrendsActionsViewSet, SummaryActionsViewSet):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [TopicPermission]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['-is_active', '-conversation_count', 'name']

    def get_serializer_class(self):
        if self.action in ['list', 'list_active', 'retrieve']:
            return TopicListSerializer
        elif self.action in ['summary_data']:
            return MetaSummarySerializer
        elif self.action in ['conversations', 'conversation_trend', 'duration_trend', 'sentiment_trend']:
            return ConversationTrendsSerializer
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return TopicModifySerializer
        return TopicListSerializer

    def get_queryset(self):
        """
        Return topics that belong to the user's organization
        """
        if self.request.user.is_superuser:
            return Topic.objects.all()
        if self.request.user.employee.organization:
            if self.action == 'list_active':
                return Topic.objects.filter(organization=self.request.user.employee.organization, is_active=True)
            else:
                return Topic.objects.filter(organization=self.request.user.employee.organization)
        return Topic.objects.none()

    @decorators.action(detail=False, methods=['get'], url_path='list_active')
    def list_active(self, request):
        """
        Custom action to list only active topics
        """
        return self.list(request)

    def conversation_topic_trend(self, request, *args, **kwargs):
        # This action will not appear in the API schema
        pass


class AgentViewSet(TrendsActionsViewSet, SummaryActionsViewSet):
    """
    This ViewSet allows to view details from all or a single Agent in an organization. Please note that it's read-only,
    since Employee-level modifications should be done with the Employee ViewSet.
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [AgentPermission]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['-conversation_count', 'user_id']

    def get_serializer_class(self):
        if self.action == 'list':
            return AgentListSerializer
        elif self.action in ['retrieve', 'managed_agents']:
            return AgentDetailSerializer
        elif self.action in ['summary_data']:
            return MetaSummarySerializer
        elif self.action in ['conversations', 'conversation_trend', 'conversation_topic_trend', 'duration_trend',
                             'sentiment_trend']:
            return ConversationTrendsSerializer
        return AgentListSerializer

    def get_queryset(self):
        """
        Return agents that belong to the user's organization
        """
        if self.request.user.is_superuser:
            return Agent.objects.all()
        if self.request.user.employee.organization:
            return Agent.objects.filter(organization=self.request.user.employee.organization)
        return Agent.objects.none()

    @decorators.action(detail=True, methods=['get'])
    def managed_agents(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return response.Response({'managed_agents': serializer.get_agent_data(obj)})


class CustomerViewSet(viewsets.ModelViewSet, TrendsActionsViewSet, SummaryActionsViewSet):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [CustomerPermission]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['-conversation_count', 'name']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CustomerListSerializer
        elif self.action in ['summary_data']:
            return MetaSummarySerializer
        elif self.action in ['conversations', 'conversation_trend', 'conversation_topic_trend', 'duration_trend',
                             'sentiment_trend']:
            return ConversationTrendsSerializer
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return CustomerModifySerializer
        return CustomerListSerializer

    def get_queryset(self):
        """
        Return agents that belong to the user's organization
        """
        if self.request.user.is_superuser:
            return Customer.objects.all()
        if self.request.user.employee.organization:
            return Customer.objects.filter(organization=self.request.user.employee.organization)
        return Customer.objects.none()


class EmployeeViewSet(viewsets.ModelViewSet):
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [EmployeePermission]
    serializer_class = EmployeeModifySerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return EmployeeListSerializer
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return EmployeeModifySerializer
        return EmployeeListSerializer

    def get_queryset(self):
        """
        Return employees that belong to the user's organization
        """
        if self.request.user.is_superuser:
            return Employee.objects.all()
        if self.request.user.employee.organization:
            return Employee.objects.filter(organization=self.request.user.employee.organization)
        return Employee.objects.none()
