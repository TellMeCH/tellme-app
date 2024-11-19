import pytest
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from call_miner.models import Customer

TREND_ACTIONS = ['conversations', 'conversation-trend', 'conversation-topic-trend', 'duration-trend',
                 'sentiment-trend', 'summary-data']


@pytest.mark.django_db
class TestCustomerList:
    """Test the customer-list API endpoint."""

    def test_customer_list_as_superuser(self, client, superuser, customer, another_organization_customer):
        """Test that a superuser can list all customers across organizations."""
        client.force_authenticate(user=superuser)
        url = reverse('customer-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2

    def test_customer_list_as_analyst_in_org(self, client, analyst_user, customer,
                                             another_organization_customer):
        """
        Test that an analyst within the organization can list customers in their organization.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('customer-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == customer.name

    def test_customer_list_as_analyst_outside_org(self, client, another_organization_analyst_user, customer,
                                                  another_organization_customer):
        """
        Test that an analyst outside the organization sees only their own organization's customers.
        """
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('customer-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == another_organization_customer.name

    def test_customer_list_as_agent_in_org(self, client, agent_user, customer):
        """Test that an agent within the organization can list customers in their organization."""
        client.force_authenticate(user=agent_user)
        url = reverse('customer-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == customer.name

    def test_customer_list_as_agent_outside_org(self, client, another_organization_agent_user,
                                                another_organization_customer):
        """Test that an agent outside the organization sees only their own organization's customers."""
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('customer-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == another_organization_customer.name

    def test_customer_list_as_unauthenticated_user(self, client):
        """Test that an unauthenticated user cannot list customers."""
        url = reverse('customer-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCustomerRetrieve:
    """Test the customer-detail API endpoint for viewing a Customer's details."""

    def test_customer_retrieve_as_superuser(self, client, superuser, customer):
        """Test that a superuser can retrieve any customer."""
        client.force_authenticate(user=superuser)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == customer.name

    def test_customer_retrieve_as_analyst_in_org(self, client, analyst_user, customer):
        """Test that an analyst within the organization can retrieve a customer."""
        client.force_authenticate(user=analyst_user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == customer.name

    def test_customer_retrieve_as_analyst_outside_org(self, client, another_organization_analyst_user, customer):
        """Test that an analyst outside the organization cannot retrieve customers from another organization."""
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_customer_retrieve_as_agent_in_org(self, client, agent_user, customer):
        """Test that an agent within the organization can retrieve a customer."""
        client.force_authenticate(user=agent_user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == customer.name

    def test_customer_retrieve_as_agent_outside_org(self, client, another_organization_agent_user, customer):
        """Test that an agent outside the organization cannot retrieve customers from another organization."""
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_customer_retrieve_as_unauthenticated_user(self, client, customer):
        """Test that an unauthenticated user cannot retrieve a customer."""
        url = reverse('customer-detail', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCustomerCreate:
    """Test the creation of a new Customer instance"""

    def test_customer_create_as_superuser(self, client, superuser, organization):
        """Test that a superuser can create a new customer."""
        client.force_authenticate(user=superuser)
        url = reverse('customer-list')
        data = {'name': 'New Customer', 'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Customer.objects.filter(name='New Customer').exists()

    def test_customer_create_as_analyst_in_org(self, client, analyst_user, organization):
        """Test that an analyst within the organization cannot create a new customer."""
        client.force_authenticate(user=analyst_user)
        url = reverse('customer-list')
        data = {'name': 'New Customer', 'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_create_as_analyst_outside_org(self, client, another_organization_analyst_user, organization):
        """Test that an analyst outside the organization cannot create a customer in another organization."""
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('customer-list')
        data = {'name': 'New Customer', 'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_create_as_agent_in_org(self, client, agent_user, organization):
        """Test that an agent within the organization cannot create a new customer."""
        client.force_authenticate(user=agent_user)
        url = reverse('customer-list')
        data = {'name': 'New Customer', 'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_create_as_agent_outside_org(self, client, another_organization_agent_user, organization):
        """Test that an agent outside the organization cannot create a customer in another organization."""
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('customer-list')
        data = {'name': 'New Customer', 'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_create_as_unauthenticated_user(self, client, organization):
        """Test that an unauthenticated user cannot create a customer."""
        url = reverse('customer-list')
        data = {'name': 'New Customer', 'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCustomerUpdate:
    """Tests for the update of existing Customer instances."""

    def test_customer_update_as_superuser(self, client, superuser, customer):
        """Test that a superuser can update a customer."""
        client.force_authenticate(user=superuser)
        url = reverse('customer-detail', args=[customer.pk])
        data = {'name': 'Updated Customer Name'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert Customer.objects.filter(name='Updated Customer Name').exists()

    def test_customer_update_as_analyst_in_org(self, client, analyst_user, customer):
        """Test that an analyst within the organization cannot update a customer."""
        client.force_authenticate(user=analyst_user)
        url = reverse('customer-detail', args=[customer.pk])
        data = {'name': 'Updated Customer Name'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_update_as_analyst_outside_org(self, client, another_organization_analyst_user, customer):
        """Test that an analyst outside the organization cannot update a customer."""
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('customer-detail', args=[customer.pk])
        data = {'name': 'Updated Customer Name'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_update_as_agent_in_org(self, client, agent_user, customer):
        """Test that an agent within the organization cannot update a customer."""
        client.force_authenticate(user=agent_user)
        url = reverse('customer-detail', args=[customer.pk])
        data = {'name': 'Updated Customer Name'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_update_as_agent_outside_org(self, client, another_organization_agent_user, customer):
        """Test that an agent outside the organization cannot update a customer."""
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('customer-detail', args=[customer.pk])
        data = {'name': 'Updated Customer Name'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_update_as_unauthenticated_user(self, client, customer):
        """Test that an unauthenticated user cannot update a customer."""
        url = reverse('customer-detail', args=[customer.pk])
        data = {'name': 'Updated Customer Name'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCustomerDelete:
    """Tests for the deletion of existing Customer instances"""

    def test_customer_delete_as_superuser(self, client, superuser, customer):
        """Test that a superuser can delete a customer."""
        client.force_authenticate(user=superuser)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_customer_delete_as_analyst_in_org(self, client, analyst_user, customer):
        """Test that an analyst within the organization cannot delete a customer."""
        client.force_authenticate(user=analyst_user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_delete_as_analyst_outside_org(self, client, another_organization_analyst_user, customer):
        """Test that an analyst outside the organization cannot delete a customer."""
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_delete_as_agent_in_org(self, client, agent_user, customer):
        """Test that an agent within the organization cannot delete a customer."""
        client.force_authenticate(user=agent_user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_delete_as_agent_outside_org(self, client, another_organization_agent_user, customer):
        """Test that an agent outside the organization cannot delete a customer."""
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_delete_as_unauthenticated_user(self, client, customer):
        """Test that an unauthenticated user cannot delete a customer."""
        url = reverse('customer-detail', args=[customer.pk])
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCustomerActions:
    """Test the ViewSet actions for viewing a Customer's activity trends and conversation summary"""

    def test_customer_trend_actions_as_superuser(self, client, superuser, customer):
        """Test that a superuser can access trend actions for a customer."""
        client.force_authenticate(user=superuser)
        for action in TREND_ACTIONS:
            url = reverse(f'customer-{action}', args=[customer.pk])
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK

    def test_customer_trend_actions_as_analyst_in_org(self, client, analyst_user, customer):
        """Test that an analyst within the organization can access trend actions for a customer."""
        client.force_authenticate(user=analyst_user)
        for action in TREND_ACTIONS:
            url = reverse(f'customer-{action}', args=[customer.pk])
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK

    def test_customer_trend_actions_as_analyst_outside_org(self, client, another_organization_analyst_user, customer):
        """Test that an analyst outside the organization cannot access trend actions for a customer."""
        client.force_authenticate(user=another_organization_analyst_user)
        for action in TREND_ACTIONS:
            url = reverse(f'customer-{action}', args=[customer.pk])
            response = client.get(url)
            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_customer_trend_actions_as_agent_in_org(self, client, agent_user, customer):
        """Test that an agent within the organization can access trend actions for a customer."""
        client.force_authenticate(user=agent_user)
        for action in TREND_ACTIONS:
            url = reverse(f'customer-{action}', args=[customer.pk])
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK

    def test_customer_trend_actions_as_agent_outside_org(self, client, another_organization_agent_user, customer):
        """Test that an agent outside the organization cannot access trend actions for a customer."""
        client.force_authenticate(user=another_organization_agent_user)
        for action in TREND_ACTIONS:
            url = reverse(f'customer-{action}', args=[customer.pk])
            response = client.get(url)
            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_customer_trend_actions_as_unauthenticated_user(self, client, customer):
        """Test that an unauthenticated user cannot access trend actions for a customer."""
        for action in TREND_ACTIONS:
            url = reverse(f'customer-{action}', args=[customer.pk])
            response = client.get(url)
            assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_conversations_action_returns_expected_content(self, client, agent_user, customer, conversation):
        """
        Test that the 'conversations' action for a customer retrieves the expected conversation data.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('customer-conversations', args=[customer.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['title'] == conversation.title

    def test_customer_conversation_trend_action_returns_expected_content(self, client, agent_user, customer,
                                                                         conversation):
        """
        Test that the 'conversation_trend' action for an agent retrieves the expected conversation data.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('customer-conversation-trend', args=[customer.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['count'] == 1
        assert results[0]['date'] == conversation.date

    def test_customer_conversation_topic_trend_action_returns_expected_content(self, client, agent_user, customer,
                                                                               conversation):
        """
        Test that the 'conversation_topic_trend' action for a customer retrieves the expected conversation data.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('customer-conversation-topic-trend', args=[customer.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['count'] == 1
        assert results[0]['date'] == conversation.date
        assert results[0]['topic'] == str(conversation.topics.all()[0])

    def test_customer_duration_trend_action_returns_expected_content(self, client, agent_user, customer, conversation):
        """
        Test that the 'duration-trend' action for a customer retrieves the expected duration trend data.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('customer-duration-trend', args=[customer.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['avg_value'] == conversation.duration

    def test_customer_sentiment_trend_action_returns_expected_content(self, client, agent_user, customer, conversation):
        """
        Test that the 'sentiment-trend' action for a customer retrieves the expected sentiment trend data.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('customer-sentiment-trend', args=[customer.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['avg_value'] == conversation.sentiment

    def test_customer_summary_data_returns_expected_content(self, client, agent_user, customer, conversation):
        """
        Test that the 'summary-data' action for a customer retrieves the expected summary data.
        """
        with patch('call_miner.models.condense_summaries') as mock_condense_summaries:
            mock_condense_summaries.return_value = 'Mocked summary text'
            client.force_authenticate(user=agent_user)
            url = reverse('customer-summary-data', args=[customer.id])
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert 'summary' in response.data
            assert response.data['summary'] == 'Mocked summary text'

    def test_customer_search_by_name(self, client, agent_user, customer):
        """
        Test that the search action on a customer name behaves as expected
        """
        client.force_authenticate(user=agent_user)
        search_query = customer.name
        url = reverse('customer-search') + f'?query={search_query}'
        all_results = []
        while url:
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK
            data = response.data
            results = data.get('results', [])
            all_results.extend(results)
            url = data.get('next')

        customer_ids = [cust['url'].rstrip('/').split('/')[-1] for cust in all_results]

        assert len(all_results) == 1
        assert str(customer.id) in customer_ids

    def test_customer_search_no_results(self, client, analyst_user):
        """
        Test the expected response when a query produces no results
        """
        client.force_authenticate(user=analyst_user)
        search_query = "agrearhadfgsdfgfdsgdfg"
        url = reverse('customer-search') + f'?query={search_query}'
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == 'Your query produced no results.'

