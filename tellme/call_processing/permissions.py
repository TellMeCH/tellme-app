from rest_framework.permissions import BasePermission
from tellme.call_miner.models import Organization


class IsAuthenticatedOrganization(BasePermission):
    """
    Allows access only to authenticated organizations or valid API key holders.
    """

    def has_permission(self, request, view):
        return isinstance(request.user, Organization)
