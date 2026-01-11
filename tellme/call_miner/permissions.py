from rest_framework import permissions


class ConversationPermission(permissions.BasePermission):
    """
    Permissions class for the ConversationViewSet.
    """
    def has_permission(self, request, view):
        """
        Modification is only allowed to superusers, listing is possible for Employees and superusers
        """
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if request.method not in ['POST', 'PATCH', 'PUT', 'DELETE']:
            return hasattr(request.user, 'employee')
        return False

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
        Modification is only allowed to superusers, listing is possible for Analysts
        """
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if hasattr(request.user.employee, 'analyst'):
            return request.method not in ['POST', 'PATCH', 'PUT', 'DELETE'] and view.action != 'list'
        return False

    def has_object_permission(self, request, view, obj):
        """
        For retrieve, check that the user belongs to the Organization.
        For modification, check that the user is a superuser
        Note that this expects obj to be an instance of Organization
        """
        if hasattr(request.user, 'employee'):
            return request.user.employee.organization == obj
        return request.user.is_superuser


class OrganizationAPIKeyPermission(permissions.BasePermission):
    """
    Permissions class for the OrganizationAPIKeyViewSet.
    """
    def has_permission(self, request, view):
        """
        Superusers can do anything. Organization admins can create a new key or list all existing keys.
        """
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.employee.is_organization_admin:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """
        Object-specific actions are only possible for organization admins or superusers
        """
        if request.user.is_superuser:
            return True
        if request.user.employee.is_organization_admin:
            return request.user.employee.organization == obj.organization
        return False


class TopicPermission(permissions.BasePermission):
    """
    Permissions class for the TopicViewSet.
    """
    def has_permission(self, request, view):
        """
        Modification is only allowed to analysts and superusers, listing is possible for Employees.
        POST is also allowed for the 'summary_data' action.
        """
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser or hasattr(request.user.employee, 'analyst'):
            return True

        # Allow POST for summary_data action (non-modifying action)
        if request.method == 'POST' and view.action == 'summary_data':
            return hasattr(request.user, 'employee')

        if request.method not in ['POST', 'PATCH', 'PUT', 'DELETE']:
            return hasattr(request.user, 'employee')
        return False

    def has_object_permission(self, request, view, obj):
        """
        For retrieve, check that the user belongs to the Topic's Organization, or whether it's a superuser
        Note that this expects obj to be an instance of Topic
        """
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'employee'):
            return request.user.employee.organization == obj.organization
        return False


class AgentPermission(permissions.BasePermission):
    """
    Permissions class for the AgentViewSet.
    """
    def has_permission(self, request, view):
        """
        Only superusers can modify an agent (although the AgentViewSet is not meant for it), and organization employees
        can list.
        POST is also allowed for the 'summary_data' action.
        """
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        if hasattr(request.user, 'employee'):
            # Allow POST for summary_data action (non-modifying action)
            if request.method == 'POST' and view.action == 'summary_data':
                return True

            return request.method not in ['POST', 'PATCH', 'PUT', 'DELETE']
        return False

    def has_object_permission(self, request, view, obj):
        """
        For retrieve, check that the user is either the agent or the agent's manager.
        For modification, check that the user is an organization admin
        Note that this expects obj to be an instance of Agent
        """
        if request.user.is_superuser:
            return True
        if request.user.employee.is_organization_admin:
            return request.user.employee.organization.id == obj.organization_id
        if hasattr(request.user.employee, 'agent'):
            managed_agents = request.user.employee.agent.agents.all()
            return (obj in managed_agents) or (obj == request.user.employee.agent)
        return False


class CustomerPermission(permissions.BasePermission):
    """
    Permissions class for the CustomerViewSet.
    """
    def has_permission(self, request, view):
        """
        Only superusers can modify a customer, and organization employees can list them all.
        POST is also allowed for the 'ticket' and 'summary_data' actions.
        """
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        # Allow POST for ticket and summary_data actions (non-modifying actions)
        if request.method == 'POST' and view.action in ['ticket', 'summary_data']:
            return hasattr(request.user, 'employee')

        if request.method not in ['POST', 'PATCH', 'PUT', 'DELETE']:
            return hasattr(request.user, 'employee')
        return False

    def has_object_permission(self, request, view, obj):
        """
        For retrieve, check that the user belongs to the same organization as the customer.
        For modification, check that the user is a superuser
        Note that this expects obj to be an instance of Customer
        """
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'employee'):
            return request.user.employee.organization == obj.organization
        return False


class EmployeePermission(permissions.BasePermission):
    """
    Permissions class for the EmployeeViewSet.
    """
    def has_permission(self, request, view):
        """
        Superusers can do anything. Organization admins can create a new employee or list all existing employees.
        """
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.employee.is_organization_admin:
            return True
        if request.method not in ['POST', 'PATCH', 'PUT', 'DELETE'] and view.action not in ['list', 'invite']:
            return hasattr(request.user, 'employee')
        return False

    def has_object_permission(self, request, view, obj):
        """
        The retrieve action for an Employee is possible for superusers, organization admins and the employee itself
        All other actions are only possible for organization admins or superusers
        """
        if request.user.is_superuser:
            return True
        if request.user.employee.is_organization_admin:
            return request.user.employee.organization == obj.organization
        if request.user.employee.id == obj.id:
            return True
        return False
