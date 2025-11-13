import pytest
from unittest.mock import patch
from datetime import datetime
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from tellme.call_miner.models import SuggestedTopic, Topic, Conversation, Organization, Customer, Agent, PeriodSummary
from tellme.call_processing.utils import db_handler
from tellme.call_processing.utils.db_handler import (
    trigger_summarization_tasks, create_periodsummary
)


@pytest.mark.django_db
class TestObtainSuggestedTopics:
    """Test the obtain_suggested_topics function."""
    
    def test_obtain_suggested_topics_with_data(self, setup_db):
        """Test with existing suggested topics."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db
        result = db_handler.obtain_suggested_topics(org.id)
        assert suggested_topic.name in result
        assert suggested_topic.description in result

    def test_obtain_suggested_topics_multiple(self, setup_db):
        """Test with multiple suggested topics."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db
        SuggestedTopic.objects.create(name="Support", description="Customer support calls", organization=org)
        SuggestedTopic.objects.create(name="Billing", description="Billing inquiries", organization=org)
        
        result = db_handler.obtain_suggested_topics(org.id)
        assert "Support" in result
        assert "Billing" in result
        assert "Customer support calls" in result
        assert "Billing inquiries" in result


@pytest.mark.django_db 
class TestCreateSuggestedTopics:
    """Test the create_suggested_topics function."""
    
    def test_create_suggested_topics_basic(self, setup_db):
        """Test creating new suggested topics."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db
        new_topics = [
            {"name": "Test Topic", "description": "A test topic"},
            {"name": "Another Topic", "description": "Another test topic"}
        ]
        initial_count = SuggestedTopic.objects.filter(organization=org).count()

        db_handler.create_suggested_topics(
            new_topics, 
            conversation.path, 
            org.id
        )
        
        # Check topics were created
        final_count = SuggestedTopic.objects.filter(organization=org).count()
        assert final_count == initial_count + 2
        
        # Check topics are linked to conversation
        conversation.refresh_from_db()
        assert conversation.suggested_topics.filter(name="Test Topic").exists()
        assert conversation.suggested_topics.filter(name="Another Topic").exists()
    
    def test_create_suggested_topics_duplicate_names_skipped(self, setup_db):
        """Test that duplicate topic names are skipped."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db
        new_topics = [
            {"name": suggested_topic.name, "description": "Duplicate name"},
            {"name": "New Topic", "description": "This should be created"}
        ]
        initial_count = SuggestedTopic.objects.filter(organization=org).count()
        
        db_handler.create_suggested_topics(
            new_topics,
            conversation.path,
            org.id
        )
        
        # Only one new topic should be created (duplicate skipped)
        final_count = SuggestedTopic.objects.filter(organization=org).count()
        assert final_count == initial_count + 1
        
        # Check only the new topic was created
        assert SuggestedTopic.objects.filter(name="New Topic", organization=org).exists()
    
    def test_create_suggested_topics_duplicate_with_regular_topics_skipped(self, setup_db):
        """Test that topics with names matching regular topics are skipped."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db
        new_topics = [
            {"name": topic.name, "description": "Same name as regular topic"},
            {"name": "Unique Topic", "description": "This should be created"}
        ]
        initial_count = SuggestedTopic.objects.filter(organization=org).count()
        
        db_handler.create_suggested_topics(
            new_topics,
            conversation.path,
            org.id
        )
        
        # Only one new topic should be created (duplicate with regular topic skipped)
        final_count = SuggestedTopic.objects.filter(organization=org).count()
        assert final_count == initial_count + 1
        assert SuggestedTopic.objects.filter(name="Unique Topic", organization=org).exists()
    
    def test_create_suggested_topics_replacement_logic(self, setup_db):
        """Test topic replacement when at max capacity."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Set max topic count to 2 for testing
        org.max_topic_count = 2
        org.save()
        
        # Create 2 existing suggested topics
        old_topic1 = SuggestedTopic.objects.create(
            name="Old Topic 1", description="Old", organization=org
        )
        old_topic2 = SuggestedTopic.objects.create(
            name="Old Topic 2", description="Old", organization=org  
        )
        
        # Create conversations for old topics to set conversation_count = 1
        old_conv1 = Conversation.objects.create(
            path="old_conv1.wav", date=timezone.now(), duration=60,
            title="Old1", summary="Old1", transcript="Old1", sentiment=3,
            starting_sentiment=2, ending_sentiment=4,
            agent=agent, customer=customer, input_tokens=10, output_tokens=10
        )
        old_conv2 = Conversation.objects.create(
            path="old_conv2.wav", date=timezone.now(), duration=60,
            title="Old2", summary="Old2", transcript="Old2", sentiment=3,
            starting_sentiment=2, ending_sentiment=4,
            agent=agent, customer=customer, input_tokens=10, output_tokens=10
        )
        
        old_conv1.suggested_topics.add(old_topic1)
        old_conv2.suggested_topics.add(old_topic2)
        
        # Force stats update
        old_topic1.update_conversation_stats()
        old_topic2.update_conversation_stats()
        
        new_topics = [
            {"name": "New Topic 1", "description": "New topic 1"},
            {"name": "New Topic 2", "description": "New topic 2"}
        ]
        
        db_handler.create_suggested_topics(
            new_topics,
            conversation.path, 
            org.id
        )

        # Check old topics were replaced
        assert not SuggestedTopic.objects.filter(name="Old Topic 1").exists()
        assert not SuggestedTopic.objects.filter(name="Old Topic 2").exists()
        assert SuggestedTopic.objects.filter(name="New Topic 1").exists()
        assert SuggestedTopic.objects.filter(name="New Topic 2").exists()
    
    def test_create_suggested_topics_no_replacement_when_popular(self, setup_db):
        """Test that popular topics (conversation_count > 1) are not replaced."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db
        org.max_topic_count = 1
        org.save()
        
        # Create existing suggested topic
        popular_topic = SuggestedTopic.objects.create(
            name="Popular Topic", description="Popular", organization=org
        )
        
        # Create multiple conversations to make it popular (conversation_count > 1)
        conv1 = Conversation.objects.create(
            path="pop_conv1.wav", date=timezone.now(), duration=60,
            title="Pop1", summary="Pop1", transcript="Pop1", sentiment=3,
            starting_sentiment=2, ending_sentiment=4,
            agent=agent, customer=customer, input_tokens=10, output_tokens=10
        )
        conv2 = Conversation.objects.create(
            path="pop_conv2.wav", date=timezone.now(), duration=60,
            title="Pop2", summary="Pop2", transcript="Pop2", sentiment=3,
            starting_sentiment=2, ending_sentiment=4,
            agent=agent, customer=customer, input_tokens=10, output_tokens=10
        )
        
        conv1.suggested_topics.add(popular_topic)
        conv2.suggested_topics.add(popular_topic)
        popular_topic.update_conversation_stats()
        
        new_topics = [{"name": "New Topic", "description": "Should not be created"}]
        
        db_handler.create_suggested_topics(new_topics, conversation.path, org.id)
        
        # Popular topic should remain, new topic should not be created
        assert SuggestedTopic.objects.filter(name="Popular Topic").exists()
        assert not SuggestedTopic.objects.filter(name="New Topic").exists()
    
    def test_create_suggested_topics_invalid_format_skipped(self, setup_db):
        """Test that topics with invalid format are skipped."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db
        new_topics = [
            {"name": "Valid Topic", "description": "Valid"},
            {"name": "Missing Description"},  # Missing description
            {"description": "Missing Name"},  # Missing name
            {},  # Empty dict
            {"name": "", "description": "Empty name"},  # Empty name
            {"name": "Empty desc", "description": ""}  # Empty description
        ]
        
        initial_count = SuggestedTopic.objects.filter(organization=org).count()
        
        db_handler.create_suggested_topics(new_topics, conversation.path, org.id)
        
        # Only valid topic should be created
        final_count = SuggestedTopic.objects.filter(organization=org).count()
        assert final_count == initial_count + 1
        assert SuggestedTopic.objects.filter(name="Valid Topic").exists()
    
    def test_create_suggested_topics_nonexistent_conversation_raises(self, setup_db):
        """Test that nonexistent conversation path raises ValueError."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db
        new_topics = [{"name": "Test", "description": "Test"}]
        
        with pytest.raises(ValueError) as exc_info:
            db_handler.create_suggested_topics(new_topics, "nonexistent.wav", org.id)
        
        assert "Could not find a Conversation instance" in str(exc_info.value)
    
    def test_create_suggested_topics_multiple_conversations_same_path_raises(self, setup_db):
        """Test that multiple conversations with same path raises ValueError."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Create two conversations with same path
        Conversation.objects.create(
            path="duplicate.wav", date=timezone.now(), duration=60,
            title="Dup1", summary="Dup1", transcript="Dup1", sentiment=3,
            starting_sentiment=2, ending_sentiment=4,
            agent=agent, customer=customer, input_tokens=10, output_tokens=10
        )
        Conversation.objects.create(
            path="duplicate.wav", date=timezone.now(), duration=60,
            title="Dup2", summary="Dup2", transcript="Dup2", sentiment=3,
            starting_sentiment=2, ending_sentiment=4,
            agent=agent, customer=customer, input_tokens=10, output_tokens=10
        )
        
        new_topics = [{"name": "Test", "description": "Test"}]
        
        with pytest.raises(ValueError) as exc_info:
            db_handler.create_suggested_topics(new_topics, "duplicate.wav", org.id)
        
        assert "More than one Conversation instance matches" in str(exc_info.value)


