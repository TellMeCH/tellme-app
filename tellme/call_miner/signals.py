from django.db.models.signals import post_save, pre_delete, post_delete, m2m_changed
from django.dispatch import receiver
from tellme.call_miner.models import Conversation


@receiver(post_save, sender=Conversation)
def conversation_post_save_update_stats(sender, instance, created, **kwargs):
    """
    Updates conversation-related stats whenever a Conversation is created/updated.
    Mirrors what 'register_signals' used to do. Now it’s in a single receiver:
    - Update the agent’s stats
    - Update the customer’s stats
    - Update each topic’s stats
    - Update each
    """
    # Update the agent stats
    if instance.agent:
        instance.agent.update_conversation_stats()

    # Update the customer stats
    if instance.customer:
        instance.customer.update_conversation_stats()

    # Update all topics stats
    for topic in instance.topics.all():
        topic.update_conversation_stats()
    
    # Update all suggested topics stats
    for suggested_topic in instance.suggested_topics.all():
        suggested_topic.update_conversation_stats()


@receiver(pre_delete, sender=Conversation)
def conversation_pre_delete_store_topics(sender, instance, **kwargs):
    # Stash the topics in an attribute, so we can access them in post_delete
    instance._topics_before_deletion = list(instance.topics.all())
    instance._suggested_topics_before_deletion = list(instance.suggested_topics.all())


@receiver(post_delete, sender=Conversation)
def conversation_post_delete_update_stats(sender, instance, **kwargs):
    if instance.agent:
        instance.agent.update_conversation_stats()

    if instance.customer:
        instance.customer.update_conversation_stats()

    # Now we can't use instance.topics.all(), but we have instance._topics_before_deletion
    for topic in getattr(instance, '_topics_before_deletion', []):
        topic.update_conversation_stats()
    
    # Update suggested topics stats after deletion
    for suggested_topic in getattr(instance, '_suggested_topics_before_deletion', []):
        suggested_topic.update_conversation_stats()


@receiver(m2m_changed, sender=Conversation.topics.through)
def validate_topics_organization(sender, instance, action, **kwargs):
    """
    Enforces that all 'topics' belong to the same organization as the conversation's agent.
    """
    if action in ('post_add', 'post_remove', 'post_clear'):
        conversation_organization = instance.agent.organization
        for topic in instance.topics.all():
            if topic.organization != conversation_organization:
                raise ValueError(
                    f"Topic '{topic.name}' is not associated with the same "
                    "organization as the customer and agent."
                )
        # Optionally, if you want stats updated immediately after adding or removing topics:
        for topic in instance.topics.all():
            topic.update_conversation_stats()


@receiver(m2m_changed, sender=Conversation.suggested_topics.through)
def validate_suggested_topics_organization(sender, instance, action, **kwargs):
    """
    Enforces that all 'suggested_topics' belong to the same organization as the conversation's agent.
    """
    if action in ('post_add', 'post_remove', 'post_clear'):
        conversation_organization = instance.agent.organization
        for suggested_topic in instance.suggested_topics.all():
            if suggested_topic.organization != conversation_organization:
                raise ValueError(
                    f"Suggested Topic '{suggested_topic.name}' is not associated with the same "
                    "organization as the customer and agent."
                )
        # Optionally, if you want stats updated immediately after adding or removing suggested topics:
        for suggested_topic in instance.suggested_topics.all():
            suggested_topic.update_conversation_stats()