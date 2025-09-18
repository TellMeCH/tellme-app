import pytest
from datetime import datetime
from django.utils import timezone
from apps.call_miner.models import SuggestedTopic, Topic, Conversation, Organization, Customer
from call_processing.utils import db_handler


@pytest.mark.django_db
class TestObtainSuggestedTopics:
    """Test the obtain_suggested_topics function."""
    
    def test_obtain_suggested_topics_with_data(self, setup_db):
        """Test with existing suggested topics."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db
        result = db_handler.obtain_suggested_topics(org.id)
        assert suggested_topic.name in result
        assert suggested_topic.description in result
        assert result.endswith(', ')
    
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
            agent=agent, customer=customer, input_tokens=10, output_tokens=10
        )
        old_conv2 = Conversation.objects.create(
            path="old_conv2.wav", date=timezone.now(), duration=60,
            title="Old2", summary="Old2", transcript="Old2", sentiment=3,
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
            agent=agent, customer=customer, input_tokens=10, output_tokens=10
        )
        conv2 = Conversation.objects.create(
            path="pop_conv2.wav", date=timezone.now(), duration=60,
            title="Pop2", summary="Pop2", transcript="Pop2", sentiment=3,
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
            agent=agent, customer=customer, input_tokens=10, output_tokens=10
        )
        Conversation.objects.create(
            path="duplicate.wav", date=timezone.now(), duration=60,
            title="Dup2", summary="Dup2", transcript="Dup2", sentiment=3,
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
            summary="Test summary",
            title="Test Call",
            input_tokens=100,
            output_tokens=50
        )
        
        # Verify conversation was created
        conversation = Conversation.objects.get(path="test_call.wav")
        assert conversation.agent == agent
        assert conversation.customer.external_id == customer_id
        assert conversation.customer.organization == org
        assert conversation.duration == 120.5
        assert conversation.transcript == "Test transcript"
        assert conversation.sentiment == 4.2
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
            summary="Test summary", 
            title="Test Call",
            input_tokens=80,
            output_tokens=40
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
            summary="Test summary",
            title="Test Call",
            input_tokens=120,
            output_tokens=60
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
            summary="Multi-topic summary",
            title="Multi-topic Call",
            input_tokens=200,
            output_tokens=100
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
    
    def test_create_conversation_missing_topics_warning(self, setup_db):
        """Test that missing topics raise a warning."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Create only one topic but request two
        existing_topic = Topic.objects.create(name="Existing Topic", description="Exists", organization=org)
        
        with pytest.raises(Warning) as exc_info:
            db_handler.create_conversation(
                customer_id="CUST789",
                organization_id=org.id,
                agent_id=agent.id,
                topics=["Existing Topic", "Missing Topic"],  # One exists, one doesn't
                suggested_topics=[],
                file_name="missing_topics_call.wav",
                timestamp="2024-01-01T12:00:00Z",
                duration=60.0,
                transcript="Test transcript",
                sentiment=3.0,
                summary="Test summary",
                title="Test Call",
                input_tokens=80,
                output_tokens=40
            )
        
        assert "Some topics were not found" in str(exc_info.value)
        assert "Missing Topic" in str(exc_info.value)
    
    def test_create_conversation_missing_suggested_topics_warning(self, setup_db):
        """Test that missing suggested topics raise a warning."""
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Create only one suggested topic but request two
        existing_suggested = SuggestedTopic.objects.create(
            name="Existing Suggested", 
            description="Exists", 
            organization=org
        )
        
        with pytest.raises(Warning) as exc_info:
            db_handler.create_conversation(
                customer_id="CUST101",
                organization_id=org.id,
                agent_id=agent.id,
                topics=[topic.name],
                suggested_topics=["Existing Suggested", "Missing Suggested"],
                file_name="missing_suggested_call.wav",
                timestamp="2024-01-01T12:00:00Z",
                duration=75.0,
                transcript="Test transcript", 
                sentiment=4.0,
                summary="Test summary",
                title="Test Call",
                input_tokens=90,
                output_tokens=45
            )
        
        assert "Some suggested topics were not found" in str(exc_info.value)
        assert "Missing Suggested" in str(exc_info.value)
    
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
            summary="Simple summary",
            title="Simple Call",
            input_tokens=60,
            output_tokens=30
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
            summary="Timezone summary",
            title="Timezone Call",
            input_tokens=70,
            output_tokens=35
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
            summary="Datetime summary",
            title="Datetime Call", 
            input_tokens=85,
            output_tokens=42
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
                summary="Test summary",
                title="Test Call",
                input_tokens=80,
                output_tokens=40
            )
        
        assert "Could not parse datetime from" in str(exc_info.value)