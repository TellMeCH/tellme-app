import pytest
import zoneinfo
from urllib.parse import urlparse, parse_qs
from django.utils import timezone
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from tellme.call_miner.models import Customer, Conversation, PeriodSummary
from tellme.call_miner.utils.period_utils import period_bounds

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
        assert 'total_revenue' in response.data['results'][0]
        assert response.data['results'][0]['total_revenue'] == 0.0

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

    def test_customer_list_ordering_allowed_fields(self, client, analyst_user, customer, agent):
        """Test that all allowed ordering fields work correctly and aggregated values are computed"""

        # Create conversations with different values for testing aggregated fields
        base_date = timezone.now()

        # Create conversations for the customer
        Conversation.objects.create(
            path="test1.mp3",
            date=base_date - timedelta(days=1),
            duration=300.0,
            transcript="Test transcript 1",
            sentiment=4.0,
            summary="Summary 1",
            title="Title 1",
            input_tokens=100,
            output_tokens=50,
            revenue_at_stake=1000.0,
            customer=customer,
            agent=agent,
            resolved=True
        )

        Conversation.objects.create(
            path="test2.mp3",
            date=base_date,
            duration=450.0,
            transcript="Test transcript 2",
            sentiment=2.0,
            summary="Summary 2",
            title="Title 2",
            input_tokens=120,
            output_tokens=60,
            revenue_at_stake=500.0,
            customer=customer,
            agent=agent,
            resolved=False
        )

        client.force_authenticate(user=analyst_user)
        allowed_fields = ['last_conversation_date', 'conversation_count', 'created', 'total_revenue', 'avg_sentiment']

        for field in allowed_fields:
            # Test ascending
            response = client.get(reverse('customer-list'), {'ordering': field})
            assert response.status_code == status.HTTP_200_OK, f"Failed for field: {field}"

            # Test descending
            response = client.get(reverse('customer-list'), {'ordering': f'-{field}'})
            assert response.status_code == status.HTTP_200_OK, f"Failed for field: -{field}"

        # Verify aggregated values are present and correct
        response = client.get(reverse('customer-list'))
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert len(results) >= 1

        customer_data = results[0]
        assert 'total_revenue' in customer_data
        assert 'avg_sentiment' in customer_data

        # Verify the aggregated values are correct
        assert customer_data['total_revenue'] == 1500.0  # 1000 + 500
        assert customer_data['avg_sentiment'] == 3.0      # (4.0 + 2.0) / 2

    def test_customer_list_ordering_invalid_field(self, client, analyst_user, customer):
        """Test that ordering by invalid fields is ignored and default ordering is applied"""
        client.force_authenticate(user=analyst_user)

        # Get response with invalid ordering
        invalid_response = client.get(reverse('customer-list'), {'ordering': 'invalid_field'})
        assert invalid_response.status_code == status.HTTP_200_OK

        # Get response with default ordering
        default_response = client.get(reverse('customer-list'))
        assert default_response.status_code == status.HTTP_200_OK

        # Results should be the same (invalid ordering ignored, default applied)
        assert invalid_response.data == default_response.data

    def test_customer_list_no_ordering_parameter(self, client, analyst_user, customer):
        """Test that default ordering is applied when no ordering parameter is provided"""
        client.force_authenticate(user=analyst_user)
        response = client.get(reverse('customer-list'))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_customer_list_cursor_with_different_ordering_limitation(self, client, analyst_user, customer, agent):
        """Test that cursor pagination with different ordering has limitations"""

        # Create additional customers to enable pagination
        base_date = timezone.now()
        for i in range(3):
            Customer.objects.create(
                organization=customer.organization,
                external_id=f"test_customer_{i}",
                created=base_date - timedelta(days=i)
            )

        client.force_authenticate(user=analyst_user)

        # Get first page ordered by created date
        created_response = client.get(reverse('customer-list'), {
            'ordering': 'created',
            'page_size': 2  # Force pagination
        })
        assert created_response.status_code == status.HTTP_200_OK

        # Extract cursor
        next_url = created_response.data.get('next')
        parsed_url = urlparse(next_url)
        cursor_params = parse_qs(parsed_url.query)
        cursor = cursor_params.get('cursor', [None])[0]

        # Try to use cursor with same ordering
        response = client.get(reverse('customer-list'), {
            'ordering': 'created',
            'cursor': cursor
        })

        assert response.status_code == status.HTTP_200_OK

        # Try to use cursor with different ordering - should raise an error
        with pytest.raises((ValueError, Exception)):
            response = client.get(reverse('customer-list'), {
                'ordering': 'total_revenue',
                'cursor': cursor
            })

    def test_customer_latest_conversation_tracking(self, customer, agent):
        """Test that latest_conversation and latest_conversation_title are properly tracked"""
        # Initially, customer should have no conversations
        assert customer.latest_conversation is None
        assert customer.latest_conversation_title is None
        assert customer.conversation_count == 0

        # Create first conversation
        base_date = timezone.now()
        conv1 = Conversation.objects.create(
            path="test1.mp3",
            date=base_date - timedelta(days=2),
            duration=300.0,
            transcript="Test transcript 1",
            sentiment=3.0,
            summary="Summary 1",
            title="First Conversation",
            input_tokens=100,
            output_tokens=50,
            customer=customer,
            agent=agent
        )

        # Refresh customer from DB to get updated stats
        customer.refresh_from_db()
        assert customer.latest_conversation == conv1
        assert customer.latest_conversation_title == "First Conversation"
        assert customer.conversation_count == 1

        # Create second conversation with later date
        conv2 = Conversation.objects.create(
            path="test2.mp3",
            date=base_date - timedelta(days=1),
            duration=450.0,
            transcript="Test transcript 2",
            sentiment=4.0,
            summary="Summary 2",
            title="Second Conversation",
            input_tokens=120,
            output_tokens=60,
            customer=customer,
            agent=agent
        )

        # Refresh and check latest conversation is now conv2
        customer.refresh_from_db()
        assert customer.latest_conversation == conv2
        assert customer.latest_conversation_title == "Second Conversation"
        assert customer.conversation_count == 2

        # Create third conversation with earliest date
        conv3 = Conversation.objects.create(
            path="test3.mp3",
            date=base_date - timedelta(days=3),
            duration=200.0,
            transcript="Test transcript 3",
            sentiment=2.5,
            summary="Summary 3",
            title="Third Conversation",
            input_tokens=80,
            output_tokens=40,
            customer=customer,
            agent=agent
        )

        # Latest conversation should still be conv2 (most recent date)
        customer.refresh_from_db()
        assert customer.latest_conversation == conv2
        assert customer.latest_conversation_title == "Second Conversation"
        assert customer.conversation_count == 3

        # Delete the latest conversation
        conv2.delete()

        # Latest should now be conv1
        customer.refresh_from_db()
        assert customer.latest_conversation == conv1
        assert customer.latest_conversation_title == "First Conversation"
        assert customer.conversation_count == 2

        # Delete all conversations
        conv1.delete()
        conv3.delete()

        # Should be back to no conversations
        customer.refresh_from_db()
        assert customer.latest_conversation is None
        assert customer.latest_conversation_title is None
        assert customer.conversation_count == 0


