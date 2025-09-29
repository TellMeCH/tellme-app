import pytest
import zoneinfo
from datetime import datetime, timedelta
from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from tellme.call_miner.models import Customer, Conversation

TREND_ACTIONS = ['conversations', 'trend', 'summary-data']


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
        assert response.data['results'][0]['external_id'] == customer.external_id

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
        assert response.data['results'][0]['external_id'] == another_organization_customer.external_id

    def test_customer_list_as_agent_in_org(self, client, agent_user, customer):
        """Test that an agent within the organization can list customers in their organization."""
        client.force_authenticate(user=agent_user)
        url = reverse('customer-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['external_id'] == customer.external_id

    def test_customer_list_as_agent_outside_org(self, client, another_organization_agent_user,
                                                another_organization_customer):
        """Test that an agent outside the organization sees only their own organization's customers."""
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('customer-list')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['external_id'] == another_organization_customer.external_id

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
        assert response.data['external_id'] == customer.external_id

    def test_customer_retrieve_as_analyst_in_org(self, client, analyst_user, customer):
        """Test that an analyst within the organization can retrieve a customer."""
        client.force_authenticate(user=analyst_user)
        url = reverse('customer-detail', args=[customer.pk])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['external_id'] == customer.external_id

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
        assert response.data['external_id'] == customer.external_id

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

    def test_customer_conversation_stats(self, client, organization_admin_user, conversation, agent, customer, topic):
        """
        Test that the conversation stats for the customer are as expected
        """
        client.force_authenticate(user=organization_admin_user)
        url = reverse('customer-detail', args=[customer.id])
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "conversation_count" in response.data
        assert "first_conversation_date" in response.data
        assert "last_conversation_date" in response.data
        assert response.data.get("conversation_count") == 1
        assert response.data.get("first_conversation_date") == conversation.date.isoformat()[:-6] + 'Z'
        assert response.data.get("last_conversation_date") == conversation.date.isoformat()[:-6] + 'Z'



@pytest.mark.django_db
class TestCustomerCreate:
    """Test the creation of a new Customer instance"""

    def test_customer_create_as_superuser(self, client, superuser, organization):
        """Test that a superuser can create a new customer."""
        client.force_authenticate(user=superuser)
        url = reverse('customer-list')
        data = {
            'external_id': '8cf7b5784836b86e69e4d601a8d111efd75812873a746bbc162244109f2fbf84',
            'organization': organization.pk
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Customer.objects.filter(
            external_id='8cf7b5784836b86e69e4d601a8d111efd75812873a746bbc162244109f2fbf84'
        ).exists()

    def test_customer_create_as_analyst_in_org(self, client, analyst_user, organization):
        """Test that an analyst within the organization cannot create a new customer."""
        client.force_authenticate(user=analyst_user)
        url = reverse('customer-list')
        data = {
            'external_id': '8cf7b5784836b86e69e4d601a8d111efd75812873a746bbc162244109f2fbf84',
            'organization': organization.pk
        }
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_create_as_analyst_outside_org(self, client, another_organization_analyst_user, organization):
        """Test that an analyst outside the organization cannot create a customer in another organization."""
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('customer-list')
        data = {'external_id': '8cf7b5784836b86e69e4d601a8d111efd75812873a746bbc162244109f2fbf84',
                'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_create_as_agent_in_org(self, client, agent_user, organization):
        """Test that an agent within the organization cannot create a new customer."""
        client.force_authenticate(user=agent_user)
        url = reverse('customer-list')
        data = {'external_id': '8cf7b5784836b86e69e4d601a8d111efd75812873a746bbc162244109f2fbf84',
                'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_create_as_agent_outside_org(self, client, another_organization_agent_user, organization):
        """Test that an agent outside the organization cannot create a customer in another organization."""
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('customer-list')
        data = {'external_id': '8cf7b5784836b86e69e4d601a8d111efd75812873a746bbc162244109f2fbf84',
                'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_create_as_unauthenticated_user(self, client, organization):
        """Test that an unauthenticated user cannot create a customer."""
        url = reverse('customer-list')
        data = {'external_id': '8cf7b5784836b86e69e4d601a8d111efd75812873a746bbc162244109f2fbf84',
                'organization': organization.pk}
        response = client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCustomerUpdate:
    """Tests for the update of existing Customer instances."""

    def test_customer_update_as_superuser(self, client, superuser, customer):
        """Test that a superuser can update a customer."""
        client.force_authenticate(user=superuser)
        url = reverse('customer-detail', args=[customer.pk])
        data = {'external_id': '8cf7b5784836b86e69e4d601a8d111efd75812873a746bbc162244109f2fbf84'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert Customer.objects.filter(external_id='8cf7b5784836b86e69e4d601a8d111efd75812873a746bbc162244109f2fbf84').exists()

    def test_customer_update_as_analyst_in_org(self, client, analyst_user, customer):
        """Test that an analyst within the organization cannot update a customer."""
        client.force_authenticate(user=analyst_user)
        url = reverse('customer-detail', args=[customer.pk])
        data = {'external_id': '8cf7b5784836b86e69e4d601a8d111efd75812873a746bbc162244109f2fbf84'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_update_as_analyst_outside_org(self, client, another_organization_analyst_user, customer):
        """Test that an analyst outside the organization cannot update a customer."""
        client.force_authenticate(user=another_organization_analyst_user)
        url = reverse('customer-detail', args=[customer.pk])
        data = {'external_id': '8cf7b5784836b86e69e4d601a8d111efd75812873a746bbc162244109f2fbf84'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_update_as_agent_in_org(self, client, agent_user, customer):
        """Test that an agent within the organization cannot update a customer."""
        client.force_authenticate(user=agent_user)
        url = reverse('customer-detail', args=[customer.pk])
        data = {'external_id': '8cf7b5784836b86e69e4d601a8d111efd75812873a746bbc162244109f2fbf84'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_update_as_agent_outside_org(self, client, another_organization_agent_user, customer):
        """Test that an agent outside the organization cannot update a customer."""
        client.force_authenticate(user=another_organization_agent_user)
        url = reverse('customer-detail', args=[customer.pk])
        data = {'external_id': '8cf7b5784836b86e69e4d601a8d111efd75812873a746bbc162244109f2fbf84'}
        response = client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_customer_update_as_unauthenticated_user(self, client, customer):
        """Test that an unauthenticated user cannot update a customer."""
        url = reverse('customer-detail', args=[customer.pk])
        data = {'external_id': '8cf7b5784836b86e69e4d601a8d111efd75812873a746bbc162244109f2fbf84'}
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
        Test that the 'trend' action for an agent retrieves the expected conversation data.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('customer-trend', args=[customer.id])
        response = client.get(url, {'trend_period': 'daily', 'field': 'count'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['count'] == 1
        assert results[0]['date'] == conversation.date

    def test_customer_conversation_topic_trend_action_returns_expected_content(self, client, agent_user, customer,
                                                                               conversation):
        """
        Test that the 'trend' action for a customer retrieves the expected conversation data per topic.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('customer-trend', args=[customer.id])
        response = client.get(url, {'trend_period': 'daily', 'field': 'count', 'per_topic': 'true'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['count'] == 1
        assert results[0]['date'] == conversation.date
        assert results[0]['topic_name'] == str(conversation.topics.all()[0])
        assert 'topic_id' in results[0]

    def test_customer_duration_trend_action_returns_expected_content(self, client, agent_user, customer, conversation):
        """
        Test that the 'trend' action for a customer retrieves the expected duration trend data.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('customer-trend', args=[customer.id])
        response = client.get(url, {'trend_period': 'daily', 'field': 'duration'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['avg_duration'] == conversation.duration

    def test_customer_sentiment_trend_action_returns_expected_content(self, client, agent_user, customer, conversation):
        """
        Test that the 'trend' action for a customer retrieves the expected sentiment trend data.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('customer-trend', args=[customer.id])
        response = client.get(url, {'trend_period': 'daily', 'field': 'sentiment'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['avg_sentiment'] == conversation.sentiment

    def test_customer_revenue_trend_action_returns_expected_content(self, client, agent_user, customer, conversation):
        """
        Test that the 'trend' action for a customer retrieves the expected revenue trend data.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('customer-trend', args=[customer.id])
        response = client.get(url, {'trend_period': 'daily', 'field': 'revenue'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['avg_revenue'] == conversation.revenue_at_stake

    def test_customer_sentiment_per_topic_trend_action_returns_expected_content(self, client, agent_user, customer,
                                                                                conversation):
        """
        Test that the 'trend' action for a customer retrieves the expected sentiment trend data.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('customer-trend', args=[customer.id])
        response = client.get(url, {'trend_period': 'daily', 'field': 'sentiment', 'per_topic': 'true'})
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['avg_sentiment'] == conversation.sentiment
        assert results[0]['topic_name'] == str(conversation.topics.all()[0])
        assert 'topic_id' in results[0]

    def test_customer_summary_data_returns_expected_content(self, client, agent_user, customer, conversation_today):
        """
        Test that the 'summary-data' action for a customer retrieves the expected summary data.
        """
        with patch('tellme.call_miner.models.condense_summaries') as mock_condense_summaries:
            mock_condense_summaries.return_value = 'Mocked summary text'
            client.force_authenticate(user=agent_user)
            url = reverse('customer-summary-data', args=[customer.id])
            response = client.get(url)
            assert response.status_code == status.HTTP_200_OK
            assert 'summary' in response.data
            assert response.data['summary'] == 'Mocked summary text'
            assert 'period_label' in response.data
            assert response.data['period_label'] == 'Rolling90D'

            for period in ['week', 'month', 'quarter']:
                for rolling in [True, False]:
                    response = client.get(url, {'period': period, 'rolling': rolling})
                    assert response.status_code == status.HTTP_200_OK
                    assert 'summary' in response.data
                    assert response.data['summary'] == 'Mocked summary text'
                    assert 'period_label' in response.data
                    if rolling:
                        days = {'week': 7, 'month': 30, 'quarter': 90}
                        label = f'Rolling{days[period]}D'
                    else:
                        today = datetime.today()
                        if period == 'week':
                            label = today.strftime("%G-W%V")
                        elif period == 'month':
                            label = today.strftime("%Y-%m")
                        else:
                            label = f"{today.year}-Q{((today.month - 1) // 3) + 1}"
                    assert response.data['period_label'] == label

    def test_all_summaries_respects_minimum_call_count_and_period(
            self, client, organization_admin_user, agent, customer, topic, conversation_today
    ):
        """
        • customer (with 1 call) → add a 2nd call so it qualifies
        • low_customer  (1 call) → should be filtered out
        • zero_customer (0 call) → should be filtered out
        • period label must be quarterly
        """
        # make qualifying 2nd conversation for 'customer'
        utc = zoneinfo.ZoneInfo("UTC")
        Conversation.objects.create(
            path="2nd",
            date=datetime.now(tz=utc) - timedelta(hours=1),
            duration=60,
            title="2nd",
            summary="x",
            transcript="t",
            sentiment=4.2,
            agent=agent,
            customer=customer,
            input_tokens=10,
            output_tokens=5,
        ).topics.add(topic)

        # low-customer: only 1 conversation
        low_customer = Customer.objects.create(
            external_id="low123",
            organization=customer.organization,
        )
        Conversation.objects.create(
            path="low",
            date=datetime.now(tz=utc),
            duration=30,
            title="low",
            summary="x",
            transcript="t",
            sentiment=3.5,
            agent=agent,
            customer=low_customer,
            input_tokens=10,
            output_tokens=5,
        ).topics.add(topic)

        # customer with zero calls
        zero_customer = Customer.objects.create(
            external_id="zero123",
            organization=customer.organization,
        )

        client.force_authenticate(user=organization_admin_user)
        resp = client.get(reverse("customer-all-summaries"))
        assert resp.status_code == status.HTTP_200_OK

        data = resp.data
        # qualifying customer included
        assert customer.id in data
        # others excluded
        assert low_customer.id not in data
        assert zero_customer.id not in data

        # correct period label (quarter)
        assert data[customer.id]["period_label"] == 'Rolling90D'
