import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from call_miner.models import Employee, Agent, Analyst, Organization

ERROR_MESSAGES = {
    'org_admins_organization': "Org Admins should not provide an organization when modifying an Employee.",
    'manager_same_organization': 'Manager must belong to the same organization as the current user.',
    'analysts_managers': "Analysts can't have managers.",
    'superusers_organization': "Superusers must provide an organization when creating an Employee."
}


@pytest.fixture
def client():
    """Create an APIClient instance for testing."""
    return APIClient()


@pytest.fixture
def organization():
    """Create and return a test organization."""
    return Organization.objects.create(name='Test Organization')


@pytest.fixture
def another_organization():
    """Create and return another test organization."""
    return Organization.objects.create(name='Another Organization')


@pytest.fixture
def superuser(db, organization):
    """Create and return a superuser."""
    user = User.objects.create_superuser('superuser', 'super@example.com', 'password')
    return user


@pytest.fixture
def organization_admin(organization):
    """Create and return an organization admin user."""
    user = User.objects.create_user('orgadmin', 'orgadmin@example.com', 'password')
    Employee.objects.create(user=user, organization=organization, is_organization_admin=True)
    return user


@pytest.fixture
def analyst(organization):
    """Create and return an analyst user."""
    user = User.objects.create_user('analyst', 'analyst@example.com', 'password')
    Analyst.objects.create(user=user, organization=organization, is_organization_admin=False)
    return user


@pytest.fixture
def agent(organization):
    """Create and return an agent user."""
    user = User.objects.create_user('agent', 'agent@example.com', 'password')
    Agent.objects.create(user=user, organization=organization, is_organization_admin=False)
    return user


@pytest.fixture
def agent_manager(organization):
    """Create and return an agent manager and an agent managed by them."""
    manager_user = User.objects.create_user('manager', 'manager@example.com', 'password')
    manager = Agent.objects.create(user=manager_user, organization=organization, is_organization_admin=False)
    agent_user = User.objects.create_user('agent2', 'agent2@example.com', 'password')
    Agent.objects.create(user=agent_user, organization=organization, is_organization_admin=False, manager=manager)
    return manager_user


@pytest.fixture
def another_organization_admin(another_organization):
    """Create and return an organization admin in another organization."""
    user = User.objects.create_user('another_orgadmin', 'another_orgadmin@example.com', 'password')
    Employee.objects.create(user=user, organization=another_organization, is_organization_admin=True)
    return user


@pytest.fixture
def another_organization_agent(another_organization):
    """Create and return an agent in another organization."""
    user = User.objects.create_user('another_org_employee', 'another_org_employee@example.com', 'password')
    Employee.objects.create(user=user, organization=another_organization, is_organization_admin=False, role='AGENT')
    return user


