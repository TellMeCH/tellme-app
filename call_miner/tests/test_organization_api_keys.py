import pytest
from django.urls import reverse
from rest_framework import status
from call_miner.models import OrganizationAPIKey

ERROR_MESSAGES = {
    'max_keys_reached': "Cannot add more API keys to this organization; max key count reached.",
    'duplicated_key_name': 'An API key with this name already exists in this organization.'
}


@pytest.mark.django_db
class TestOrganizationAPIKeyList:
    """Tests for listing organization API keys."""

    def test_superuser_can_list_all_api_keys(self, client, superuser, api_key, another_organization):
        """
        Superuser should be able to see all API keys across organizations.
        """
        client.force_authenticate(user=superuser)
        url = reverse('api-key-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_org_admin_can_list_own_organization_keys(
        self, client, organization_admin_user, organization, api_key, another_organization
    ):
        """
        Organization admin can list keys for their own organization, but not from others.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('api-key-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        # Should see keys from his own org only
        returned_ids = {item['id'] for item in response.data['results']}
        org_keys = OrganizationAPIKey.objects.filter(organization=organization).values_list('id', flat=True)
        assert set(org_keys) == returned_ids

    def test_analyst_cannot_list_api_keys(self, client, analyst_user):
        """
        An analyst (non-admin) should not be able to list API keys.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('api-key-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_list_api_keys(self, client, agent_user):
        """
        An agent should not be able to list API keys.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('api-key-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_list_api_keys(self, client):
        """
        An unauthenticated user should not be able to list API keys.
        """
        url = reverse('api-key-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestOrganizationAPIKeyRetrieve:
    """Tests for retrieving a single API key."""

    def test_superuser_can_retrieve_any_api_key(self, client, superuser, api_key):
        """
        Superuser can retrieve any existing key.
        """
        client.force_authenticate(user=superuser)
        url = reverse('api-key-detail', args=[api_key.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == api_key.name

    def test_org_admin_can_retrieve_own_org_api_key(self, client, organization_admin_user, api_key):
        """
        Organization admin can retrieve an API key that belongs to their org.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('api-key-detail', args=[api_key.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_org_admin_cannot_retrieve_other_org_api_key(self, client, organization_admin_user, another_organization):
        """
        Organization admin cannot retrieve an API key from a different org.
        """
        # Create a key in the 'another_organization'
        other_key = OrganizationAPIKey.create_key(
            organization=another_organization, name="Another Org Key"
        )
        other_api_key = another_organization.api_keys.get(name="Another Org Key")

        client.force_authenticate(user=organization_admin_user)
        url = reverse('api-key-detail', args=[other_api_key.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_analyst_cannot_retrieve_api_keys(self, client, analyst_user, api_key):
        """
        Analyst should not be able to retrieve any API key.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('api-key-detail', args=[api_key.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_retrieve_api_keys(self, client, agent_user, api_key):
        """
        Agent should not be able to retrieve any API key.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('api-key-detail', args=[api_key.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_retrieve_api_key(self, client, api_key):
        """
        Unauthenticated user cannot retrieve any API key.
        """
        url = reverse('api-key-detail', args=[api_key.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestOrganizationAPIKeyCreate:
    """Tests for creating new API keys."""

    def test_superuser_can_create_api_key_for_any_organization(self, client, superuser, organization):
        """
        Superuser can create a new API key for any organization.
        """
        client.force_authenticate(user=superuser)
        url = reverse('api-key-list')
        data = {
            "name": "Superuser Created Key",
            "organization": organization.id
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'plain_key' in response.data

        # Confirm it actually got created
        new_key = OrganizationAPIKey.objects.get(name="Superuser Created Key")
        assert new_key.organization == organization

    def test_org_admin_can_create_api_key_for_own_org(self, client, organization_admin_user, organization):
        """
        Org admin can create a new API key for their own organization.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('api-key-list')
        response = client.post(url, {"name": "Org Admin Key"}, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'plain_key' in response.data

        new_key = OrganizationAPIKey.objects.get(name="Org Admin Key")
        assert new_key.organization == organization

    def test_org_admin_cannot_create_api_key_for_other_org(self, client, organization_admin_user, another_organization):
        """
        Org admin cannot create an API key for a different organization.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('api-key-list')
        data = {
            "name": "Invalid Key",
            "organization": another_organization.id
        }
        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_analyst_cannot_create_api_key(self, client, analyst_user, organization):
        """
        Analyst should not be able to create any API key.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('api-key-list')
        response = client.post(url, {"name": "Analyst Key Attempt"}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_create_api_key(self, client, agent_user, organization):
        """
        Agent should not be able to create any API key.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('api-key-list')
        response = client.post(url, {"name": "Agent Key Attempt"}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_create_api_key(self, client, organization):
        """
        Unauthenticated user cannot create any API key.
        """
        url = reverse('api-key-list')
        response = client.post(url, {"name": "Unauthenticated Key Attempt"}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_api_key_beyond_max(self, client, organization_admin_user, organization):
        """
        Even an org admin cannot create more than MAX_KEYS_PER_ORG keys for the org.
        By default, OrganizationAPIKey.MAX_KEYS_PER_ORG = 3
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('api-key-list')

        # Create up to the max
        keys_to_create = OrganizationAPIKey.MAX_KEYS_PER_ORG - organization.api_keys.count()
        for i in range(keys_to_create):
            response = client.post(url, {"name": f"Key_{i}"}, format='json')
            assert response.status_code == status.HTTP_201_CREATED

        # Attempt to create one more beyond the max
        response = client.post(url, {"name": "Excess Key"}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ERROR_MESSAGES['max_keys_reached'] in str(response.data['non_field_errors'])

    def test_create_api_key_with_duplicate_name(self, client, organization_admin_user, organization, api_key):
        """
        Even an org admin cannot create an API key with the same name as an existing one.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('api-key-list')

        response = client.post(url, {'name': api_key.name}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ERROR_MESSAGES['duplicated_key_name'] in str(response.data['name'])


@pytest.mark.django_db
class TestOrganizationAPIKeyRegenerate:
    """Tests for the custom `regenerate` action."""

    def test_superuser_can_regenerate_api_key(self, client, superuser, api_key):
        """
        Superuser can regenerate (delete + create new one with same name).
        """
        client.force_authenticate(user=superuser)
        url = reverse('api-key-regenerate', args=[api_key.id])
        response = client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['plain_key'] is not None

        with pytest.raises(OrganizationAPIKey.DoesNotExist):
            OrganizationAPIKey.objects.get(id=api_key.id)

        new_key = OrganizationAPIKey.objects.get(name=api_key.name)
        assert new_key is not None

    def test_org_admin_can_regenerate_own_org_api_key(self, client, organization_admin_user, api_key):
        """
        Org admin can regenerate a key from their own organization.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('api-key-regenerate', args=[api_key.id])
        response = client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_201_CREATED

        with pytest.raises(OrganizationAPIKey.DoesNotExist):
            OrganizationAPIKey.objects.get(id=api_key.id)

        new_key = OrganizationAPIKey.objects.get(name=api_key.name)
        assert new_key is not None

    def test_org_admin_cannot_regenerate_key_in_other_org(self, client, organization_admin_user, another_organization):
        """
        Org admin cannot regenerate a key from a different organization.
        """
        other_key = OrganizationAPIKey.create_key(
            organization=another_organization, name="Another Org Key"
        )
        other_api_key = another_organization.api_keys.get(name="Another Org Key")

        client.force_authenticate(user=organization_admin_user)
        url = reverse('api-key-regenerate', args=[other_api_key.id])
        response = client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_analyst_cannot_regenerate_api_key(self, client, analyst_user, api_key):
        client.force_authenticate(user=analyst_user)
        url = reverse('api-key-regenerate', args=[api_key.id])
        response = client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_regenerate_api_key(self, client, agent_user, api_key):
        client.force_authenticate(user=agent_user)
        url = reverse('api-key-regenerate', args=[api_key.id])
        response = client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_regenerate_api_key(self, client, api_key):
        url = reverse('api-key-regenerate', args=[api_key.id])
        response = client.post(url, {}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestOrganizationAPIKeyDelete:
    """Tests for deleting an organization API key."""

    def test_superuser_can_delete_api_key(self, client, superuser, api_key):
        """
        Superuser can delete any API key.
        """
        client.force_authenticate(user=superuser)
        url = reverse('api-key-detail', args=[api_key.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        with pytest.raises(OrganizationAPIKey.DoesNotExist):
            OrganizationAPIKey.objects.get(id=api_key.id)

    def test_org_admin_can_delete_own_api_key(self, client, organization_admin_user, api_key):
        """
        Org admin can delete their own org's API key.
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('api-key-detail', args=[api_key.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        with pytest.raises(OrganizationAPIKey.DoesNotExist):
            OrganizationAPIKey.objects.get(id=api_key.id)

    def test_org_admin_cannot_delete_other_org_api_key(self, client, organization_admin_user, another_organization):
        """
        Org admin cannot delete an API key from a different organization.
        """
        other_key = OrganizationAPIKey.create_key(
            organization=another_organization, name="Another Org Key"
        )
        other_api_key = another_organization.api_keys.get(name="Another Org Key")

        client.force_authenticate(user=organization_admin_user)
        url = reverse('api-key-detail', args=[other_api_key.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_analyst_cannot_delete_api_key(self, client, analyst_user, api_key):
        """
        Analyst cannot delete any API key.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('api-key-detail', args=[api_key.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_agent_cannot_delete_api_key(self, client, agent_user, api_key):
        """
        Agent cannot delete any API key.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('api-key-detail', args=[api_key.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_user_cannot_delete_api_key(self, client, api_key):
        """
        Unauthenticated user cannot delete any API key.
        """
        url = reverse('api-key-detail', args=[api_key.id])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
