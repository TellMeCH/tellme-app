from rest_framework.pagination import CursorPagination
from rest_framework.settings import api_settings


class CustomFieldCursorPaginator(CursorPagination):
    """
    Custom cursor paginator that allows per-field pagination
    """
    ordering = ['-date', 'id']  # Default ordering by descending date
    page_size = api_settings.PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = 100  # Set a maximum limit to prevent excessively large requests

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
    max_page_size = 100  # Set a maximum limit to prevent excessively large requests

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