@pytest.mark.django_db
class TestCreateConversation:
    """Test the create_conversation function in db_handler."""
    
    def test_create_conversation_basic(self, setup_db):
        """Test basic conversation creation with topics and suggested topics."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db
        customer_id = "CUST123"
        timestamp = "2024-01-01T12:00:00Z"
        
        db_handler.create_conversation(
            customer_id=customer_id,
            organization_id=org.id,
            agent_id=agent.id,
            topics=[topic.name],
            suggested_topics=[suggested_topic.name],
            file_name="test_call.wav",
            timestamp=timestamp,
            duration=120.5,
            transcript="Test transcript",
            sentiment=4.2,
            starting_sentiment=3.0,
            ending_sentiment=5.0,
            summary="Test summary",
            title="Test Call",
            input_tokens=100,
            output_tokens=50,
            revenue_at_stake=3.4,
            resolved=False
        )
        
        # Verify conversation was created
        conversation = Conversation.objects.get(path="test_call.wav")
        assert conversation.agent == agent
        assert conversation.customer.external_id == customer_id
        assert conversation.customer.organization == org
        assert conversation.duration == 120.5
        assert conversation.transcript == "Test transcript"
        assert conversation.sentiment == 4.2
        assert conversation.starting_sentiment == 3.0
        assert conversation.ending_sentiment == 5.0
        assert conversation.summary == "Test summary"
        assert conversation.title == "Test Call"
        assert conversation.input_tokens == 100
        assert conversation.output_tokens == 50
        
        # Verify topic relationships
        assert topic in conversation.topics.all()
        assert suggested_topic in conversation.suggested_topics.all()
    
    def test_create_conversation_creates_customer(self, setup_db):
        """Test that create_conversation creates a new customer if one doesn't exist."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db
        customer_id = "NEW_CUSTOMER_123"
        
        # Verify customer doesn't exist
        assert not Customer.objects.filter(
            external_id=customer_id, 
            organization=org
        ).exists()
        
        db_handler.create_conversation(
            customer_id=customer_id,
            organization_id=org.id,
            agent_id=agent.id,
            topics=[topic.name],
            suggested_topics=[],
            file_name="test_call.wav",
            timestamp="2024-01-01T12:00:00Z",
            duration=60.0,
            transcript="Test transcript",
            sentiment=3.0,
            starting_sentiment=2.5,
            ending_sentiment=3.5,
            summary="Test summary", 
            title="Test Call",
            input_tokens=80,
            output_tokens=40,
            revenue_at_stake=3.4,
            resolved=False
        )
        
        # Verify customer was created
        customer = Customer.objects.get(
            external_id=customer_id,
            organization=org
        )
        conversation = Conversation.objects.get(path="test_call.wav")
        assert conversation.customer == customer
    
    def test_create_conversation_reuses_existing_customer(self, setup_db):
        """Test that create_conversation reuses an existing customer."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        initial_customer_count = Customer.objects.filter(organization=org).count()
        
        db_handler.create_conversation(
            customer_id=customer.external_id,
            organization_id=org.id,
            agent_id=agent.id,
            topics=[topic.name],
            suggested_topics=[],
            file_name="test_call.wav", 
            timestamp="2024-01-01T12:00:00Z",
            duration=90.0,
            transcript="Test transcript",
            sentiment=4.0,
            starting_sentiment=3.5,
            ending_sentiment=4.5,
            summary="Test summary",
            title="Test Call",
            input_tokens=120,
            output_tokens=60,
            revenue_at_stake=3.4,
            resolved=False
        )
        
        # Verify no new customer was created
        final_customer_count = Customer.objects.filter(organization=org).count()
        assert final_customer_count == initial_customer_count
        
        # Verify conversation uses existing customer
        conversation = Conversation.objects.get(path="test_call.wav")
        assert conversation.customer == customer
    
    def test_create_conversation_multiple_topics(self, setup_db):
        """Test creating conversation with multiple topics and suggested topics."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Create multiple topics and suggested topics
        topic1 = Topic.objects.create(name="Topic 1", description="First topic", organization=org)
        topic2 = Topic.objects.create(name="Topic 2", description="Second topic", organization=org)
        suggested1 = SuggestedTopic.objects.create(name="Suggested 1", description="First suggested", organization=org)
        suggested2 = SuggestedTopic.objects.create(name="Suggested 2", description="Second suggested", organization=org)
        
        db_handler.create_conversation(
            customer_id="CUST456",
            organization_id=org.id,
            agent_id=agent.id,
            topics=[topic1.name, topic2.name],
            suggested_topics=[suggested1.name, suggested2.name],
            file_name="multi_topic_call.wav",
            timestamp="2024-01-01T12:00:00Z", 
            duration=180.0,
            transcript="Multi-topic transcript",
            sentiment=3.5,
            starting_sentiment=3.0,
            ending_sentiment=4.0,
            summary="Multi-topic summary",
            title="Multi-topic Call",
            input_tokens=200,
            output_tokens=100,
            revenue_at_stake=3.4,
            resolved=False
        )
        
        conversation = Conversation.objects.get(path="multi_topic_call.wav")
        
        # Verify all topics are linked
        assert conversation.topics.count() == 2
        assert topic1 in conversation.topics.all()
        assert topic2 in conversation.topics.all()
        
        # Verify all suggested topics are linked
        assert conversation.suggested_topics.count() == 2  
        assert suggested1 in conversation.suggested_topics.all()
        assert suggested2 in conversation.suggested_topics.all()

    def test_create_conversation_empty_topics_lists(self, setup_db):
        """Test creating conversation with empty topics and suggested_topics lists."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        db_handler.create_conversation(
            customer_id="CUST202",
            organization_id=org.id,
            agent_id=agent.id,
            topics=[],  # Empty
            suggested_topics=[],  # Empty
            file_name="empty_topics_call.wav",
            timestamp="2024-01-01T12:00:00Z",
            duration=45.0,
            transcript="Simple transcript",
            sentiment=3.8,
            starting_sentiment=3.2,
            ending_sentiment=4.4,
            summary="Simple summary",
            title="Simple Call",
            input_tokens=60,
            output_tokens=30,
            revenue_at_stake=3.4,
            resolved=False
        )
        
        conversation = Conversation.objects.get(path="empty_topics_call.wav")
        assert conversation.topics.count() == 0
        assert conversation.suggested_topics.count() == 0
    
    def test_create_conversation_timezone_handling(self, setup_db):
        """Test that timestamps are properly handled for timezone awareness."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Test with naive datetime string
        db_handler.create_conversation(
            customer_id="CUST303",
            organization_id=org.id,
            agent_id=agent.id,
            topics=[topic.name],
            suggested_topics=[],
            file_name="timezone_call.wav",
            timestamp="2024-01-01T12:00:00",  # No timezone info
            duration=60.0,
            transcript="Timezone test",
            sentiment=4.0,
            starting_sentiment=3.8,
            ending_sentiment=4.2,
            summary="Timezone summary",
            title="Timezone Call",
            input_tokens=70,
            output_tokens=35,
            revenue_at_stake=3.4,
            resolved=False
        )
        
        conversation = Conversation.objects.get(path="timezone_call.wav")
        # Verify the datetime is timezone-aware
        assert conversation.date.tzinfo is not None
    
    def test_create_conversation_datetime_object(self, setup_db):
        """Test create_conversation with datetime object instead of string."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db
        
        dt_obj = timezone.make_aware(datetime(2024, 1, 1, 12, 0, 0))
        
        db_handler.create_conversation(
            customer_id="CUST404",
            organization_id=org.id,
            agent_id=agent.id,
            topics=[topic.name],
            suggested_topics=[],
            file_name="datetime_obj_call.wav",
            timestamp=dt_obj,  # Datetime object
            duration=55.0,
            transcript="Datetime object test",
            sentiment=3.2,
            starting_sentiment=3.0,
            ending_sentiment=3.4,
            summary="Datetime summary",
            title="Datetime Call", 
            input_tokens=85,
            output_tokens=42,
            revenue_at_stake=3.4,
            resolved=False
        )
        
        conversation = Conversation.objects.get(path="datetime_obj_call.wav")
        assert conversation.date == dt_obj
    
    def test_create_conversation_invalid_timestamp_raises(self, setup_db):
        """Test that invalid timestamp raises ValueError."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        with pytest.raises(ValueError) as exc_info:
            db_handler.create_conversation(
                customer_id="CUST505",
                organization_id=org.id,
                agent_id=agent.id,
                topics=[topic.name],
                suggested_topics=[],
                file_name="invalid_timestamp_call.wav",
                timestamp=None,  # Invalid timestamp
                duration=60.0,
                transcript="Test transcript",
                sentiment=3.0,
                starting_sentiment=2.8,
                ending_sentiment=3.2,
                summary="Test summary",
                title="Test Call",
                input_tokens=80,
                output_tokens=40,
                revenue_at_stake=3.4,
                resolved=False
            )
        
        assert "Could not parse datetime from" in str(exc_info.value)


