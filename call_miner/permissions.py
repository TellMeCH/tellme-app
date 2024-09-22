from rest_framework import permissions


class IsOrganizationMember(permissions.BasePermission):
    """
    Custom permission to allow access to objects only for users within their own organization.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        core_check = (request.user and request.user.is_authenticated)

        if hasattr(obj, 'agent'):  # If the object is a Conversation, check the organization of its agent
            necessary_org = obj.agent.organization
        elif hasattr(obj, 'organization'):  # Otherwise get the object's organization
            necessary_org = obj.organization
        else:
            raise ValueError('IsOrganizationMember was applied to an incorrect Viewset')

        # For other objects, check if the object's organization matches the user's organization
        return core_check and necessary_org == request.user.employee.organization


class IsAnalyst(permissions.BasePermission):
    """
    Custom permission to allow access to objects only for Analysts.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Only allow access if the user is an analyst
        return hasattr(request.user.employee, 'analyst')


class IsManager(permissions.BasePermission):
    """
    Custom permission to allow access to objects only for managers.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Check if the user is an agent (and therefore can be a manager)
        if hasattr(request.user.employee, 'agent'):
            # Retrieve the agents managed by the current user
            managed_agents = request.user.employee.agent.agents.all()
            # Allow access if the object is one of the agents managed by the user
            return (obj in managed_agents) or (obj == request.user.employee.agent)
        # Return False if the user is not an agent or does not manage any agents
        return False
