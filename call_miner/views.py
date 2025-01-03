from rest_framework import viewsets, decorators, response, status
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import F
from drf_spectacular.utils import extend_schema
from django.conf import settings
from call_miner.models import Conversation, Organization, OrganizationAPIKey, Topic, Employee, Agent, Customer
from call_miner.serializers import (
    ConversationModifySerializer, ConversationListSerializer, ConversationDetailSerializer,
    OrganizationDetailSerializer, OrganizationAPIKeyListSerializer, OrganizationAPIKeyModifySerializer,
    ConversationTrendsSerializer, MetaSummarySerializer, TopicModifySerializer, TopicListSerializer,
    AgentListSerializer, AgentDetailSerializer, CustomerModifySerializer, CustomerListSerializer,
    EmployeeListSerializer, EmployeeModifySerializer
)
from call_miner.permissions import (ConversationPermission, OrganizationPermission, OrganizationAPIKeyPermission,
                                    TopicPermission, AgentPermission, CustomerPermission, EmployeePermission)
from call_miner.utils.paginators import CustomListViewPaginator
from call_miner.authentication import FirebaseAuthentication
from call_miner.schemas import (
    ID_PARAMETER_SCHEMA, SUMMARY_DATA_RESPONSE_SCHEMA, ALL_SUMMARIES_RESPONSE_SCHEMA,
    CONVERSATIONS_RESPONSE_SCHEMA, TREND_RESPONSE_SCHEMA, TREND_PERIOD_PARAMETER_SCHEMA, PER_TOPIC_PARAMETER_SCHEMA,
    SEARCH_QUERY_PARAMETER_SCHEMA, REGENERATE_API_KEY_RESPONSE_SCHEMA, SEARCH_RESPONSE_SCHEMA,
    TRANSCRIPT_RESPONSE_SCHEMA, LIST_ACTIVE_TOPICS_RESPONSE_SCHEMA, MANAGED_AGENTS_RESPONSE_SCHEMA,
    ERROR_RESPONSE_SCHEMA, NOT_FOUND_RESPONSE_SCHEMA, FORBIDDEN_RESPONSE_SCHEMA
)


class SummaryActionsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet to outline the actions of the MetaSummarySerializer.
    """

    @staticmethod
    def define_trace_data(request, obj, name: str):
        """
        This method defines trace data to be used by Langfuse when recording an LLM trace
        """
        if hasattr(request.user, 'employee'):
            role = request.user.employee.role.lower()
            organization = request.user.employee.organization
        else:
            organization = None
            if request.user.is_superuser:
                role = 'superuser'
            else:
                role = 'unknown'
        return {
            'name': name, 'user_id': request.user.id, 'tags': [settings.TELLME_ENV],
            'metadata': {'organization': organization, 'role': role, 'object': str(type(obj)), 'id': obj.id}
        }

    @extend_schema(
        description=MetaSummarySerializer.get_summary_data.__doc__,
        parameters=[ID_PARAMETER_SCHEMA],
        responses={
            200: SUMMARY_DATA_RESPONSE_SCHEMA,
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=True, methods=['get'])
    def summary_data(self, request, pk=None):
        obj = self.get_object()
        trace_data = self.define_trace_data(request, obj, 'get_summary_data')
        serializer = self.get_serializer(obj, context={'trace_data': trace_data})
        try:
            return response.Response(serializer.get_summary_data(obj))
        except ValueError as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TrendsActionsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet to outline the actions of the ConversationTrendsSerializer.
    """
    @extend_schema(
        description=ConversationTrendsSerializer.get_conversations.__doc__,
        parameters=[ID_PARAMETER_SCHEMA],
        responses={
            200: CONVERSATIONS_RESPONSE_SCHEMA,
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=True, methods=['get'])
    def conversations(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        try:
            return response.Response(serializer.get_conversations(obj))
        except ValueError as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description=ConversationTrendsSerializer.get_trend.__doc__,
        parameters=[ID_PARAMETER_SCHEMA, TREND_PERIOD_PARAMETER_SCHEMA, PER_TOPIC_PARAMETER_SCHEMA],
        responses={
            200: TREND_RESPONSE_SCHEMA,
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=True, methods=['get'])
    def trend(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        try:
            return response.Response(serializer.get_trend(obj))
        except ValueError as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_context(self):
        return {'request': self.request}


class SearchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Abstract ViewSet containing a series of generic search actions that are re-used by multiple ViewSets
    """
    search_vector = None
    relationships_to_select = []
    relationships_to_prefetch = []

    @extend_schema(
        description='Search over all object instances given a query.',
        parameters=[SEARCH_QUERY_PARAMETER_SCHEMA],
        responses={
            200: SEARCH_RESPONSE_SCHEMA,
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Provides search results for a given query. Assumes that a search_vector has been previously defined at the level
        of the ViewSet inheriting this abstract ViewSet.
        """
        query = request.query_params.get('query', None)
        if not query:
            return response.Response({"detail": "No search query provided."}, status=400)

        search_query = SearchQuery(query, search_type='websearch')

        # Get the base queryset, and apply the query
        queryset = (
            self.get_queryset()
            .select_related(*self.relationships_to_select)
            .prefetch_related(*self.relationships_to_prefetch)
        )

        # Rank the search results by relevance, filter based on a relevance threshold, and sort based on the rank.
        queryset = (
            queryset
            .annotate(rank=SearchRank(self.search_vector, search_query))
            .filter(rank__gte=0.1)
            .order_by('-rank')
            .distinct()
        )

        # Return the results. If empty, raise a 404. Otherwise paginate if necessary.
        if not queryset.exists():
            return response.Response(
                {'detail': 'Your query produced no results.'},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True, context={'request': request})
            return response.Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet, SearchViewSet):
    """
    A ViewSet for the Conversation model. Inherits from the SearchViewSet to allow users to search for transcripts
    containing certain keywords.
    A summary of the permissions:
    - Modification is only allowed to superusers
    - Viewing is allowed to employees of the same organization as the conversation (and superusers)
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [ConversationPermission]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['-date']
    relationships_to_select = ['customer', 'agent']
    relationships_to_prefetch = ['topics']
    search_vector = (
        SearchVector('transcript', weight='A') +
        SearchVector('summary', weight='A') +
        SearchVector(F('topics__name'), weight='B')
    )

    def get_serializer_class(self):
        if self.action in ['list', 'search']:
            return ConversationListSerializer
        elif self.action in ['retrieve', 'transcript']:
            return ConversationDetailSerializer
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return ConversationModifySerializer
        raise ValueError(f'Action {self.action} not permitted.')

    def get_queryset(self):
        """
        Return conversations that belong to the user's organization
        """
        if self.request.user.is_superuser:
            return Conversation.objects.all()
        if self.request.user.employee.organization:
            return Conversation.objects.filter(agent__organization=self.request.user.employee.organization)
        return Conversation.objects.none()

    @extend_schema(
        description=ConversationDetailSerializer.get_processed_transcript.__doc__,
        parameters=[ID_PARAMETER_SCHEMA],
        responses={
            200: TRANSCRIPT_RESPONSE_SCHEMA,
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=True, methods=['get'])
    def transcript(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return response.Response(serializer.get_processed_transcript(obj))

    def get_serializer_context(self):
        return {'request': self.request}


class OrganizationViewSet(viewsets.ModelViewSet, TrendsActionsViewSet):
    """
    A ViewSet for the Organization model. Inherits from the TrendsActionsViewSet to obtain relevant conversation trends.
    A summary of the permissions:
    - Modification is only possible for superusers
    - Analysts can retrieve their own organization (and superusers can view anything)
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [OrganizationPermission]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['name']

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list', 'modify', 'create', 'update', 'destroy', 'partial_update']:
            return OrganizationDetailSerializer
        elif self.action in ['conversations', 'trend']:
            return ConversationTrendsSerializer
        raise ValueError(f'Action {self.action} not permitted.')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Organization.objects.all()
        if self.request.user.employee.organization:
            return Organization.objects.filter(pk=self.request.user.employee.organization.pk)
        return Organization.objects.none()


class OrganizationAPIKeyViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for the OrganizationAPIKey model. Used to create, delete, and list an organization's API keys.
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [OrganizationAPIKeyPermission]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return OrganizationAPIKey.objects.all()
        if self.request.user.employee.organization:
            return OrganizationAPIKey.objects.filter(organization=self.request.user.employee.organization)
        return OrganizationAPIKey.objects.none()

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return OrganizationAPIKeyListSerializer
        elif self.action in ['create', 'destroy', 'regenerate']:
            return OrganizationAPIKeyModifySerializer
        raise ValueError(f'Action {self.action} not permitted.')

    @extend_schema(
        description="Deletes and recreates an API key, maintaining its name and organization but re-setting its expiry",
        parameters=[ID_PARAMETER_SCHEMA],
        responses={
            200: REGENERATE_API_KEY_RESPONSE_SCHEMA,
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """
        Custom endpoint: delete the existing key, re-create one with the same name.
        """
        instance = self.get_object()
        name = instance.name
        organization = instance.organization
        instance.delete()

        data = {'name': name}
        if self.request.user.is_superuser:
            data['organization'] = organization.pk

        # Create a new key with the same name
        serializer = OrganizationAPIKeyModifySerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        created_instance = serializer.save()
        return response.Response(serializer.to_representation(created_instance), status=status.HTTP_201_CREATED)


class TopicViewSet(viewsets.ModelViewSet, TrendsActionsViewSet, SummaryActionsViewSet):
    """
    A ViewSet for the Topic model. Inherits from TrendsActionsViewSet to obtain conversation trends, as well as from the
    SummaryActionsViewSet, to obtain meta-summaries of all the associated conversation summaries.
    A summary of the permissions:
    - Modification is allowed to superusers and analysts of the same organization
    - Viewing is allowed to employees of the same organization (and superusers)
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [TopicPermission]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['-is_active', '-conversation_count', 'name']

    def get_serializer_class(self):
        if self.action in ['list', 'list_active', 'retrieve']:
            return TopicListSerializer
        elif self.action in ['summary_data', 'all_summaries']:
            return MetaSummarySerializer
        elif self.action in ['conversations', 'trend']:
            return ConversationTrendsSerializer
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return TopicModifySerializer
        raise ValueError(f'Action {self.action} not permitted.')

    def get_queryset(self):
        """
        Return topics that belong to the user's organization
        """
        if self.request.user.is_superuser:
            return Topic.objects.all()
        if self.request.user.employee.organization:
            if self.action in ['list_active', 'all_summaries']:
                return Topic.objects.filter(organization=self.request.user.employee.organization, is_active=True)
            else:
                return Topic.objects.filter(organization=self.request.user.employee.organization)
        return Topic.objects.none()

    @extend_schema(
        description="List active topics of an organization",
        responses=LIST_ACTIVE_TOPICS_RESPONSE_SCHEMA
    )
    @decorators.action(detail=False, methods=['get'], url_path='list_active')
    def list_active(self, request):
        """
        Custom action to list only active topics
        """
        return self.list(request)

    @extend_schema(
        responses={
            200: ALL_SUMMARIES_RESPONSE_SCHEMA,
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=False, methods=['get'], url_path='all_summaries')
    def all_summaries(self, request):
        """
        This method takes get_summary_data a step further, obtaining the summary data of all topics in the queryset.
        The response is now a dictionary, where the key corresponds to the topic ID.
        """
        queryset = self.get_queryset()
        try:
            summaries = {}
            for obj in queryset:
                trace_data = self.define_trace_data(request, obj, 'get_all_summaries')
                serializer = self.get_serializer(obj, context={'trace_data': trace_data})
                summary_data = serializer.get_summary_data(obj)
                summary_data['name'] = obj.name
                summaries[obj.id] = summary_data
            return response.Response(summaries)
        except ValueError as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AgentViewSet(TrendsActionsViewSet, SummaryActionsViewSet):
    """
    A ViewSet for the Agent model. Inherits from TrendsActionsViewSet to obtain conversation trends, as well as from the
    SummaryActionsViewSet, to obtain meta-summaries of all the associated conversation summaries. This ViewSet is
    read-only since Employee-level modifications should be done with the Employee ViewSet.
    A summary of the permissions:
    - Modification is only allowed to superusers, although this is not the ViewSet for it
    - Listing is possible to Employees of the same organization. Retrieving a single Agent is only possible to the agent
        itself, to its manager, or to an organization admin of the same organization (and superusers).
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
        elif self.action in ['conversations', 'trend']:
            return ConversationTrendsSerializer
        raise ValueError(f'Action {self.action} not permitted.')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Agent.objects.all()
        if self.request.user.employee.organization:
            return Agent.objects.filter(organization=self.request.user.employee.organization)
        return Agent.objects.none()

    @extend_schema(
        description="List agents under management of the current agent",
        parameters=[ID_PARAMETER_SCHEMA],
        responses={
            200: MANAGED_AGENTS_RESPONSE_SCHEMA,
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=True, methods=['get'])
    def managed_agents(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        return response.Response(serializer.get_agent_data(obj))


class CustomerViewSet(viewsets.ModelViewSet, TrendsActionsViewSet, SummaryActionsViewSet):
    """
    A ViewSet for the Customer model. This ViewSet inherits from:
    - TrendsActionsViewSet: to obtain conversation trends of a single Customer
    - SummaryActionsViewSet: to obtain meta-summaries of a customer's conversation summaries

    The ViewSet permissions can be summarized as follows:
    - Modification is only allowed to superusers
    - Viewing is allowed to any employee of the same organization (and superusers)
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [CustomerPermission]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['-last_conversation_date', 'conversation_count']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CustomerListSerializer
        elif self.action in ['summary_data']:
            return MetaSummarySerializer
        elif self.action in ['conversations', 'trend']:
            return ConversationTrendsSerializer
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return CustomerModifySerializer
        raise ValueError(f'Action {self.action} not permitted.')

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
    """
    A ViewSet for the Employee model. This is the ViewSet to be used to alter Agent and Analyst data.
    A summary of the permissions:
    - Modification is allowed to superusers and organization admins of the same organization
    - Listing is only available to organization admins (and superusers), and retrieving a single employee is possible
        for organization admins of the same organization and the employee itself (and superusers).
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [EmployeePermission]
    serializer_class = EmployeeModifySerializer

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return EmployeeListSerializer
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return EmployeeModifySerializer
        raise ValueError(f'Action {self.action} not permitted.')

    def get_queryset(self):
        """
        Return employees that belong to the user's organization
        """
        if self.request.user.is_superuser:
            return Employee.objects.all()
        if self.request.user.employee.organization:
            return Employee.objects.filter(organization=self.request.user.employee.organization)
        return Employee.objects.none()