@pytest.mark.django_db
class TestTriggerSummarizationTasks:
    """Test the trigger_summarization_tasks function."""

    @patch('tellme.call_miner.models.create_summarization_task')
    def test_trigger_summarization_tasks_with_conversation(self, mock_create_task, setup_db):
        """Test triggering summarization tasks for a conversation with linked objects."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Mock the task creation to return a task ID
        mock_create_task.return_value = "task-id-123"

        # Call the function with the conversation
        trigger_summarization_tasks(conversation)

        # Verify that summarization tasks were created for topic, customer, and agent
        # Default settings typically use 'quarter' period and rolling=True, but this depends on settings
        # At minimum, there should be calls for the 3 objects (topic, customer, agent)
        assert mock_create_task.call_count >= 3

        # Verify that tasks were created for all linked objects
        call_args_list = mock_create_task.call_args_list
        created_object_ids = [call[1]['object_id'] for call in call_args_list]

        assert topic.id in created_object_ids
        assert customer.id in created_object_ids
        assert agent.id in created_object_ids

    @patch('tellme.call_miner.models.create_summarization_task')
    def test_trigger_summarization_tasks_with_multiple_topics(self, mock_create_task, setup_db):
        """Test triggering summarization tasks for conversation with multiple topics."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Create additional topics and link them to the conversation
        topic2 = Topic.objects.create(
            name="Additional Topic",
            description="Another test topic",
            organization=org,
            is_active=True
        )
        conversation.topics.add(topic2)

        # Mock the task creation to return a task ID
        mock_create_task.return_value = "task-id-456"

        # Call the function
        trigger_summarization_tasks(conversation)

        # Verify that summarization tasks were created for both topics plus customer and agent
        call_args_list = mock_create_task.call_args_list
        created_object_ids = [call[1]['object_id'] for call in call_args_list]

        # Should have tasks for both topics, customer, and agent
        assert topic.id in created_object_ids
        assert topic2.id in created_object_ids
        assert customer.id in created_object_ids
        assert agent.id in created_object_ids

    @patch('tellme.call_miner.models.create_summarization_task')
    def test_trigger_summarization_tasks_handles_failures(self, mock_create_task, setup_db):
        """Test that function handles task creation failures gracefully."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Mock one of the calls to raise an exception
        def side_effect(*args, **kwargs):
            if kwargs.get('object_type') == 'topic':
                raise Exception("Task creation failed")
            return "task-id-success"

        mock_create_task.side_effect = side_effect

        # Call the function - should not raise exception
        trigger_summarization_tasks(conversation)

        # Verify that task creation was attempted for all objects
        # Even if one fails, the others should still be attempted
        assert mock_create_task.call_count >= 3


@pytest.mark.django_db
class TestCreatePeriodSummary:
    """Test the create_periodsummary function."""

    def test_create_periodsummary_success(self, setup_db):
        """Test successful creation of a PeriodSummary object."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Call the function
        result = create_periodsummary(
            obj=topic,
            summary="Test summary content",
            latest_date="2024-01-15",
            call_count=10,
            label="January 2024",
            period="month"
        )

        # Verify the function returns None
        assert result is None

        # Verify it was saved to the database
        content_type = ContentType.objects.get_for_model(topic)
        saved_summary = PeriodSummary.objects.get(
            content_type=content_type,
            object_id=topic.id,
            period_type="month",
            period_label="January 2024"
        )

        # Verify the saved object has correct attributes
        assert saved_summary.summary == "Test summary content"
        assert str(saved_summary.last_call_at) == '2024-01-15 00:00:00+00:00'
        assert saved_summary.call_count == 10
        assert saved_summary.period_label == "January 2024"
        assert saved_summary.period_type == "month"

    def test_create_periodsummary_different_object_types(self, setup_db):
        """Test creating PeriodSummary for different object types."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        objects_to_test = [
            (topic, "Topic summary"),
            (customer, "Customer summary"),
            (agent, "Agent summary")
        ]

        for obj, summary_text in objects_to_test:
            result = create_periodsummary(
                obj=obj,
                summary=summary_text,
                latest_date="2024-01-01",
                call_count=1,
                label="Rolling90D",
                period="quarter"
            )

            # Verify the function returns None
            assert result is None

            # Verify correct object type association in database
            content_type = ContentType.objects.get_for_model(obj)
            saved_summary = PeriodSummary.objects.get(
                content_type=content_type,
                object_id=obj.id,
                period_type="quarter",
                period_label="Rolling90D"
            )
            assert saved_summary.content_type == content_type
            assert saved_summary.object_id == obj.id
            assert saved_summary.summary == summary_text

    def test_create_periodsummary_updates_existing(self, setup_db):
        """Test that creating a PeriodSummary updates existing ones with same parameters."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Create first summary
        first_result = create_periodsummary(
            obj=topic,
            summary="Original summary",
            latest_date="2024-01-01",
            call_count=5,
            label="Test Label",
            period="month"
        )

        # Verify first call returns None
        assert first_result is None

        # Get the created summary from database
        content_type = ContentType.objects.get_for_model(topic)
        first_summary = PeriodSummary.objects.get(
            content_type=content_type,
            object_id=topic.id,
            period_type="month",
            period_label="Test Label"
        )
        first_id = first_summary.id

        # Create another with same label - should update existing
        second_result = create_periodsummary(
            obj=topic,
            summary="Updated summary",
            latest_date="2024-01-15",
            call_count=10,
            label="Test Label",
            period="month"
        )

        # Verify second call also returns None
        assert second_result is None

        # Get the updated summary from database
        updated_summary = PeriodSummary.objects.get(
            content_type=content_type,
            object_id=topic.id,
            period_type="month",
            period_label="Test Label"
        )

        # Should be the same object (updated)
        assert updated_summary.id == first_id
        assert updated_summary.summary == "Updated summary"
        assert str(updated_summary.last_call_at) == '2024-01-15 00:00:00+00:00'
        assert updated_summary.call_count == 10
        assert updated_summary.period_label == "Test Label"

        # Verify only one object exists in the database
        count = PeriodSummary.objects.filter(
            content_type=content_type,
            object_id=topic.id,
            period_type="month"
        ).count()
        assert count == 1