@pytest.mark.django_db
class TestEmployeeList:
    """Tests for the Employee list API endpoint."""

    def test_superuser_can_list_all_employees(self, client, superuser, organization_admin, analyst, agent_manager,
                                              agent, another_organization_agent):
        """Test that a superuser can list all employees across organizations."""
        client.force_authenticate(user=superuser)
        url = reverse('employee-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 6

    def test_organization_admin_can_list_own_organization_employees(self, client, superuser, organization_admin,
                                                                    analyst, agent_manager, agent,
                                                                    another_organization_agent):
        """Test that an organization admin can list employees in their own organization."""
        client.force_authenticate(user=organization_admin)
        url = reverse('employee-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5

    def test_analyst_cannot_list_employees(self, client, analyst):
        """Test that an analyst cannot list employees."""
        client.force_authenticate(user=analyst)
        url = reverse('employee-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_list_employees(self, client, agent):
        """Test that an agent cannot list employees."""
        client.force_authenticate(user=agent)
        url = reverse('employee-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_list_employees(self, client):
        """Test that an unauthenticated user cannot list employees."""
        url = reverse('employee-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestEmployeeRetrieve:
    """Tests for retrieving individual employees via the API."""

    def test_superuser_can_retrieve_any_employee(self, client, superuser, analyst, another_organization_agent):
        """Test that a superuser can retrieve any employee from any organization."""
        client.force_authenticate(user=superuser)
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['username'] == analyst.username

        another_employee = Employee.objects.get(user=another_organization_agent)
        url = reverse('employee-detail', args=[another_employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['username'] == another_organization_agent.username

    def test_organization_admin_can_retrieve_employee_in_organization(self, client, organization_admin, analyst):
        """Test that an organization admin can retrieve an employee in their organization."""
        client.force_authenticate(user=organization_admin)
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['username'] == analyst.username

    def test_organization_admin_cannot_retrieve_employee_in_another_organization(self, client, organization_admin,
                                                                                 another_organization_agent):
        """Test that an organization admin cannot retrieve an employee from another organization."""
        client.force_authenticate(user=organization_admin)
        another_employee = Employee.objects.get(user=another_organization_agent)
        url = reverse('employee-detail', args=[another_employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_analyst_can_retrieve_self(self, client, analyst):
        """Test that an analyst can retrieve their own employee record."""
        client.force_authenticate(user=analyst)
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['username'] == analyst.username

    def test_analyst_cannot_retrieve_other_employee(self, client, analyst, agent):
        """Test that an analyst cannot retrieve another employee's record."""
        client.force_authenticate(user=analyst)
        employee = Employee.objects.get(user=agent)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_manager_can_retrieve_self(self, client, agent_manager):
        """Test that an agent manager can retrieve their own employee record."""
        client.force_authenticate(user=agent_manager)
        employee = Employee.objects.get(user=agent_manager)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['username'] == agent_manager.username

    def test_agent_manager_cannot_retrieve_other_employee(self, client, agent_manager, agent):
        """Test that an agent manager cannot retrieve another employee's record."""
        client.force_authenticate(user=agent_manager)
        employee = Employee.objects.get(user=agent)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_can_retrieve_self(self, client, agent):
        """Test that an agent can retrieve their own employee record."""
        client.force_authenticate(user=agent)
        employee = Employee.objects.get(user=agent)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['username'] == agent.username

    def test_unauthenticated_user_cannot_retrieve_employee(self, client, analyst):
        """Test that an unauthenticated user cannot retrieve any employee record."""
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestEmployeeCreate:
    """Tests for creating employees via the API."""

    def test_superuser_can_create_employee(self, client, superuser, organization):
        """Test that a superuser can create a new employee with organization specified."""
        client.force_authenticate(user=superuser)
        url = reverse('employee-list')
        data = {
            'user': {
                'username': 'new_user',
                'password': 'password',
                'email': 'new_user@example.com'
            },
            'role': 'ANALYST',
            'manager': None,
            'is_organization_admin': False,
            'organization': organization.id,
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        new_employee_id = response.data['id']
        new_employee = Employee.objects.get(id=new_employee_id)
        assert new_employee.user.username == 'new_user'

    def test_superuser_cannot_create_employee_without_organization(self, client, superuser, organization):
        """Test that a superuser cannot create an employee without specifying an organization."""
        client.force_authenticate(user=superuser)
        url = reverse('employee-list')
        data = {
            'user': {
                'username': 'new_user',
                'password': 'password',
                'email': 'new_user@example.com'
            },
            'role': 'ANALYST',
            'manager': None,
            'is_organization_admin': False,
            # 'organization' is intentionally omitted
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data['organization'][0]) == ERROR_MESSAGES['superusers_organization']

    def test_organization_admin_can_create_employee(self, client, organization_admin, organization):
        """Test that an organization admin can create a new employee in their organization."""
        client.force_authenticate(user=organization_admin)
        url = reverse('employee-list')
        data = {
            'user': {
                'username': 'new_employee',
                'password': 'password',
                'email': 'new_employee@example.com'
            },
            'role': 'AGENT',
            'is_organization_admin': False
            # 'organization' is intentionally omitted
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        new_employee_id = response.data['id']
        new_employee = Employee.objects.get(id=new_employee_id)
        assert new_employee.user.username == 'new_employee'

    def test_organization_admin_cannot_create_employee_specifying_organization(self, client, organization_admin,
                                                                               organization):
        """Test that an organization admin cannot specify organization when creating an employee."""
        client.force_authenticate(user=organization_admin)
        url = reverse('employee-list')
        data = {
            'user': {
                'username': 'new_employee',
                'password': 'password',
                'email': 'new_employee@example.com'
            },
            'role': 'AGENT',
            'is_organization_admin': False,
            'organization': organization.id  # Should not specify organization
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data['organization'][0]) == ERROR_MESSAGES['org_admins_organization']

    def test_organization_admin_cannot_create_employee_with_invalid_role(self, client, organization_admin):
        """Test that an organization admin cannot create an employee with an invalid role."""
        client.force_authenticate(user=organization_admin)
        url = reverse('employee-list')
        data = {
            'user': {
                'username': 'invalid_role_user',
                'password': 'password',
                'email': 'invalid@example.com'
            },
            'role': 'INVALID',
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'role' in response.data

    def test_organization_admin_can_create_agent_with_manager(self, client, organization_admin, agent_manager):
        """Test that an organization admin can create an agent with a manager."""
        client.force_authenticate(user=organization_admin)
        agent_manager_agent = agent_manager.employee.agent
        url = reverse('employee-list')
        data = {
            'user': {
                'username': 'agent_with_manager',
                'password': 'password',
                'email': 'agent_with_manager@example.com'
            },
            'role': 'AGENT',
            'manager': agent_manager_agent.id,
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        new_employee_id = response.data['id']
        new_employee = Employee.objects.get(id=new_employee_id)
        assert new_employee.agent.manager == agent_manager_agent

    def test_organization_admin_cannot_create_analyst_with_manager(self, client, organization_admin, agent_manager):
        """Test that an organization admin cannot assign a manager to an analyst."""
        client.force_authenticate(user=organization_admin)
        agent_manager_agent = agent_manager.employee.agent
        url = reverse('employee-list')
        data = {
            'user': {
                'username': 'agent_with_manager',
                'password': 'password',
                'email': 'agent_with_manager@example.com'
            },
            'role': 'ANALYST',
            'manager': agent_manager_agent.id,
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'role' in response.data

    def test_analyst_cannot_create_employee(self, client, analyst):
        """Test that an analyst cannot create a new employee."""
        client.force_authenticate(user=analyst)
        url = reverse('employee-list')
        data = {
            'user': {
                'username': 'new_employee',
                'password': 'password',
                'email': 'new_employee@example.com'
            },
            'role': 'AGENT',
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_create_employee(self, client, agent):
        """Test that an agent cannot create a new employee."""
        client.force_authenticate(user=agent)
        url = reverse('employee-list')
        data = {
            'user': {
                'username': 'new_employee',
                'password': 'password',
                'email': 'new_employee@example.com'
            },
            'role': 'AGENT',
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_create_employee(self, client):
        """Test that an unauthenticated user cannot create a new employee."""
        url = reverse('employee-list')
        data = {
            'user': {
                'username': 'new_employee',
                'password': 'password',
                'email': 'new_employee@example.com'
            },
            'role': 'AGENT',
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestEmployeeUpdate:
    """Tests for updating employees via the API."""

    def test_superuser_can_update_any_employee(self, client, superuser, analyst):
        """Test that a superuser can update any employee's information."""
        client.force_authenticate(user=superuser)
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        data = {'is_organization_admin': True}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        new_employee_id = response.data['id']
        new_employee = Employee.objects.get(id=new_employee_id)
        assert new_employee.is_organization_admin

    def test_superuser_can_update_employee_organization(self, client, superuser, analyst, organization,
                                                        another_organization):
        """Test that a superuser can change an employee's organization."""
        client.force_authenticate(user=superuser)
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        data = {'organization': another_organization.id}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        updated_employee = Employee.objects.get(id=employee.id)
        assert updated_employee.organization == another_organization

    def test_superuser_cannot_change_employee_role(self, client, superuser, analyst):
        """Test that a superuser cannot change an employee's role."""
        client.force_authenticate(user=superuser)
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        data = {'role': 'AGENT'}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'It is not possible to change role' in str(response.data)

    def test_superuser_can_update_employee_manager(self, client, superuser, agent, agent_manager):
        """Test that a superuser can assign or change an employee's manager."""
        employee = Employee.objects.get(user=agent)
        manager_employee = Employee.objects.get(user=agent_manager)

        client.force_authenticate(user=superuser)
        url = reverse('employee-detail', args=[employee.id])
        data = {'manager': manager_employee.agent.id}
        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        updated_employee = Employee.objects.get(id=employee.id)
        assert updated_employee.agent.manager == manager_employee.agent

    def test_superuser_can_unset_employee_manager(self, client, superuser, agent_manager):
        """Test that a superuser can unset an employee's manager."""
        manager_employee = Employee.objects.get(user=agent_manager)
        employee = Agent.objects.get(manager=manager_employee.agent)

        client.force_authenticate(user=superuser)
        url = reverse('employee-detail', args=[employee.id])
        data = {'manager': None}
        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        updated_employee = Employee.objects.get(id=employee.id)
        assert updated_employee.agent.manager is None

    def test_organization_admin_can_update_employee_in_organization(self, client, organization_admin, analyst):
        """Test that an organization admin can update an employee in their organization."""
        client.force_authenticate(user=organization_admin)
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        data = {'is_organization_admin': True}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        new_employee_id = response.data['id']
        new_employee = Employee.objects.get(id=new_employee_id)
        assert new_employee.is_organization_admin

    def test_organization_admin_cannot_update_employee_organization(self, client, organization_admin, analyst,
                                                                    organization, another_organization):
        """Test that an organization admin cannot change an employee's organization."""
        client.force_authenticate(user=organization_admin)
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        data = {'organization': another_organization.id}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data['organization'][0]) == ERROR_MESSAGES['org_admins_organization']

    def test_organization_admin_cannot_change_employee_role(self, client, organization_admin, analyst):
        """Test that an organization admin cannot change an employee's role."""
        client.force_authenticate(user=organization_admin)
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        data = {'role': 'AGENT'}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'It is not possible to change role' in str(response.data)

    def test_organization_admin_can_update_employee_manager(self, client, organization_admin, agent, agent_manager):
        """Test that an organization admin can assign or change an employee's manager within the organization."""
        employee = Employee.objects.get(user=agent)
        manager_employee = Employee.objects.get(user=agent_manager)

        client.force_authenticate(user=organization_admin)
        url = reverse('employee-detail', args=[employee.id])
        data = {'manager': manager_employee.agent.id}
        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        updated_employee = Employee.objects.get(id=employee.id)
        assert updated_employee.agent.manager == manager_employee.agent

    def test_organization_admin_can_unset_employee_manager(self, client, organization_admin, agent_manager):
        """Test that an organization admin can unset an employee's manager."""
        manager_employee = Employee.objects.get(user=agent_manager)
        employee = Agent.objects.get(manager=manager_employee.agent)

        client.force_authenticate(user=organization_admin)
        url = reverse('employee-detail', args=[employee.id])
        data = {'manager': None}
        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        updated_employee = Employee.objects.get(id=employee.id)
        assert updated_employee.agent.manager is None

    def test_organization_admin_cannot_update_employee_manager_to_other_organization(self, client, organization_admin,
                                                                                     agent, another_organization):
        """Test that an organization admin cannot assign a manager from another organization."""
        client.force_authenticate(user=organization_admin)
        employee = Employee.objects.get(user=agent)
        other_agent_user = User.objects.create_user('other_agent', 'other_agent@example.com', 'password')
        other_agent = Agent.objects.create(user=other_agent_user, organization=another_organization)
        url = reverse('employee-detail', args=[employee.id])
        data = {'manager': other_agent.id}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data['manager'][0]) == ERROR_MESSAGES['manager_same_organization']

    def test_analyst_cannot_update_employee(self, client, analyst, agent):
        """Test that an analyst cannot update another employee's information."""
        client.force_authenticate(user=analyst)
        employee = Employee.objects.get(user=agent)
        url = reverse('employee-detail', args=[employee.id])
        data = {'is_organization_admin': False}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyst_cannot_update_self(self, client, analyst):
        """Test that an analyst cannot update their own employee record."""
        client.force_authenticate(user=analyst)
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        data = {'is_organization_admin': False}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_update_employee(self, client, agent, analyst):
        """Test that an agent cannot update another employee's information."""
        client.force_authenticate(user=agent)
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        data = {'is_organization_admin': True}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_update_self(self, client, agent):
        """Test that an agent cannot update their own employee record."""
        client.force_authenticate(user=agent)
        employee = Employee.objects.get(user=agent)
        url = reverse('employee-detail', args=[employee.id])
        data = {'is_organization_admin': True}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_update_employee(self, client, analyst):
        """Test that an unauthenticated user cannot update any employee."""
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        data = {'is_organization_admin': False}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestEmployeeDelete:
    """Tests for deleting employees via the API."""

    def test_superuser_can_delete_any_employee(self, client, superuser, analyst):
        """Test that a superuser can delete any employee."""
        client.force_authenticate(user=superuser)
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_organization_admin_can_delete_employee_in_organization(self, client, organization_admin, analyst):
        """Test that an organization admin can delete an employee in their organization."""
        client.force_authenticate(user=organization_admin)
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_analyst_cannot_delete_employee(self, client, analyst, agent):
        """Test that an analyst cannot delete another employee."""
        client.force_authenticate(user=analyst)
        employee = Employee.objects.get(user=agent)
        url = reverse('employee-detail', args=[employee.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyst_cannot_delete_self(self, client, analyst):
        """Test that an analyst cannot delete their own employee record."""
        client.force_authenticate(user=analyst)
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_delete_employee(self, client, agent, analyst):
        """Test that an agent cannot delete another employee."""
        client.force_authenticate(user=agent)
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_delete_self(self, client, agent):
        """Test that an agent cannot delete their own employee record."""
        client.force_authenticate(user=agent)
        employee = Employee.objects.get(user=agent)
        url = reverse('employee-detail', args=[employee.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_delete_employee(self, client, analyst):
        """Test that an unauthenticated user cannot delete any employee."""
        employee = Employee.objects.get(user=analyst)
        url = reverse('employee-detail', args=[employee.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN