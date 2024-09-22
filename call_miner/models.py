import re
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from call_miner.utils.summary_mining import condense_summaries
from django.core.exceptions import ValidationError


class MetaSummaryAbstractModel(models.Model):
    """
    An abstract model that handles the creation and retrieval of summaries objects for Agent, Customer, and Topic models
    """
    summary = models.TextField(null=True)
    summary_date = models.DateTimeField(auto_now_add=True, null=True)
    summary_call_count = models.IntegerField(default=0)

    # Deviation Threshold (in %) for Re-calculation
    DEVIATION_THRESHOLD = 10

    class Meta:
        abstract = True

    def get_or_create_summary(self):
        """
        Extract all the object's related conversations, as well as their summaries. If enough new summaries have
        been produced, condense them into a new meta-summary for the object.
        """
        relevant_summaries = [conv.summary for conv in self.conversations.order_by('-date')]
        latest_date = self.conversations.aggregate(latest_date=models.Max('date'))['latest_date']
        actual_call_count = len(relevant_summaries)

        # Compare the count with the Summary object's count field
        if self.is_deviation_significant(actual_call_count):
            # Call the external function with the list of summaries
            new_summary_text = condense_summaries(relevant_summaries)
            self.summary = new_summary_text
            self.summary_call_count = actual_call_count
            self.summary_date = latest_date
            self.save()  # Save the updated MetaSummary with the new data

    def is_deviation_significant(self, actual_count):
        """
        Determine whether enough new calls have been created associated to the agent/customer/topic to warrant a
        summary re-calculation
        """
        # Calculate the percentage deviation
        if self.summary_call_count == 0:  # Prevent division by zero
            return True
        deviation = abs((actual_count - self.summary_call_count) / self.summary_call_count) * 100
        return deviation > self.DEVIATION_THRESHOLD


class ConversationTrendMixin:
    """
    Mixin containing the trends of the conversations associated with a given object, now including
    average call duration and sentiment.
    """

    @property
    def conversations_scope(self):
        """
        Retrieves the conversation set depending on the type of object.
        If it's an Organization, it fetches all conversations from its associated agents.
        If it's an Agent that is a manager, it fetches all the team's conversations.
        Otherwise, it assumes the object has a direct relationship to conversations.
        """
        if isinstance(self, Organization):
            # Get all conversations for the organization's agents
            return Conversation.objects.filter(agent__organization=self)
        elif isinstance(self, Agent):
            # If the agent is a manager, get their own conversations and those of their team
            return Conversation.objects.filter(agent__in=self.agents.all() | Agent.objects.filter(id=self.id))
        else:
            # Assume the object has a direct relationship with conversations
            return self.conversations.all()

    def get_conversation_trend(self):
        """
        Returns the evolution of the number of calls with time.
        """
        conversations_per_day = (
            self.conversations_scope
            .values('date__date')
            .annotate(count=models.Count('id'))
            .order_by('date__date')
        )
        return list(conversations_per_day)

    def get_conversation_trend_per_topic(self):
        """
        Returns the number of conversations per topic per day.
        """
        conversations_per_topic_per_day = (
            self.conversations_scope
            .values('topics__name', 'date__date')
            .annotate(count=models.Count('id'))
            .order_by('topics__name', 'date__date')
        )
        return list(conversations_per_topic_per_day)

    def get_avg_for_periods(self, field):
        """
        Generic function to calculate the average of a given field (duration or sentiment)
        for daily, weekly, and monthly periods.
        """
        periods = {
            'daily': models.functions.TruncDay('date'),
            'weekly': models.functions.TruncWeek('date'),
            'monthly': models.functions.TruncMonth('date'),
        }

        results = {}
        for period_name, period_trunc in periods.items():
            avg_per_period = (
                self.conversations_scope
                .annotate(period=period_trunc)
                .values('period')
                .annotate(avg_value=models.Avg(field))
                .order_by('period')
            )
            results[period_name] = list(avg_per_period)

        return results

    def get_avg_duration(self):
        """
        Returns a dictionary with the average call duration per day, week, and month.
        """
        return self.get_avg_for_periods('duration')

    def get_avg_sentiment(self):
        """
        Returns a dictionary with the average sentiment score per day, week, and month.
        """
        return self.get_avg_for_periods('sentiment')


class Organization(models.Model, ConversationTrendMixin):
    """
    Organization: One of the many organizations that make use of the app. Separates the data for every group of users
    """

    name = models.CharField(max_length=100, unique=True, null=False)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name',)
        verbose_name_plural = "Organizations"


