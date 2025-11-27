import zoneinfo
from rest_framework import viewsets, decorators, response, status, mixins, filters
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import F, Max, Avg, Sum
from datetime import datetime, timedelta
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import MethodNotAllowed
from django.conf import settings
from tellme.call_miner.models import (
    Conversation, Organization, OrganizationAPIKey, Topic, SuggestedTopic, Employee, Agent, Customer
)
from tellme.call_miner.serializers import (
    ConversationModifySerializer, ConversationListSerializer, ConversationDetailSerializer,
    OrganizationSerializer, OrganizationAPIKeyListSerializer, OrganizationAPIKeyModifySerializer,
    ConversationTrendsSerializer, MetaSummarySerializer, TopicModifySerializer, TopicListSerializer,
    SuggestedTopicAcceptSerializer, SuggestedTopicListSerializer, AgentListSerializer, AgentDetailSerializer,
    CustomerModifySerializer, CustomerListSerializer, EmployeeListSerializer, EmployeeModifySerializer
)
from tellme.call_miner.permissions import (ConversationPermission, OrganizationPermission, OrganizationAPIKeyPermission,
                                    TopicPermission, AgentPermission, CustomerPermission, EmployeePermission)
from tellme.call_miner.utils.paginators import CustomListViewPaginator
from tellme.call_miner.utils.period_utils import period_bounds
from tellme.call_miner.utils.summary_utils import DEFAULT_SUMMARY_SETTINGS
from tellme.call_miner.authentication import FirebaseAuthentication
from tellme.call_miner.schemas import (
    ID_PARAMETER_SCHEMA, SUMMARY_PERIOD_PARAMETER_SCHEMA, SUMMARY_ROLLING_PARAMETER_SCHEMA,
    SUMMARY_DATA_RESPONSE_SCHEMA, ALL_SUMMARIES_RESPONSE_SCHEMA, CONVERSATIONS_RESPONSE_SCHEMA, TREND_RESPONSE_SCHEMA,
    ORGANIZATION_TREND_RESPONSE_SCHEMA, TREND_PERIOD_PARAMETER_SCHEMA, OVERVIEW_RESPONSE_SCHEMA,
    ORGANIZATION_OVERVIEW_RESPONSE_SCHEMA, PER_TOPIC_PARAMETER_SCHEMA, SEARCH_QUERY_PARAMETER_SCHEMA,
    REGENERATE_API_KEY_RESPONSE_SCHEMA, SEARCH_RESPONSE_SCHEMA, TRANSCRIPT_RESPONSE_SCHEMA,
    LIST_ACTIVE_TOPICS_RESPONSE_SCHEMA, MANAGED_AGENTS_RESPONSE_SCHEMA, ERROR_RESPONSE_SCHEMA,
    NOT_FOUND_RESPONSE_SCHEMA, FORBIDDEN_RESPONSE_SCHEMA, TOPIC_DATA_RESPONSE_SCHEMA,
    CONVERSATION_ORDERING_PARAMETER_SCHEMA, CUSTOMER_ORDERING_PARAMETER_SCHEMA, get_search_parameters_schema
)


class SummaryActionsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet to outline the actions of the MetaSummarySerializer.
    Attributes:
        summary_period (str): Time period by which to apply summarization when calling all_summaries
        summary_order_keys (list[str]): List of keys inside the dictionary summary by which to order resulting summaries
        summary_order_desc (bool): Indicates whether order the summary dictionaries in descending order of the order key
        summary_rolling_window (bool): Indicates whether to use a rolling window when selecting conversations
    """
    summary_period = DEFAULT_SUMMARY_SETTINGS['agent']['period']
    summary_order_keys = ['summary_call_count']
    summary_order_desc = True
    summary_rolling_window = DEFAULT_SUMMARY_SETTINGS['agent']['rolling']

    @staticmethod
    def get_summary_name(obj):
        """
        Returns the label that will be placed next to every summary.
        Default: try obj.name, otherwise None.
        """
        return getattr(obj, "name", None)

    @extend_schema(
        description=MetaSummarySerializer.get_summary_data.__doc__,
        parameters=[ID_PARAMETER_SCHEMA, SUMMARY_PERIOD_PARAMETER_SCHEMA, SUMMARY_ROLLING_PARAMETER_SCHEMA],
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
        context = self.get_serializer_context()

        # Inject trace data and period to the default serializer context
        period = self.request.query_params.get("period", self.summary_period)
        rolling = self.request.query_params.get("rolling", self.summary_rolling_window)
        context['period'] = period
        context['rolling'] = rolling
        serializer = self.get_serializer(obj, context=context)
        try:
            return response.Response(serializer.get_summary_data(obj))
        except ValueError as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
        This method takes get_summary_data a step further, obtaining the summary data of all objects in the queryset.
        The response is now a dictionary, where the key corresponds to the object ID.
        The default summarization period is 'month'. For Customers, the summarization period is 'quarter'.
        """
        queryset = self.get_queryset()
        try:
            summaries = {}
            ordering = {}
            context = self.get_serializer_context()
            context['period'] = self.summary_period
            context['rolling'] = self.summary_rolling_window
            for obj in queryset:
                serializer = self.get_serializer(obj, context=context)
                summary_data = serializer.get_summary_data(obj)
                summary_data['name'] = self.get_summary_name(obj)
                summaries[obj.id] = summary_data

                # Extract the order of this summary item
                order_value = summary_data.copy()
                for key in self.summary_order_keys:
                    order_value = order_value.get(key)
                ordering[obj.id] = order_value

            # Sort the resulting summary data by the ordering
            # NOTE: Ordering does not work because the dict response is re-sorted when JSONified.
            # Would have to return a list for this ordering to stick
            sorted_summaries = dict(sorted(
                    summaries.items(),
                    key=lambda item: ordering[item[0]],
                    reverse=self.summary_order_desc
                )
            )
            return response.Response(sorted_summaries)
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

    @extend_schema(
        description=ConversationTrendsSerializer.get_overview.__doc__,
        parameters=[ID_PARAMETER_SCHEMA, PER_TOPIC_PARAMETER_SCHEMA],
        responses={
            200: OVERVIEW_RESPONSE_SCHEMA,
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=True, methods=['get'])
    def overview(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj)
        try:
            return response.Response(serializer.get_overview(obj))
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
            .distinct()
        )

        # Apply ordering: use OrderingFilter if explicitly specified, otherwise fallback to search relevance
        ordering_param = getattr(self, 'ordering_param', 'ordering')
        if request.query_params.get(ordering_param):
            # User explicitly provided ordering parameter
            ordering = filters.OrderingFilter().get_ordering(request, queryset, self)
            queryset = queryset.order_by(*ordering)
        else:
            # No ordering parameter provided, use search relevance
            queryset = queryset.order_by('-rank')

        # Return the results. If empty, raise a 404. Otherwise paginate if necessary.
        if not queryset.exists():
            return response.Response(
                {'detail': 'Your query produced no results.'},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            # For search without ordering, temporarily modify cursor_ordering to prioritize rank
            original_cursor_ordering = getattr(self, 'cursor_ordering', None)
            if not request.query_params.get(ordering_param):
                # Prepend -rank to cursor_ordering for the paginator
                if original_cursor_ordering:
                    self.cursor_ordering = ['-rank'] + list(original_cursor_ordering)
                else:
                    self.cursor_ordering = ['-rank']

            try:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True, context={'request': request})
                    return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(queryset, many=True, context={'request': request})
                return response.Response(serializer.data)
            finally:
                # Restore original cursor_ordering
                if original_cursor_ordering is not None:
                    self.cursor_ordering = original_cursor_ordering
                elif hasattr(self, 'cursor_ordering'):
                    delattr(self, 'cursor_ordering')


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
    cursor_ordering = ['-date', 'sentiment', 'resolved']
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date', 'sentiment', 'resolved']
    ordering = ['-date', 'sentiment', 'resolved']  # Match cursor_ordering for consistency
    relationships_to_select = ['customer', 'agent', 'agent__user']
    relationships_to_prefetch = ['topics']
    search_vector = (
        SearchVector('transcript', weight='A') +
        SearchVector('summary', weight='A') +
        SearchVector(F('topics__name'), weight='B')
    )

    @extend_schema(
        description='Search conversations by transcript content, summary text, and topic names.',
        parameters=get_search_parameters_schema(CONVERSATION_ORDERING_PARAMETER_SCHEMA),
        responses={
            200: SEARCH_RESPONSE_SCHEMA,
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        return super().search(request)

    def get_serializer_class(self):
        if self.action in ['list', 'search']:
            return ConversationListSerializer
        elif self.action in ['retrieve', 'transcript']:
            return ConversationDetailSerializer
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return ConversationModifySerializer
        raise MethodNotAllowed(self.action)

    def get_queryset(self):
        """
        Return conversations that belong to the user's organization
        """
        if self.request.user.is_superuser:
            qs = Conversation.objects.all()
        elif self.request.user.employee.organization:
            qs = Conversation.objects.filter(agent__organization=self.request.user.employee.organization)
        else:
            return Conversation.objects.none()

        qs = (
            qs
            .select_related(*self.relationships_to_select)
            .prefetch_related(*self.relationships_to_prefetch)
        )
        return qs

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

    @extend_schema(
        description="List conversations with optional ordering",
        parameters=[CONVERSATION_ORDERING_PARAMETER_SCHEMA],
        responses={
            200: "Paginated list of conversations",
            403: FORBIDDEN_RESPONSE_SCHEMA
        }
    )
    def list(self, request, *args, **kwargs):
        """List conversations with optional ordering by date, sentiment, or resolved status."""
        return super().list(request, *args, **kwargs)

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
            return OrganizationSerializer
        elif self.action in ['conversations', 'trend', 'overview']:
            return ConversationTrendsSerializer
        raise MethodNotAllowed(self.action)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Organization.objects.all()
        if self.request.user.employee.organization:
            return Organization.objects.filter(pk=self.request.user.employee.organization.pk)
        return Organization.objects.none()

    @extend_schema(
        description=ConversationTrendsSerializer.get_trend.__doc__,
        parameters=[TREND_PERIOD_PARAMETER_SCHEMA, PER_TOPIC_PARAMETER_SCHEMA],
        responses={
            200: ORGANIZATION_TREND_RESPONSE_SCHEMA,
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=False, methods=['get'])
    def trend(self, request):
        queryset = self.get_queryset()
        try:
            trends = {}
            for obj in queryset:
                serializer = self.get_serializer(obj)
                trends[obj.id] = serializer.get_trend(obj)
            return response.Response(trends)
        except ValueError as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description=ConversationTrendsSerializer.get_trend.__doc__,
        parameters=[PER_TOPIC_PARAMETER_SCHEMA],
        responses={
            200: ORGANIZATION_OVERVIEW_RESPONSE_SCHEMA,
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=False, methods=['get'])
    def overview(self, request):
        queryset = self.get_queryset()
        try:
            trends = {}
            for obj in queryset:
                serializer = self.get_serializer(obj)
                trends[obj.id] = serializer.get_overview(obj)
            return response.Response(trends)
        except ValueError as e:
            return response.Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrganizationAPIKeyViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
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
        raise MethodNotAllowed(self.action)

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
    summary_period = DEFAULT_SUMMARY_SETTINGS['topic']['period']
    summary_order_keys = ['summary_call_count']
    summary_order_desc = True
    summary_rolling_window = DEFAULT_SUMMARY_SETTINGS['topic']['rolling']

    def get_serializer_class(self):
        if self.action in ['list', 'list_active', 'retrieve', 'list_recent']:
            return TopicListSerializer
        elif self.action in ['summary_data', 'all_summaries']:
            return MetaSummarySerializer
        elif self.action in ['conversations', 'trend']:
            return ConversationTrendsSerializer
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return TopicModifySerializer
        raise MethodNotAllowed(self.action)

    def get_queryset(self):
        """
        Return topics that belong to the user's organization
        """
        if self.request.user.is_superuser:
            qs = Topic.objects.all()
        elif self.request.user.employee.organization:
            qs = Topic.objects.filter(organization=self.request.user.employee.organization)
        else:
            qs = Topic.objects.none()

        # Optimize DB Querying for all_summaries and summary_data
        if self.action in ['all_summaries', 'summary_data', 'list_recent']:
            qs = qs.prefetch_related('conversations')

        # If the action is 'all_summaries' fetch only those topics that would contribute to the period's summary
        if self.action == 'all_summaries':
            start, end, label = period_bounds(self.summary_period, self.summary_rolling_window)
            qs = qs.filter(last_conversation_date__gte=start)

        # If the action is 'list_active', also do the is_active filter:
        if self.action == 'list_active':
            qs = qs.filter(is_active=True)

        return qs

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
        description="List topics of an organization mentioned in the past year",
        responses=LIST_ACTIVE_TOPICS_RESPONSE_SCHEMA
    )
    @decorators.action(detail=False, methods=['get'], url_path='list_recent')
    def list_recent(self, request):
        """
        Custom action to list only topics mentioned in the past year
        """
        qs = self.get_queryset()
        one_year_ago = datetime.now(tz=zoneinfo.ZoneInfo("UTC")) - timedelta(days=365)
        recent_qs = qs.filter(last_conversation_date__gte=one_year_ago)  # Excludes topics with no conversations

        # Paginate and return
        page = self.paginate_queryset(recent_qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recent_qs, many=True)
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def overview(self, request, pk=None):
        # Override the inherited /overview action
        raise MethodNotAllowed("GET")


class SuggestedTopicViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    A ViewSet for the SuggestedTopic model.
    A summary of the permissions:
    - Accepting a suggested topic is allowed to superusers and analysts of the same organization
    - Viewing is allowed to employees of the same organization (and superusers)
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [TopicPermission]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['-conversation_count', 'created']

    def get_serializer_class(self):
        if self.action == "accept":
            return SuggestedTopicAcceptSerializer
        elif self.action == "list":
            return SuggestedTopicListSerializer
        else:
            raise MethodNotAllowed(self.action)

    def get_queryset(self):
        """
        Return suggested topics that belong to the user's organization
        """
        if self.request.user.is_superuser:
            qs = SuggestedTopic.objects.all()
        elif self.request.user.employee.organization:
            qs = SuggestedTopic.objects.filter(organization=self.request.user.employee.organization)
        else:
            qs = SuggestedTopic.objects.none()
        return qs

    @extend_schema(
        description='Accepts an AI-suggested topic converting it into an actual topic.',
        responses={
            200: TOPIC_DATA_RESPONSE_SCHEMA,
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a suggested topic and convert it to a real topic."""
        suggested_topic = self.get_object()

        serializer = self.get_serializer(instance=suggested_topic)
        topic_data = serializer.accept()
        return response.Response(topic_data, status=status.HTTP_200_OK)


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
        elif self.action in ['summary_data', 'all_summaries']:
            return MetaSummarySerializer
        elif self.action in ['conversations', 'trend', 'overview']:
            return ConversationTrendsSerializer
        raise MethodNotAllowed(self.action)

    def get_queryset(self):
        qs = Agent.objects.select_related('user', 'manager', 'manager__user')

        if self.request.user.is_superuser:
            return qs
        if self.request.user.employee.organization:
            return qs.filter(organization=self.request.user.employee.organization)
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

    def get_summary_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class CustomerViewSet(viewsets.ModelViewSet, SearchViewSet, TrendsActionsViewSet, SummaryActionsViewSet):
    """
    A ViewSet for the Customer model. This ViewSet inherits from:
    - SearchViewSet: to allow users to search customers by name, latest conversation title, and conversation transcripts
    - TrendsActionsViewSet: to obtain conversation trends of a single Customer
    - SummaryActionsViewSet: to obtain meta-summaries of a customer's conversation summaries

    The ViewSet permissions can be summarized as follows:
    - Modification is only allowed to superusers
    - Viewing is allowed to any employee of the same organization (and superusers)
    """
    MINIMUM_CALL_COUNT = 2  # Minimum number of calls for a customer to be included in all_summaries result
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [CustomerPermission]
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['-last_conversation_date', 'conversation_count']
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['last_conversation_date', 'conversation_count', 'created', 'total_revenue', 'avg_sentiment']
    ordering = ['-last_conversation_date', 'conversation_count']  # Match cursor_ordering for consistency
    relationships_to_select = ['latest_conversation']
    relationships_to_prefetch = []
    search_vector = (
        SearchVector('first_name', weight='A') +
        SearchVector('last_name', weight='A') +
        SearchVector('latest_conversation__title', weight='B') +
        SearchVector(F('conversations__transcript'), weight='C')
    )
    summary_period = DEFAULT_SUMMARY_SETTINGS['customer']['period']
    summary_order_keys = ['summary', 'Customer Value']
    summary_order_desc = True
    summary_rolling_window = DEFAULT_SUMMARY_SETTINGS['customer']['rolling']

    @extend_schema(
        description='Search customers by name, latest conversation title, and conversation transcript content.',
        parameters=get_search_parameters_schema(CUSTOMER_ORDERING_PARAMETER_SCHEMA),
        responses={
            200: SEARCH_RESPONSE_SCHEMA,
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        return super().search(request)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'search']:
            return CustomerListSerializer
        elif self.action in ['summary_data', 'all_summaries']:
            return MetaSummarySerializer
        elif self.action in ['conversations', 'trend']:
            return ConversationTrendsSerializer
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            return CustomerModifySerializer
        raise MethodNotAllowed(self.action)

    def get_queryset(self):
        """
        Return customers that belong to the user's organization, with aggregated fields for ordering
        """
        if self.request.user.is_superuser:
            qs = Customer.objects.all()
        elif self.request.user.employee.organization:
            qs = Customer.objects.filter(organization=self.request.user.employee.organization)
        else:
            qs = Customer.objects.none()

        # Add aggregated fields for ordering
        qs = qs.annotate(
            total_revenue=Sum('conversations__revenue_at_stake'),
            avg_sentiment=Avg('conversations__sentiment')
        )

        # Optimize DB Querying for all_summaries and summary_data
        if self.action in ['all_summaries', 'summary_data']:
            qs = qs.prefetch_related('conversations')

        # Load only customers that have a minimum conversation count and would have a summary for the period
        if self.action == 'all_summaries':
            start, end, label = period_bounds(self.summary_period, self.summary_rolling_window)
            qs = qs.filter(conversation_count__gte=self.MINIMUM_CALL_COUNT).filter(last_conversation_date__gte=start)
        return qs

    @extend_schema(
        description="List customers with optional ordering",
        parameters=[CUSTOMER_ORDERING_PARAMETER_SCHEMA],
        responses={
            200: "Paginated list of customers with aggregated fields (total_revenue, avg_sentiment)",
            403: FORBIDDEN_RESPONSE_SCHEMA
        }
    )
    def list(self, request, *args, **kwargs):
        """List customers with optional ordering by conversation metrics or aggregated fields."""
        return super().list(request, *args, **kwargs)

    def get_summary_name(self, obj):
        return obj.external_id


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
    pagination_class = CustomListViewPaginator
    cursor_ordering = ['-role', 'user__last_name', 'id']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'me']:
            return EmployeeListSerializer
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'invite']:
            return EmployeeModifySerializer
        raise MethodNotAllowed(self.action)

    def get_queryset(self):
        """
        Return employees that belong to the user's organization
        """
        if self.request.user.is_superuser:
            return (
                Employee
                .objects
                .all()
                .select_related('user')
            )
        if self.request.user.employee.organization:
            return (
                Employee
                .objects
                .filter(organization=self.request.user.employee.organization)
                .select_related('user')
            )
        return Employee.objects.none()

    @extend_schema(
        description="Return current employee details",
        responses={
            200: EmployeeListSerializer,
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=False, methods=['get'])
    def me(self, request):
        """
        Custom endpoint to return the current user's employee data.
        """
        employee = getattr(request.user, 'employee', None)
        if not employee:
            return response.Response({'detail': 'Employee not found.'}, status=404)

        serializer = self.get_serializer(employee)
        return response.Response(serializer.data)

    @extend_schema(
        description="Send invitation email to an employee",
        responses={
            200: {'detail': 'Invitation email was sent.'},
            400: ERROR_RESPONSE_SCHEMA,
            403: FORBIDDEN_RESPONSE_SCHEMA,
            404: NOT_FOUND_RESPONSE_SCHEMA
        }
    )
    @decorators.action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """
        Custom endpoint to re-send an invitation email to the employee. Only meant for organization admins.
        """
        employee = self.get_object()
        if not employee:
            return response.Response({'detail': 'Employee not found.'}, status=404)

        employee.user.send_onboarding_email()
        return response.Response({'detail': 'Invitation email was sent.'}, status=200)