@pytest.mark.django_db
class TestCustomerSearch:
    """Tests for the customer search functionality"""

    @staticmethod
    def response_from_search_url(client, search_query: str):
        """
        Helper method to fetch all paginated results given a search query

        :param client: The APIClient instance.
        :param search_query: Search query to construct the first URL from.
        :return: A list containing all results from all pages.
        """
        all_results = []
        next_url = reverse('customer-search') + f'?query={search_query}'
        while next_url:
            response = client.get(next_url)
            assert response.status_code == status.HTTP_200_OK
            data = response.data
            results = data.get('results', [])
            all_results.extend(results)
            next_url = data.get('next')
        return all_results

    def test_search_by_first_name(self, client, analyst_user, customer, conversation):
        """
        Test that customers can be searched and retrieved based on their first name.
        """
        client.force_authenticate(user=analyst_user)
        search_query = customer.first_name
        results = self.response_from_search_url(client, search_query)
        customer_ids = [cust['url'].rstrip('/').split('/')[-1] for cust in results]

        assert len(results) >= 1
        assert str(customer.id) in customer_ids

    def test_search_by_last_name(self, client, analyst_user, customer, conversation):
        """
        Test that customers can be searched and retrieved based on their last name.
        """
        client.force_authenticate(user=analyst_user)
        search_query = customer.last_name
        results = self.response_from_search_url(client, search_query)
        customer_ids = [cust['url'].rstrip('/').split('/')[-1] for cust in results]

        assert len(results) >= 1
        assert str(customer.id) in customer_ids

    def test_search_by_latest_conversation_title(self, client, analyst_user, customer, conversation):
        """
        Test that customers can be searched and retrieved based on their latest conversation title.
        """
        client.force_authenticate(user=analyst_user)
        search_query = conversation.title
        results = self.response_from_search_url(client, search_query)
        customer_ids = [cust['url'].rstrip('/').split('/')[-1] for cust in results]

        assert len(results) >= 1
        assert str(customer.id) in customer_ids

    def test_search_by_conversation_transcript_content(self, client, analyst_user, customer, conversation):
        """
        Test that customers can be searched and retrieved based on content in their conversation transcripts.
        """
        client.force_authenticate(user=analyst_user)
        search_query = "strange noise"  # This text exists in the conversation transcript
        results = self.response_from_search_url(client, search_query)
        customer_ids = [cust['url'].rstrip('/').split('/')[-1] for cust in results]

        assert len(results) >= 1
        assert str(customer.id) in customer_ids

    def test_search_no_duplicates_in_results(self, client, analyst_user, customer, agent, conversation):
        """
        Test that customers resulting from a query do not contain duplicates,
        even when multiple customers match the search query.
        """
        # Ensure the main customer has a conversation (from conversation fixture)
        customer.refresh_from_db()

        # Create additional customers with similar names and conversations to test deduplication
        utc = zoneinfo.ZoneInfo("UTC")
        test_date = datetime.now(tz=utc)

        customer2 = Customer.objects.create(
            first_name='Edward',
            last_name='Johnson',
            external_id='different_id_1',
            organization=customer.organization
        )
        Conversation.objects.create(
            path='path/to/customer2_conv',
            date=test_date,
            duration=120,
            title='Customer 2 Conversation',
            summary='Test conversation',
            transcript='Test transcript',
            sentiment=3.0,
            agent=agent,
            customer=customer2,
            input_tokens=100,
            output_tokens=50
        )

        customer3 = Customer.objects.create(
            first_name='Edward',
            last_name='Brown',
            external_id='different_id_2',
            organization=customer.organization
        )
        Conversation.objects.create(
            path='path/to/customer3_conv',
            date=test_date,
            duration=120,
            title='Customer 3 Conversation',
            summary='Test conversation',
            transcript='Test transcript',
            sentiment=3.0,
            agent=agent,
            customer=customer3,
            input_tokens=100,
            output_tokens=50
        )

        client.force_authenticate(user=analyst_user)
        # Search by first name which should match all three Edwards
        search_query = customer.first_name  # "Edward"
        results = self.response_from_search_url(client, search_query)
        customer_ids = [cust['url'].rstrip('/').split('/')[-1] for cust in results]

        # Verify no duplicate customer IDs in results
        assert len(customer_ids) == len(set(customer_ids))
        # Should return 3 unique customers named Edward
        assert len(results) == 3
        assert str(customer.id) in customer_ids

    def test_search_no_results(self, client, analyst_user):
        """
        Test the expected response when a query produces no results
        """
        client.force_authenticate(user=analyst_user)
        search_query = "agrearhadfgsdfgfdsgdfg"
        url = reverse('customer-search') + f'?query={search_query}'
        response = client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data['detail'] == 'No results.'

    def test_search_with_ordering_by_total_revenue(self, client, analyst_user, agent, organization):
        """
        Test that search results can be ordered by total_revenue when ordering parameter is provided.
        """

        # Create customers with different revenue values but same searchable content
        low_revenue_customer = Customer.objects.create(
            first_name='TestCustomer',
            last_name='LowRevenue',
            external_id='low_revenue_customer',
            organization=organization
        )

        high_revenue_customer = Customer.objects.create(
            first_name='TestCustomer',
            last_name='HighRevenue',
            external_id='high_revenue_customer',
            organization=organization
        )

        utc = zoneinfo.ZoneInfo("UTC")
        test_date = datetime(2024, 3, 15, 10, 0, 0, tzinfo=utc)

        # Create conversations with different revenue amounts
        Conversation.objects.create(
            path='path/to/low_revenue_conv',
            date=test_date,
            duration=120,
            title='Low Revenue Conversation',
            summary='Revenue ordering test conversation',
            transcript='This conversation has low revenue at stake',
            sentiment=3.0,
            starting_sentiment=3.0,
            ending_sentiment=3.0,
            agent=agent,
            customer=low_revenue_customer,
            input_tokens=100,
            output_tokens=50,
            revenue_at_stake=100.0,
            resolved=True
        )

        Conversation.objects.create(
            path='path/to/high_revenue_conv',
            date=test_date,
            duration=180,
            title='High Revenue Conversation',
            summary='Revenue ordering test conversation',
            transcript='This conversation has high revenue at stake',
            sentiment=4.0,
            starting_sentiment=4.0,
            ending_sentiment=4.0,
            agent=agent,
            customer=high_revenue_customer,
            input_tokens=150,
            output_tokens=75,
            revenue_at_stake=1000.0,
            resolved=False
        )

        client.force_authenticate(user=analyst_user)
        search_query = "TestCustomer"

        # Test ordering by total_revenue ascending
        url = reverse('customer-search') + f'?query={search_query}&ordering=total_revenue'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert len(results) >= 2

        # Find our test customers in results
        result_ids = [cust['url'].rstrip('/').split('/')[-1] for cust in results]
        low_index = next(i for i, id in enumerate(result_ids) if id == str(low_revenue_customer.id))
        high_index = next(i for i, id in enumerate(result_ids) if id == str(high_revenue_customer.id))

        # Low revenue customer should come first (ascending order)
        assert low_index < high_index

        # Test ordering by total_revenue descending
        url = reverse('customer-search') + f'?query={search_query}&ordering=-total_revenue'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']

        result_ids = [cust['url'].rstrip('/').split('/')[-1] for cust in results]
        low_index = next(i for i, id in enumerate(result_ids) if id == str(low_revenue_customer.id))
        high_index = next(i for i, id in enumerate(result_ids) if id == str(high_revenue_customer.id))

        # High revenue customer should come first (descending order)
        assert high_index < low_index

    def test_search_without_ordering_uses_relevance(self, client, analyst_user, agent, organization):
        """
        Test that search results without ordering parameter are ordered by relevance (-rank).
        """

        # Create customers where name relevance differs
        high_relevance_customer = Customer.objects.create(
            first_name='RelevanceTest',
            last_name='RelevanceTest', # Name appears multiple times
            external_id='high_relevance_customer',
            organization=organization
        )

        low_relevance_customer = Customer.objects.create(
            first_name='Different',
            last_name='Name',
            external_id='low_relevance_customer',
            organization=organization
        )

        utc = zoneinfo.ZoneInfo("UTC")
        test_date = datetime(2024, 5, 15, 10, 0, 0, tzinfo=utc)

        # Create conversations - high relevance customer has conversation with keyword in title
        Conversation.objects.create(
            path='path/to/high_rel_conv',
            date=test_date,
            duration=120,
            title='RelevanceTest conversation with RelevanceTest keyword multiple times',
            summary='This summary contains RelevanceTest keyword',
            transcript='This transcript has RelevanceTest keyword many times',
            sentiment=3.0,
            starting_sentiment=3.0,
            ending_sentiment=3.0,
            agent=agent,
            customer=high_relevance_customer,
            input_tokens=100,
            output_tokens=50,
            revenue_at_stake=200.0,
            resolved=True
        )

        # Low relevance customer has conversation with keyword appearing less frequently
        Conversation.objects.create(
            path='path/to/low_rel_conv',
            date=test_date,
            duration=180,
            title='Different conversation',
            summary='Different summary',
            transcript='This transcript mentions RelevanceTest once',
            sentiment=4.0,
            starting_sentiment=4.0,
            ending_sentiment=4.0,
            agent=agent,
            customer=low_relevance_customer,
            input_tokens=150,
            output_tokens=75,
            revenue_at_stake=300.0,
            resolved=False
        )

        client.force_authenticate(user=analyst_user)
        search_query = "RelevanceTest"

        # Test search without ordering (should use relevance)
        url = reverse('customer-search') + f'?query={search_query}'
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']

        result_ids = [cust['url'].rstrip('/').split('/')[-1] for cust in results]
        high_index = next(i for i, id in enumerate(result_ids) if id == str(high_relevance_customer.id))
        low_index = next(i for i, id in enumerate(result_ids) if id == str(low_relevance_customer.id))

        # High relevance customer should come first (higher rank)
        assert high_index < low_index

    def test_search_without_query_returns_all_customers(self, client, analyst_user, customer, conversation):
        """
        Test that search endpoint without a query parameter returns all customers in the basic queryset.
        The customer must have at least one conversation to appear in search results.
        """
        client.force_authenticate(user=analyst_user)
        url = reverse('customer-search')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

        # Verify the customer is in the results
        customer_ids = [cust['url'].rstrip('/').split('/')[-1] for cust in response.data['results']]
        assert str(customer.id) in customer_ids

    def test_search_only_returns_customers_with_conversations(self, client, analyst_user, customer, organization, agent, conversation):
        """
        Test that search endpoint only returns customers with at least one conversation,
        excluding customers with zero conversations.
        """
        # Create a customer with no conversations
        customer_no_conversations = Customer.objects.create(
            first_name='NoConversations',
            last_name='Customer',
            external_id='no_conv_customer',
            organization=organization
        )

        # Ensure customer fixture has a conversation (from the conversation fixture)
        customer.refresh_from_db()
        assert customer.conversation_count >= 1
        # Verify new customer has no conversations
        assert customer_no_conversations.conversation_count == 0

        client.force_authenticate(user=analyst_user)

        # Test search with no query
        url = reverse('customer-search')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

        customer_ids = [cust['url'].rstrip('/').split('/')[-1] for cust in response.data['results']]

        # Customer with conversations should be included
        assert str(customer.id) in customer_ids
        # Customer without conversations should be excluded
        assert str(customer_no_conversations.id) not in customer_ids

        # Test search with a query that matches both customers' names
        # Search for the main customer's last name
        url = reverse('customer-search') + f'?query={customer.last_name}'
        response = client.get(url)

        # If the query returns results, verify filtering
        if response.status_code == status.HTTP_200_OK:
            customer_ids = [cust['url'].rstrip('/').split('/')[-1] for cust in response.data['results']]
            # Customer with conversations should be included
            assert str(customer.id) in customer_ids
            # Customer without conversations should be excluded
            assert str(customer_no_conversations.id) not in customer_ids


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
        assert "total_revenue" in response.data
        assert response.data.get("conversation_count") == 1
        assert response.data.get("first_conversation_date") == conversation.date.isoformat()[:-6] + 'Z'
        assert response.data.get("last_conversation_date") == conversation.date.isoformat()[:-6] + 'Z'
        assert response.data.get("total_revenue") == (conversation.revenue_at_stake or 0.0)



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

    def test_customer_deletion_removes_associated_period_summaries(self, customer, conversation_today):
        """
        Test that when a customer is deleted, its associated PeriodSummary instances are also deleted.
        """
        # Link conversation to customer (it's already linked via the conversation fixture)
        conversation_today.customer = customer
        conversation_today.save()

        # Create multiple PeriodSummary instances for the customer
        content_type = ContentType.objects.get_for_model(Customer)
        period_summaries = []

        for period_type in ['week', 'month', 'quarter']:
            start, end, label = period_bounds(period_type, True)
            summary = PeriodSummary.objects.create(
                content_type=content_type,
                object_id=customer.id,
                period_type=period_type,
                period_label=label,
                summary={
                    "Customer Value": f"High value customer for {period_type}",
                    "Engagement Level": "Active",
                    "Satisfaction Score": 4.2
                },
                last_call_at=conversation_today.date,
                call_count=1
            )
            period_summaries.append(summary)

        # Verify PeriodSummary instances exist
        assert PeriodSummary.objects.filter(
            content_type=content_type,
            object_id=customer.id
        ).count() == 3

        # Delete conversations first to avoid PROTECT foreign key constraint
        conversation_today.delete()

        # Delete the customer
        customer_id = customer.id
        customer.delete()

        # Verify all associated PeriodSummary instances are deleted
        assert PeriodSummary.objects.filter(
            content_type=content_type,
            object_id=customer_id
        ).count() == 0

        # Verify the customer itself is deleted
        assert not Customer.objects.filter(id=customer_id).exists()


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
        assert results[0]['total_revenue'] == conversation.revenue_at_stake

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
        Uses actual PeriodSummary objects instead of mocking the old sync logic.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('customer-summary-data', args=[customer.id])
        content_type = ContentType.objects.get_for_model(customer.__class__)

        summary_data = {
            'Favorite Products/Services': 'Premium subscription',
            'Churn Potential': 'Low risk, satisfied customer',
            'Customer Value': 'High value customer'
        }

        # Create PeriodSummary for each combination we'll test
        for period in ['week', 'month', 'quarter', 'eternity']:
            for rolling in [True, False]:
                if not (period == 'eternity' and rolling):
                    start, end, label = period_bounds(period, rolling)

                    PeriodSummary.objects.create(
                        content_type=content_type,
                        object_id=customer.id,
                        period_type=period,
                        period_label=label,
                        summary=summary_data,
                        last_call_at=conversation_today.date,
                        call_count=1
                    )

        # Test default request (customer uses eternity period with rolling=False by default)
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'summary' in response.data
        assert response.data['summary'] == summary_data
        assert 'period_label' in response.data
        assert response.data['status'] == 'ready'

        # Test all period/rolling combinations
        for period in ['week', 'month', 'quarter', 'eternity']:
            for rolling in [True, False]:
                response = client.get(url, {'period': period, 'rolling': rolling})
                assert response.status_code == status.HTTP_200_OK
                assert 'summary' in response.data
                assert response.data['summary'] == summary_data
                assert 'period_label' in response.data
                assert response.data['status'] == 'ready'

                # Verify the correct period label is returned
                # For eternity, rolling is always forced to False
                actual_rolling = False if period == 'eternity' else rolling
                start, end, expected_label = period_bounds(period, actual_rolling)
                assert response.data['period_label'] == expected_label

    def test_customer_summary_data_with_eternity_period(self, client, agent_user, customer, conversation_today):
        """
        Test that the 'summary-data' action for a customer works with 'eternity' period.
        Verifies that the eternity period returns full customer history and ignores rolling parameter.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('customer-summary-data', args=[customer.id])
        content_type = ContentType.objects.get_for_model(customer.__class__)

        summary_data = {
            'Customer Lifetime Value': 'High value customer with consistent engagement',
            'All-Time Favorite Products': 'Premium subscription, Enterprise features',
            'Historical Churn Indicators': 'No significant churn risk over entire history'
        }

        # Create PeriodSummary for eternity period
        start, end, label = period_bounds('eternity', False)

        PeriodSummary.objects.create(
            content_type=content_type,
            object_id=customer.id,
            period_type='eternity',
            period_label=label,
            summary=summary_data,
            last_call_at=conversation_today.date,
            call_count=1
        )

        # Test with eternity period and rolling=False
        response = client.get(url, {'period': 'eternity', 'rolling': False})
        assert response.status_code == status.HTTP_200_OK
        assert 'summary' in response.data
        assert response.data['summary'] == summary_data
        assert response.data['period_label'] == 'eternity'
        assert response.data['status'] == 'ready'

        # Test with eternity period and rolling=True (should be forced to False)
        response = client.get(url, {'period': 'eternity', 'rolling': True})
        assert response.status_code == status.HTTP_200_OK
        assert 'summary' in response.data
        assert response.data['summary'] == summary_data
        assert response.data['period_label'] == 'eternity'
        assert response.data['status'] == 'ready'

    def test_customer_default_summary_uses_eternity(self, client, agent_user, customer, conversation_today):
        """
        Test that the default summary period for customers is 'eternity' with rolling=False.
        """
        client.force_authenticate(user=agent_user)
        url = reverse('customer-summary-data', args=[customer.id])
        content_type = ContentType.objects.get_for_model(customer.__class__)

        summary_data = {
            'Customer Value': 'High value customer'
        }

        # Create PeriodSummary for eternity period (the new default for customers)
        PeriodSummary.objects.create(
            content_type=content_type,
            object_id=customer.id,
            period_type='eternity',
            period_label='eternity',
            summary=summary_data,
            last_call_at=conversation_today.date,
            call_count=1
        )

        # Test default request (should use eternity period for customers)
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'summary' in response.data
        assert response.data['period_label'] == 'eternity'
        assert response.data['status'] == 'ready'

    def test_all_summaries_respects_minimum_call_count_and_period(
            self, client, organization_admin_user, agent, customer, topic, conversation_today
    ):
        """
        Test that all_summaries only includes customers with at least one conversation
        within the summarization period (eternity - new default for customers).
        • customer (with 1 call) → should be included
        • customer_with_multiple (with 2 calls) → should be included
        • zero_customer (0 calls) → should be excluded
        """
        utc = zoneinfo.ZoneInfo("UTC")

        # Create a second customer with multiple conversations
        customer_with_multiple = Customer.objects.create(
            external_id="multi123",
            organization=customer.organization,
        )
        Conversation.objects.create(
            path="multi1",
            date=datetime.now(tz=utc) - timedelta(hours=2),
            duration=60,
            title="multi1",
            summary="x",
            transcript="t",
            sentiment=4.2,
            agent=agent,
            customer=customer_with_multiple,
            input_tokens=10,
            output_tokens=5,
        ).topics.add(topic)

        Conversation.objects.create(
            path="multi2",
            date=datetime.now(tz=utc) - timedelta(hours=1),
            duration=60,
            title="multi2",
            summary="x",
            transcript="t",
            sentiment=4.0,
            agent=agent,
            customer=customer_with_multiple,
            input_tokens=10,
            output_tokens=5,
        ).topics.add(topic)

        # customer with zero calls
        zero_customer = Customer.objects.create(
            external_id="zero123",
            organization=customer.organization,
        )

        # Create pre-existing PeriodSummaries for all customers with "Customer Value" field
        customers_to_create_summaries = [customer, customer_with_multiple, zero_customer]
        # Include 'eternity' as the new default period for customers
        period_types = ['week', 'month', 'quarter', 'eternity']

        content_type = ContentType.objects.get_for_model(Customer)

        for test_customer in customers_to_create_summaries:
            for period_type in period_types:
                # For eternity, always use rolling=False
                rolling = False if period_type == 'eternity' else True
                start, end, label = period_bounds(period_type, rolling)
                PeriodSummary.objects.create(
                    content_type=content_type,
                    object_id=test_customer.id,
                    period_type=period_type,
                    period_label=label,
                    summary={
                        "Customer Value": f"High value customer for {period_type}",
                        "Engagement Level": "Active",
                        "Issues Resolved": 85
                    },
                    last_call_at=datetime.now(tz=zoneinfo.ZoneInfo("UTC")) - timedelta(days=1),
                    call_count=test_customer.conversation_count
                )

        client.force_authenticate(user=organization_admin_user)
        resp = client.get(reverse("customer-all-summaries"))
        assert resp.status_code == status.HTTP_200_OK

        data = resp.data
        # Customers with at least one conversation should be included
        assert customer.id in data
        assert customer_with_multiple.id in data
        # Customer with zero conversations should be excluded
        assert zero_customer.id not in data

        # correct period label (eternity - new default for customers)
        assert data[customer.id]["period_label"] == 'eternity'
        assert data[customer_with_multiple.id]["period_label"] == 'eternity'

    @patch('tellme.call_miner.models.create_ticket_task')
    @patch('tellme.call_miner.models.check_ticket_tasks')
    def test_create_ticket_for_customer_with_summary(
            self, mock_check_ticket_tasks, mock_create_ticket_task,
            client, analyst_user, customer, conversation_today
    ):
        """Test creating a ticket for a customer with existing summary data."""
        # Setup mocks
        mock_check_ticket_tasks.return_value = False
        mock_create_ticket_task.return_value = "task-id-123"

        # Create summary for the customer
        content_type = ContentType.objects.get_for_model(customer.__class__)
        start, end, label = period_bounds('eternity', False)
        summary_data = {
            'Customer Value': 'High value customer',
            'Churn Potential': 'Low risk',
            'Jira Ticket Title': 'Customer Issue - Test',
            'Jira Ticket Body': 'Customer needs attention'
        }
        PeriodSummary.objects.create(
            content_type=content_type,
            object_id=customer.id,
            period_type='eternity',
            period_label=label,
            summary=summary_data,
            last_call_at=conversation_today.date,
            call_count=1
        )

        client.force_authenticate(user=analyst_user)
        url = reverse('customer-create-ticket', args=[customer.id])
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'creating'
        assert response.data['link'] is None
        assert response.data['date'] is None
        mock_create_ticket_task.assert_called_once_with(customer.id, analyst_user.id)

    def test_create_ticket_for_customer_without_conversations(
            self, client, analyst_user, customer
    ):
        """Test that creating a ticket fails when customer has no conversations."""
        client.force_authenticate(user=analyst_user)
        url = reverse('customer-create-ticket', args=[customer.id])
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'no conversations found'

    @patch('tellme.call_miner.models.create_ticket_task')
    @patch('tellme.call_miner.models.check_ticket_tasks')
    def test_get_existing_ticket_for_customer(
            self, mock_check_ticket_tasks, mock_create_ticket_task,
            client, analyst_user, customer, conversation_today
    ):
        """Test getting existing ticket information for a customer."""
        # Create summary for the customer
        content_type = ContentType.objects.get_for_model(customer.__class__)
        start, end, label = period_bounds('eternity', False)
        summary_data = {
            'Customer Value': 'High value customer',
            'Jira Ticket Title': 'Customer Issue',
            'Jira Ticket Body': 'Customer needs help'
        }
        PeriodSummary.objects.create(
            content_type=content_type,
            object_id=customer.id,
            period_type='eternity',
            period_label=label,
            summary=summary_data,
            last_call_at=conversation_today.date,
            call_count=1
        )

        # Set existing ticket information
        customer.ticket_link = "https://jira.example.com/browse/PROJ-123"
        customer.ticket_date = conversation_today.date
        customer.save()

        client.force_authenticate(user=analyst_user)
        url = reverse('customer-create-ticket', args=[customer.id])
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'ready'
        assert response.data['link'] == "https://jira.example.com/browse/PROJ-123"
        assert response.data['date'] == conversation_today.date
        # Should not create a new task if ticket already exists
        mock_create_ticket_task.assert_not_called()