class Topic(MetaSummaryAbstractModel, ConversationTrendMixin):
    """
    Topic: One of the many topics that can be discussed in the customer calls. These are to be detected by a
    multi-label classification task.
    """
    name = models.CharField(max_length=100, null=False)
    description = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='topics')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'organization')
        indexes = [
            models.Index(fields=['organization', 'name']),
        ]


class Employee(models.Model):
    """
    A versatile role. An employee can be an analyst, an agent, or a manager. Contains the basic attributes that all
    these user types inherit.
    - An analyst is a simple employee. Basically, a user with an organization label
    - An agent is an employee that can be tagged in Conversations
    - A manager is an agent that is related to another agent in a hierarchical relationship. Managers can hold calls.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='employees')
    user = models.OneToOneField('auth.User', related_name='employee', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    class Meta:
        unique_together = ('user', 'organization')
        verbose_name_plural = "Employees"


class Analyst(Employee):
    class Meta:
        verbose_name_plural = "Analysts"


class Agent(Employee, MetaSummaryAbstractModel, ConversationTrendMixin):
    manager = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL,
        related_name='agents'
    )

    def save(self, *args, **kwargs):
        # Ensure that an agent is not assigned as their own manager.
        if self.manager == self:
            raise ValidationError("An agent cannot be their own manager.")

        # Ensure that the manager is correctly specified
        if self.manager:
            if self.organization != self.manager.organization:
                raise ValueError("The assigned manager must be associated with the same organization.")

        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Agents"


class Customer(MetaSummaryAbstractModel, ConversationTrendMixin):
    """
    Customer: One of the many customers belonging to an organization. Customers have calls with one agent at a time.
    Calls act as a bridge between agents and customers
    """
    name = models.CharField(max_length=100, null=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='customers')

    class Meta:
        unique_together = ('name', 'organization')
        verbose_name_plural = "Customers"
        indexes = [
            models.Index(fields=['organization', 'name']),
        ]

    def __str__(self):
        return self.name


class Conversation(models.Model):
    """
    Conversation: One of the many calls belonging to a customer and an agent.
    Among its attributes, it contains the path to the call recording, the call date and time, the call duration,
    the call transcript, the call topics mentioned, and the call sentiment
    """
    path = models.CharField(max_length=100)
    date = models.DateTimeField()
    duration = models.FloatField()
    transcript = models.TextField()
    sentiment = models.FloatField(max_length=100)
    summary = models.TextField()
    title = models.TextField()
    input_tokens = models.IntegerField()
    output_tokens = models.IntegerField()
    topics = models.ManyToManyField(Topic, related_name='conversations')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='conversations')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='conversations')

    class Meta:
        verbose_name_plural = "Conversations"
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['agent']),
        ]

    def __str__(self):
        return self.path

    def save(self, *args, **kwargs):
        """
        Save applying checks to the given associated objects
        """
        # Ensure that agent and customer have the same associated organization
        if self.customer.organization != self.agent.organization:
            raise ValueError("The assigned customer and agent must be associated with the same organization.")
        super().save(*args, **kwargs)

    def process_transcript(self):
        """
        This method processes the call transcript to separate it into messages.
        """

        # Split the transcript on "Agent:" and "Customer:", while keeping the labels as part of the results
        # This regex will split the transcript based on "Agent:" or "Customer:" while preserving these words
        messages = re.split(r'(?=(<agent>:|<customer>:))', self.transcript)

        # Pair up the message and assign the appropriate class (agent or customer) for coloring
        processed_messages = []
        for i in range(1, len(messages), 2):  # We start at 1 because 0 is an empty string from the split
            speaker = messages[i].strip()  # Either "Agent:" or "Customer:"
            message_text = messages[i + 1][len(speaker):].strip()  # The message following the speaker identifier
            processed_messages.append({
                'message': message_text,
                'class': 'agent-message' if speaker == '<agent>:' else 'customer-message'
            })
        return processed_messages


@receiver(models.signals.m2m_changed, sender=Conversation.topics.through)
def validate_topics_organization(sender, instance, action, **kwargs):
    """
    This function checks that all associated topics belong to the same organization as the conversation's agent
    whenever the topics are added, updated, or cleared.
    """
    # Check if topics were added or changed
    if action == 'post_add' or action == 'post_clear' or action == 'post_remove':
        conversation_organization = instance.agent.organization

        # Validate that all topics belong to the same organization as the customer and agent
        for topic in instance.topics.all():
            if topic.organization != conversation_organization:
                raise ValueError(
                    f"Topic '{topic.name}' is not associated with the same organization as the customer and agent."
                )
