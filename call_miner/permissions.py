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


class TopicPermission(permissions.BasePermission):
    """
    Permissions class for the TopicViewSet.
    """
    def has_permission(self, request, view):
        """
        Modification is only allowed to analysts and superusers, listing is possible for Employees
        """
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if hasattr(request.user.employee, 'analyst'):
            if request.method == 'POST':
                organization_id = request.data.get('organization')
                return organization_id and str(request.user.employee.organization.id) == str(organization_id)
            return True
        if hasattr(request.user, 'employee'):
            return request.method not in ['POST', 'PATCH', 'PUT', 'DELETE']
        return False

    def has_object_permission(self, request, view, obj):
        """
        For retrieve, check that the user belongs to the Topic's Organization, or whether it's a superuser
        Note that this expects obj to be an instance of Topic
        """
        if hasattr(request.user, 'employee'):
            return request.user.employee.organization == obj.organization and hasattr(request.user.employee, 'analyst')
        return request.user.is_superuser


class AgentPermission(permissions.BasePermission):
    """
    Permissions class for the AgentViewSet.
    """
    def has_permission(self, request, view):
        """
        Only superusers can modify an agent (although the AgentViewSet is not meant for it), and organization employees
        can list.
        """
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'employee'):
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
        if request.method not in ['POST', 'PATCH', 'PUT', 'DELETE'] and view.action != 'list':
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
