from rest_framework.settings import api_settings
import base64
from rest_framework.pagination import CursorPagination
from rest_framework.response import Response
from rest_framework.exceptions import NotFound


class ListCursorPagination(CursorPagination):
    """
    This is a custom pagination class that is used for paginating throughout lists of dictionaries instead of QuerySets
    """
    ordering = 'id'
    page_size = api_settings.PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return min(int(request.query_params[self.page_size_query_param]), self.max_page_size)
            except (KeyError, ValueError):
                pass
        return self.page_size

    def paginate_queryset(self, list_data, request, view=None):
        # Order the list by the specified field
        reverse = self.ordering.startswith('-')
        ordering_key = self.ordering.lstrip('-')

        # Sort the data based on the ordering field
        sorted_list = sorted(list_data, key=lambda x: x.get(ordering_key), reverse=reverse)

        # Decode the cursor from the request (if it exists)
        cursor = request.query_params.get(self.cursor_query_param)
        index = self._decode_cursor(cursor) if cursor else 0

        # Slice the list based on the cursor and page size
        paginated_list = sorted_list[index:index + self.page_size]

        self.has_next = index + self.page_size < len(sorted_list)
        self.has_previous = index > 0

        # Save the cursor for next and previous pages
        self.next_cursor = self._encode_cursor(index + self.page_size) if self.has_next else None
        self.previous_cursor = self._encode_cursor(index - self.page_size) if self.has_previous else None

        # Store the request for building absolute URLs
        self.request = request

        return paginated_list

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

    def get_next_link(self):
        if self.next_cursor:
            return self.encode_cursor_link(self.next_cursor)
        return None

    def get_previous_link(self):
        if self.previous_cursor:
            return self.encode_cursor_link(self.previous_cursor)
        return None

    def encode_cursor_link(self, cursor):
        base_url = self.request.build_absolute_uri(self.request.path)
        return f'{base_url}?{self.cursor_query_param}={cursor}'

    def _encode_cursor(self, index):
        return base64.urlsafe_b64encode(str(index).encode()).decode()

    def _decode_cursor(self, cursor):
        if cursor is None:
            return 0
        try:
            return int(base64.urlsafe_b64decode(cursor.encode()).decode())
        except (TypeError, ValueError):
            raise NotFound("Invalid cursor.")


class CustomFieldCursorPaginator(CursorPagination):
    """
    Custom cursor paginator that allows per-field pagination
    """
    ordering = ['-date', 'id']
    page_size = api_settings.PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return min(int(request.query_params[self.page_size_query_param]), self.max_page_size)
            except (KeyError, ValueError):
                pass
        return self.page_size


class CustomListViewPaginator(CursorPagination):
    page_size = api_settings.PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return min(int(request.query_params[self.page_size_query_param]), self.max_page_size)
            except (KeyError, ValueError):
                pass
        return self.page_size

    def get_ordering(self, request, queryset, view):
        if hasattr(view, 'cursor_ordering'):
            return view.cursor_ordering
        return super().get_ordering(request, queryset, view)