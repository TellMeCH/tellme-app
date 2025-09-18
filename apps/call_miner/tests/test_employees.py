import pytest
from rest_framework import status
from django.urls import reverse
from django.conf import settings
from apps.call_miner.models import Employee, Agent, User

ERROR_MESSAGES = {
    'org_admins_organization': "Org Admins should not provide an organization when modifying an Employee.",
    'manager_same_organization': 'Manager must belong to the same organization as the current user.',
    'analysts_managers': "Analysts can't have managers.",
    'superusers_organization': "Superusers must provide an organization when creating an Employee.",
    'max_user_count_reached': "Cannot add more users to this organization; max user count reached.",
    'protected_user_email': 'Provided user email is protected.',
    'duplicate_user_email': 'user with this email already exists.'
}


@pytest.mark.django_db
class TestEmployeeList:
    """Tests for the Employee list API endpoint."""

    def test_superuser_can_list_all_employees(self, client, superuser, organization_admin_user, analyst_user,
                                              agent_manager_user, agent, another_organization_agent):
        """Test that a superuser can list all employees across organizations."""
        client.force_authenticate(user=superuser)
        url = reverse('employee-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 6

    def test_organization_admin_can_list_own_organization_employees(self, client, superuser, organization_admin_user,
                                                                    analyst_user, agent_manager_user, agent,
                                                                    another_organization_agent_user):
        """Test that an organization admin can list employees in their own organization."""
        client.force_authenticate(user=organization_admin_user)
        url = reverse('employee-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5

    def test_analyst_cannot_list_employees(self, client, analyst_user):
        """Test that an analyst cannot list employees."""
        client.force_authenticate(user=analyst_user)
        url = reverse('employee-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_list_employees(self, client, agent_user):
        """Test that an agent cannot list employees."""
        client.force_authenticate(user=agent_user)
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

    def test_superuser_can_retrieve_any_employee(self, client, superuser, analyst_user,
                                                 another_organization_agent_user):
        """Test that a superuser can retrieve any employee from any organization."""
        client.force_authenticate(user=superuser)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['email'] == analyst_user.email

        another_employee = Employee.objects.get(user=another_organization_agent_user)
        url = reverse('employee-detail', args=[another_employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['email'] == another_organization_agent_user.email

    def test_organization_admin_can_retrieve_employee_in_organization(self, client, organization_admin_user,
                                                                      analyst_user):
        """Test that an organization admin can retrieve an employee in their organization."""
        client.force_authenticate(user=organization_admin_user)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['email'] == analyst_user.email

    def test_organization_admin_cannot_retrieve_employee_in_another_organization(self, client, organization_admin_user,
                                                                                 another_organization_agent_user):
        """Test that an organization admin cannot retrieve an employee from another organization."""
        client.force_authenticate(user=organization_admin_user)
        another_employee = Employee.objects.get(user=another_organization_agent_user)
        url = reverse('employee-detail', args=[another_employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_analyst_can_retrieve_self(self, client, analyst_user):
        """Test that an analyst can retrieve their own employee record."""
        client.force_authenticate(user=analyst_user)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['email'] == analyst_user.email

    def test_analyst_cannot_retrieve_other_employee(self, client, analyst_user, agent_user):
        """Test that an analyst cannot retrieve another employee's record."""
        client.force_authenticate(user=analyst_user)
        employee = Employee.objects.get(user=agent_user)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_manager_can_retrieve_self(self, client, agent_manager_user):
        """Test that an agent manager can retrieve their own employee record."""
        client.force_authenticate(user=agent_manager_user)
        employee = Employee.objects.get(user=agent_manager_user)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['email'] == agent_manager_user.email

    def test_agent_manager_cannot_retrieve_other_employee(self, client, agent_manager_user, agent_user):
        """Test that an agent manager cannot retrieve another employee's record."""
        client.force_authenticate(user=agent_manager_user)
        employee = Employee.objects.get(user=agent_user)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_can_retrieve_self(self, client, agent_user):
        """Test that an agent can retrieve their own employee record."""
        client.force_authenticate(user=agent_user)
        employee = Employee.objects.get(user=agent_user)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['email'] == agent_user.email

    def test_unauthenticated_user_cannot_retrieve_employee(self, client, analyst_user):
        """Test that an unauthenticated user cannot retrieve any employee record."""
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_me_action_analyst(self, client, analyst_user):
        """Test that an analyst can retrieve its own overview"""
        client.force_authenticate(user=analyst_user)
        url = reverse('employee-me')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['email'] == analyst_user.email

    def test_me_action_agent(self, client, agent_user):
        """Test that an agent can retrieve its own overview"""
        client.force_authenticate(user=agent_user)
        url = reverse('employee-me')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['email'] == agent_user.email

    def test_me_action_unauthenticated_user(self, client, agent_user):
        """Test that an unauthenticated user can't retrieve its own overview"""
        url = reverse('employee-me')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestEmployeeCreate:
    """Tests for creating employees via the API."""

    def test_superuser_can_create_employee(self, client, superuser, organization, mock_user_email_sending):
        """Test that a superuser can create a new employee with organization specified."""
        client.force_authenticate(user=superuser)
        url = reverse('employee-list')
        data = {
            'user': {
                'first_name': 'new',
                'last_name': 'user',
                'auth_type': 'google',
                'email': 'new_user@example.com'
            },
            'role': 'ANALYST',
            'manager': None,
            'is_organization_admin': False,
            'organization': organization.id,
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        new_user = User.objects.get(email=response.data['user']['email'])
        new_employee = new_user.employee
        assert new_user.first_name == 'new'
        assert new_user.email == 'new_user@example.com'
        assert new_employee.role == 'ANALYST'
        assert hasattr(new_employee, 'analyst')

        mock_onboarding, mock_verification = mock_user_email_sending
        mock_onboarding.assert_called_once()

    def test_superuser_cannot_create_employee_without_organization(self, client, superuser, organization,
                                                                   mock_user_email_sending):
        """Test that a superuser cannot create an employee without specifying an organization."""
        client.force_authenticate(user=superuser)
        url = reverse('employee-list')
        data = {
            'user': {
                'first_name': 'new',
                'last_name': 'user',
                'auth_type': 'google',
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

        mock_onboarding, mock_verification = mock_user_email_sending
        mock_onboarding.assert_not_called()

    def test_organization_admin_can_create_employee(self, client, organization_admin_user, organization,
                                                    mock_user_email_sending):
        """Test that an organization admin can create a new employee in their organization."""
        client.force_authenticate(user=organization_admin_user)
        url = reverse('employee-list')
        data = {
            'user': {
                'first_name': 'new',
                'last_name': 'user',
                'auth_type': 'google',
                'email': 'new_employee@example.com'
            },
            'role': 'ANALYST',
            'is_organization_admin': False
            # 'organization' is intentionally omitted
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        new_user = User.objects.get(email=response.data['user']['email'])
        new_employee = new_user.employee
        assert new_user.first_name == 'new'
        assert new_user.email == 'new_employee@example.com'
        assert new_employee.role == 'ANALYST'
        assert hasattr(new_employee, 'analyst')

        mock_onboarding, mock_verification = mock_user_email_sending
        mock_onboarding.assert_called_once()

    def test_organization_admin_cannot_create_employee_specifying_organization(self, client, organization_admin_user,
                                                                               organization):
        """Test that an organization admin cannot specify organization when creating an employee."""
        client.force_authenticate(user=organization_admin_user)
        url = reverse('employee-list')
        data = {
            'user': {
                'first_name': 'new',
                'last_name': 'user',
                'auth_type': 'google',
                'email': 'new_user@example.com'
            },
            'role': 'AGENT',
            'is_organization_admin': False,
            'organization': organization.id  # Should not specify organization
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data['organization'][0]) == ERROR_MESSAGES['org_admins_organization']

    def test_organization_admin_cannot_create_employee_with_invalid_role(self, client, organization_admin_user):
        """Test that an organization admin cannot create an employee with an invalid role."""
        client.force_authenticate(user=organization_admin_user)
        url = reverse('employee-list')
        data = {
            'user': {
                'first_name': 'new',
                'last_name': 'user',
                'auth_type': 'google',
                'email': 'new_user@example.com'
            },
            'role': 'INVALID',
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'role' in response.data

    def test_organization_admin_can_create_agent_with_manager(self, client, organization_admin_user, agent_manager_user):
        """Test that an organization admin can create an agent with a manager."""
        client.force_authenticate(user=organization_admin_user)
        agent_manager_agent = agent_manager_user.employee.agent
        url = reverse('employee-list')
        data = {
            'user': {
                'first_name': 'agent_with_manager',
                'last_name': 'user',
                'auth_type': 'google',
                'email': 'agent_with_manager@example.com'
            },
            'role': 'AGENT',
            'manager': agent_manager_agent.id,
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        new_user = User.objects.get(email=response.data['user']['email'])
        new_employee = new_user.employee
        assert new_user.first_name == 'agent_with_manager'
        assert new_user.email == 'agent_with_manager@example.com'
        assert new_employee.role == 'AGENT'
        assert hasattr(new_employee, 'agent')
        assert new_employee.agent.manager == agent_manager_agent

    def test_organization_admin_cannot_create_analyst_with_manager(self, client, organization_admin_user,
                                                                   agent_manager_user):
        """Test that an organization admin cannot assign a manager to an analyst."""
        client.force_authenticate(user=organization_admin_user)
        agent_manager_agent = agent_manager_user.employee.agent
        url = reverse('employee-list')
        data = {
            'user': {
                'first_name': 'agent_with_manager',
                'last_name': 'user',
                'auth_type': 'google',
                'email': 'new_user@example.com'
            },
            'role': 'ANALYST',
            'manager': agent_manager_agent.id,
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'role' in response.data

    def test_analyst_cannot_create_employee(self, client, analyst_user):
        """Test that an analyst cannot create a new employee."""
        client.force_authenticate(user=analyst_user)
        url = reverse('employee-list')
        data = {
            'user': {
                'first_name': 'new',
                'last_name': 'user',
                'auth_type': 'google',
                'email': 'new_user@example.com'
            },
            'role': 'AGENT',
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_create_employee(self, client, agent_user):
        """Test that an agent cannot create a new employee."""
        client.force_authenticate(user=agent_user)
        url = reverse('employee-list')
        data = {
            'user': {
                'first_name': 'new',
                'last_name': 'user',
                'auth_type': 'google',
                'email': 'new_user@example.com'
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
                'first_name': 'new',
                'last_name': 'user',
                'auth_type': 'google',
                'email': 'new_user@example.com'
            },
            'role': 'AGENT',
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_superuser_cannot_create_employee_beyond_max_user_count(self, client, superuser, organization):
        """Test that even a superuser cannot create more employees than the organization's max_user_count."""
        client.force_authenticate(user=superuser)
        url = reverse('employee-list')
        employees_to_create = organization.max_user_count - Employee.objects.filter(organization=organization).count()

        # Create employees up to the max count
        for i in range(employees_to_create):
            url = reverse('employee-list')
            data = {
                'user': {
                    'first_name': f'superuser_employee_{i}',
                    'last_name': 'user',
                    'auth_type': 'google',
                    'email': f'superuser_employee_{i}@example.com'
                },
                'role': 'ANALYST',
                'manager': None,
                'is_organization_admin': False,
                'organization': organization.id
            }
            response = client.post(url, data, format='json')
            assert response.status_code == status.HTTP_201_CREATED

        # Attempt to create one more employee beyond the max count
        data = {
            'user': {
                'first_name': 'excess_superuser_employee',
                'last_name': 'user',
                'auth_type': 'google',
                'email': 'excess_superuser_employee@example.com'
            },
            'role': 'ANALYST',
            'manager': None,
            'is_organization_admin': False,
            'organization': organization.id
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ERROR_MESSAGES['max_user_count_reached'] in str(response.data['non_field_errors'])

    def test_organization_admin_cannot_create_employee_beyond_max_user_count(self, client, organization_admin_user,
                                                                             organization):
        """Test that an organization admin cannot create more employees than the organization's max_user_count."""
        client.force_authenticate(user=organization_admin_user)
        url = reverse('employee-list')
        employees_to_create = organization.max_user_count - Employee.objects.filter(organization=organization).count()

        # Create employees up to the max count
        for i in range(employees_to_create):
            data = {
                'user': {
                    'first_name': f'employee_{i}',
                    'last_name': 'user',
                    'auth_type': 'google',
                    'email': f'employee_{i}@example.com'
                },
                'role': 'AGENT',
                'is_organization_admin': False
            }
            response = client.post(url, data, format='json')
            assert response.status_code == status.HTTP_201_CREATED

        # Attempt to create one more employee beyond the max count
        data = {
            'user': {
                'first_name': 'excess_employee',
                'last_name': 'user',
                'auth_type': 'google',
                'email': 'excess_employee@example.com'
            },
            'role': 'AGENT',
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ERROR_MESSAGES['max_user_count_reached'] in str(response.data['non_field_errors'])

    def test_superuser_cannot_create_employee_with_protected_email(self, client, superuser, organization):
        """Test that even a superuser cannot create an employee with a protected email"""
        client.force_authenticate(user=superuser)
        url = reverse('employee-list')
        data = {
            'user': {
                'first_name': f'protected_employee',
                'last_name': 'user',
                'auth_type': 'google',
                'email': settings.PROCESSING_PIPELINE_USER
            },
            'role': 'AGENT',
            'organization': organization.id,
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ERROR_MESSAGES['protected_user_email'] in str(response.data['user']['email'])

    def test_organization_admin_cannot_create_employee_with_protected_email(self, client, organization_admin_user):
        """Test that even an organization admin cannot create an employee with a protected email"""
        client.force_authenticate(user=organization_admin_user)
        url = reverse('employee-list')
        data = {
            'user': {
                'first_name': f'protected_employee',
                'last_name': 'user',
                'auth_type': 'google',
                'email': settings.PROCESSING_PIPELINE_USER
            },
            'role': 'AGENT',
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ERROR_MESSAGES['protected_user_email'] in str(response.data['user']['email'])

    def test_superuser_cannot_create_employee_with_duplicate_email(self, client, superuser, organization, analyst_user):
        """Test that even a superuser cannot create an employee with a duplicate email"""
        client.force_authenticate(user=superuser)
        url = reverse('employee-list')
        data = {
            'user': {
                'first_name': 'Duplicate',
                'last_name': 'Email',
                'auth_type': 'google',
                'email': 'analyst@example.com',
            },
            'role': 'AGENT',
            'organization': organization.id,
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ERROR_MESSAGES['duplicate_user_email'] in str(response.data['user']['email'])
        
    def test_org_admin_cannot_create_employee_with_duplicate_email(
            self, client, organization_admin_user, organization, analyst_user
    ):
        """Test that an organization admin cannot create an employee with a duplicate email"""
        client.force_authenticate(user=organization_admin_user)
        url = reverse('employee-list')
        data = {
            'user': {
                'first_name': 'Duplicate',
                'last_name': 'Email',
                'auth_type': 'google',
                'email': 'analyst@example.com',
            },
            'role': 'AGENT',
            'is_organization_admin': False
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ERROR_MESSAGES['duplicate_user_email'] in str(response.data['user']['email'])


@pytest.mark.django_db
class TestEmployeeUpdate:
    """Tests for updating employees via the API."""

    def test_superuser_can_update_any_employee(self, client, superuser, analyst_user):
        """Test that a superuser can update any employee's information."""
        client.force_authenticate(user=superuser)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        data = {'is_organization_admin': True}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        updated_employee = Employee.objects.get(id=employee.id)
        assert updated_employee.is_organization_admin

    def test_superuser_can_update_employee_organization(self, client, superuser, analyst_user, organization,
                                                        another_organization):
        """Test that a superuser can change an employee's organization."""
        client.force_authenticate(user=superuser)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        data = {'organization': another_organization.id}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        updated_employee = Employee.objects.get(id=employee.id)
        assert updated_employee.organization == another_organization

    def test_superuser_cannot_change_employee_role(self, client, superuser, analyst_user):
        """Test that a superuser cannot change an employee's role."""
        client.force_authenticate(user=superuser)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        data = {'role': 'AGENT'}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'It is not possible to change role' in str(response.data)

    def test_superuser_can_update_employee_manager(self, client, superuser, agent_user, agent_manager_user):
        """Test that a superuser can assign or change an employee's manager."""
        employee = Employee.objects.get(user=agent_user)
        manager_employee = Employee.objects.get(user=agent_manager_user)

        client.force_authenticate(user=superuser)
        url = reverse('employee-detail', args=[employee.id])
        data = {'manager': manager_employee.agent.id}
        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        updated_employee = Employee.objects.get(id=employee.id)
        assert updated_employee.agent.manager == manager_employee.agent

    def test_superuser_can_unset_employee_manager(self, client, superuser, agent_manager_user):
        """Test that a superuser can unset an employee's manager."""
        manager_employee = Employee.objects.get(user=agent_manager_user)
        employee = Agent.objects.get(manager=manager_employee.agent)

        client.force_authenticate(user=superuser)
        url = reverse('employee-detail', args=[employee.id])
        data = {'manager': None}
        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        updated_employee = Employee.objects.get(id=employee.id)
        assert updated_employee.agent.manager is None

    def test_organization_admin_can_update_employee_in_organization(self, client, organization_admin_user,
                                                                    analyst_user):
        """Test that an organization admin can update an employee in their organization."""
        client.force_authenticate(user=organization_admin_user)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        data = {'is_organization_admin': True}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        new_employee = Employee.objects.get(id=employee.id)
        assert new_employee.is_organization_admin

    def test_organization_admin_cannot_update_employee_organization(self, client, organization_admin_user,
                                                                    analyst_user,
                                                                    organization, another_organization):
        """Test that an organization admin cannot change an employee's organization."""
        client.force_authenticate(user=organization_admin_user)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        data = {'organization': another_organization.id}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data['organization'][0]) == ERROR_MESSAGES['org_admins_organization']

    def test_organization_admin_cannot_change_employee_role(self, client, organization_admin_user,
                                                            analyst_user):
        """Test that an organization admin cannot change an employee's role."""
        client.force_authenticate(user=organization_admin_user)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        data = {'role': 'AGENT'}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'It is not possible to change role' in str(response.data)

    def test_organization_admin_can_update_employee_manager(self, client, organization_admin_user, agent_user,
                                                            agent_manager_user):
        """Test that an organization admin can assign or change an employee's manager within the organization."""
        employee = Employee.objects.get(user=agent_user)
        manager_employee = Employee.objects.get(user=agent_manager_user)

        client.force_authenticate(user=organization_admin_user)
        url = reverse('employee-detail', args=[employee.id])
        data = {'manager': manager_employee.agent.id}
        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        updated_employee = Employee.objects.get(id=employee.id)
        assert updated_employee.agent.manager == manager_employee.agent

    def test_organization_admin_can_unset_employee_manager(self, client, organization_admin_user, agent_manager_user):
        """Test that an organization admin can unset an employee's manager."""
        manager_employee = Employee.objects.get(user=agent_manager_user)
        employee = Agent.objects.get(manager=manager_employee.agent)

        client.force_authenticate(user=organization_admin_user)
        url = reverse('employee-detail', args=[employee.id])
        data = {'manager': None}
        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        updated_employee = Employee.objects.get(id=employee.id)
        assert updated_employee.agent.manager is None

    def test_organization_admin_cannot_update_employee_manager_to_other_organization(self, client,
                                                                                     organization_admin_user,
                                                                                     agent_user, another_organization):
        """Test that an organization admin cannot assign a manager from another organization."""
        client.force_authenticate(user=organization_admin_user)
        employee = Employee.objects.get(user=agent_user)
        other_agent_user = User.objects.create_user('other_agent@example.com', 'password', 'other', 'agent')
        other_agent = Agent.objects.create(user=other_agent_user, organization=another_organization)
        url = reverse('employee-detail', args=[employee.id])
        data = {'manager': other_agent.id}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert str(response.data['manager'][0]) == ERROR_MESSAGES['manager_same_organization']

    def test_analyst_cannot_update_employee(self, client, analyst_user, agent_user):
        """Test that an analyst cannot update another employee's information."""
        client.force_authenticate(user=analyst_user)
        employee = Employee.objects.get(user=agent_user)
        url = reverse('employee-detail', args=[employee.id])
        data = {'is_organization_admin': False}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyst_cannot_update_self(self, client, analyst_user):
        """Test that an analyst cannot update their own employee record."""
        client.force_authenticate(user=analyst_user)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        data = {'is_organization_admin': False}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_update_employee(self, client, agent_user, analyst_user):
        """Test that an agent cannot update another employee's information."""
        client.force_authenticate(user=agent_user)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        data = {'is_organization_admin': True}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_update_self(self, client, agent_user):
        """Test that an agent cannot update their own employee record."""
        client.force_authenticate(user=agent_user)
        employee = Employee.objects.get(user=agent_user)
        url = reverse('employee-detail', args=[employee.id])
        data = {'is_organization_admin': True}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_update_employee(self, client, analyst_user):
        """Test that an unauthenticated user cannot update any employee."""
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        data = {'is_organization_admin': False}
        response = client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestEmployeeDelete:
    """Tests for deleting employees via the API."""

    def test_superuser_can_delete_any_employee(self, client, superuser, analyst_user):
        """Test that a superuser can delete any employee."""
        client.force_authenticate(user=superuser)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_organization_admin_can_delete_employee_in_organization(self, client, organization_admin_user,
                                                                    analyst_user):
        """Test that an organization admin can delete an employee in their organization."""
        client.force_authenticate(user=organization_admin_user)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_analyst_cannot_delete_employee(self, client, analyst_user, agent_user):
        """Test that an analyst cannot delete another employee."""
        client.force_authenticate(user=analyst_user)
        employee = Employee.objects.get(user=agent_user)
        url = reverse('employee-detail', args=[employee.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analyst_cannot_delete_self(self, client, analyst_user):
        """Test that an analyst cannot delete their own employee record."""
        client.force_authenticate(user=analyst_user)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_delete_employee(self, client, agent_user, analyst_user):
        """Test that an agent cannot delete another employee."""
        client.force_authenticate(user=agent_user)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_delete_self(self, client, agent_user):
        """Test that an agent cannot delete their own employee record."""
        client.force_authenticate(user=agent_user)
        employee = Employee.objects.get(user=agent_user)
        url = reverse('employee-detail', args=[employee.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_delete_employee(self, client, analyst_user):
        """Test that an unauthenticated user cannot delete any employee."""
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-detail', args=[employee.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestEmployeeActions:
    """Tests for updating employees via the API."""
    def test_superuser_can_invite_any_employee(self, client, superuser, analyst_user, mock_user_email_sending):
        """Test that a superuser can invite any employee"""
        client.force_authenticate(user=superuser)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-invite', args=[employee.id])
        response = client.post(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        mock_onboarding, mock_verification = mock_user_email_sending
        mock_onboarding.assert_called_once()

    def test_organization_admin_can_invite_any_employee(self, client, organization_admin_user, analyst_user,
                                                        mock_user_email_sending):
        """Test that an organization admin can invite any employee"""
        client.force_authenticate(user=organization_admin_user)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-invite', args=[employee.id])
        response = client.post(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        mock_onboarding, mock_verification = mock_user_email_sending
        mock_onboarding.assert_called_once()

    def test_user_cannot_invite_any_employee(self, client, agent_user, analyst_user, mock_user_email_sending):
        """Test that a regular user can't invite any employee"""
        client.force_authenticate(user=agent_user)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-invite', args=[employee.id])
        response = client.post(url, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        mock_onboarding, mock_verification = mock_user_email_sending
        mock_onboarding.assert_not_called()

    def test_user_cannot_invite_self(self, client, analyst_user, mock_user_email_sending):
        """Test that a regular user can't invite itself"""
        client.force_authenticate(user=analyst_user)
        employee = Employee.objects.get(user=analyst_user)
        url = reverse('employee-invite', args=[employee.id])
        response = client.post(url, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        mock_onboarding, mock_verification = mock_user_email_sending
        mock_onboarding.assert_not_called()

    def test_user_can_call_me(self, client, analyst_user):
        """Test that a user can call the /me endpoint"""
        client.force_authenticate(user=analyst_user)
        url = reverse('employee-me')
        response = client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('user').get('email') == analyst_user.email
        assert response.data.get('role') == 'ANALYST'

