from rest_framework import permissions


class ConversationPermission(permissions.BasePermission):
    """
    Permissions class for the ConversationViewSet.
    """
    def has_permission(self, request, view):
        """
        Modification is only allowed to superusers, listing is possible for Employees and superusers
        """
        if request.method in ['POST', 'PATCH', 'PUT', 'DELETE']:
            return request.user.is_superuser
        return hasattr(request.user, 'employee') or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        """
        For retrieve, check that the user has the same organization as the Conversation.
        Note that this expects obj to be an instance of Conversation
        """
        if hasattr(request.user, 'employee'):
            return obj.agent.organization == request.user.employee.organization
        return request.user.is_superuser


class OrganizationPermission(permissions.BasePermission):
    """
    Permissions class for the OrganizationViewSet.
    """
    def has_permission(self, request, view):
        """
        Modification is only allowed to superusers, listing is possible for Employees
        """
        if request.method in ['POST', 'PATCH', 'PUT', 'DELETE']:
            return request.user.is_superuser
        return hasattr(request.user.employee, 'analyst')

    def has_object_permission(self, request, view, obj):
        """
        For retrieve, check that the user belongs to the Organization.
        For modification, check that the user is a superuser
        Note that this expects obj to be an instance of Organization
        """
        if hasattr(request.user, 'employee'):
            return request.user.employee.organization == obj
        return request.user.is_superuser


class TopicPermission(permissions.BasePermission):
    """
    Permissions class for the TopicViewSet.
    """
    def has_permission(self, request, view):
        """
        Modification is only allowed to analysts, listing is possible for Employees
        """
        if request.method in ['POST', 'PATCH', 'PUT', 'DELETE']:
            return hasattr(request.user.employee, 'analyst')
        return hasattr(request.user, 'employee')

    def has_object_permission(self, request, view, obj):
        """
        For retrieve, check that the user belongs to the Topic's Organization.
        Note that this expects obj to be an instance of Topic
        """
        return request.user.employee.organization == obj.organization and hasattr(request.user.employee, 'analyst')


class AgentPermission(permissions.BasePermission):
    """
    Permissions class for the AgentViewSet.
    """
    def has_permission(self, request, view):
        """
        Only organization admins or superusers can modify an agent, and organization employees can list.
        """
        if request.method in ['POST', 'PATCH', 'PUT', 'DELETE']:
            return request.user.employee.is_organization_admin or request.user.is_superuser
        return hasattr(request.user, 'employee')

    def has_object_permission(self, request, view, obj):
        """
        For retrieve, check that the user is either the agent or the agent's manager.
        For modification, check that the user is an organization admin
        Note that this expects obj to be an instance of Agent
        """
        if hasattr(request.user.employee, 'agent'):
            managed_agents = request.user.employee.agent.agents.all()
            return (obj in managed_agents) or (obj == request.user.employee.agent)
        return request.user.employee.is_organization_admin or request.user.is_superuser


class CustomerPermission(permissions.BasePermission):
    """
    Permissions class for the CustomerViewSet.
    """
    def has_permission(self, request, view):
        """
        Only superusers can modify a customer, and organization employees can list them all.
        """
        if request.method in ['POST', 'PATCH', 'PUT', 'DELETE']:
            return request.user.is_superuser
        return hasattr(request.user, 'employee')

    def has_object_permission(self, request, view, obj):
        """
        For retrieve, check that the user belongs to the same organization as the customer.
        For modification, check that the user is a superuser
        Note that this expects obj to be an instance of Customer
        """
        if hasattr(request.user, 'employee'):
            return request.user.employee.organization == obj.organization
        return request.user.is_superuser


class EmployeePermission(permissions.BasePermission):
    """
    Permissions class for the EmployeeViewSet.
    """
    def has_permission(self, request, view):
        """
        Only organization admins can create a new employee or list all existing employees.
        """
        if (request.method == 'GET' and view.action == 'list') or request.method == 'POST':
            return request.user.employee.is_organization_admin or request.user.is_superuser
        return True

    def has_object_permission(self, request, view, obj):
        """
        The retrieve action for an Employee is possible for organization admins and the employee itself
        All other actions are only possible for organization admins or superusers
        """
        if view.action == 'retrieve':
            return request.user.employee.is_organization_admin or request.user.employee == obj
        return request.user.employee.is_organization_admin or request.user.is_superuser

