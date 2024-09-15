import re
from django.db import models
from django.utils.text import slugify
from django.contrib.contenttypes.models import ContentType
from call_miner.utils.summary_mining import condense_summaries


class SlugAbstractModel(models.Model):
    """Abstract model with a slug field"""

    slug = models.SlugField(default="", unique=True, null=True)
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Defines the slug making sure that no duplicates within the organization exist"""
        if not self.slug:
            if hasattr(self, 'organization') and self.organization:
                object_type = self.__class__.__name__.lower()
                base_slug = slugify(f'{object_type}-{self.name}-{self.organization}')
            else:
                base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            while self.__class__.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{base_slug}-{num}'
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)


class MetaSummaryAbstractModel(models.Model):
    """
    An abstract model that handles the creation and retrieval of summaries objects for Agent, Customer, and Topic models
    """
    summary = models.TextField(blank=True)
    summary_date = models.DateTimeField(auto_now_add=True, blank=True)
    summary_call_count = models.IntegerField(default=0)

    # Deviation Threshold (in %) for Re-calculation
    DEVIATION_THRESHOLD = 10

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
    A very simple Mixin containing the trends of the conversations associated to a given object
    """
    def get_conversation_trend(self):
        """
        This simple method returns the evolution of the number of calls with time
        """
        conversations_per_day = (
            self.conversations
            .values('date__date')
            .annotate(count=models.Count('id'))
            .order_by('date__date')
        )
        return list(conversations_per_day)


class Organization(SlugAbstractModel):
    """
    Organization: One of the many organizations that make use of the app. Separates the data for every group of users
    """

    name = models.CharField(max_length=100, unique=True, null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Organizations"


class Topic(SlugAbstractModel, MetaSummaryAbstractModel, ConversationTrendMixin):
    """
    Topic: One of the many topics that can be discussed in the customer calls. These are to be detected by a
    multi-label classification task.
    """

    description = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='topics')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'organization')
        indexes = [
            models.Index(fields=['organization', 'name']),
        ]


class Analyst(models.Model):
    """
    Analyst: Each analyst belongs to a single organization and has access to all conversations in that organization.
    """

    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='analysts')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Analysts"
        indexes = [
            models.Index(fields=['organization', 'name']),
        ]


class Manager(models.Model):
    """
    Manager: Each manager supervises multiple agents within an organization.
    """

    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='managers')
    agents = models.ManyToManyField('Agent', related_name='managers')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Managers"
        indexes = [
            models.Index(fields=['organization', 'name']),
        ]


class Agent(SlugAbstractModel, MetaSummaryAbstractModel, ConversationTrendMixin):
    """
    Agent: One of the many agents belonging to an organization. In charge of making the calls.
    Each agent belongs to one or more managers.
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='agents')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Agents"
        indexes = [
            models.Index(fields=['organization', 'name']),
        ]


class Customer(SlugAbstractModel, MetaSummaryAbstractModel, ConversationTrendMixin):
    """
    Customer: One of the many customers belonging to an organization. Customers have calls with one agent at a time.
    Calls act as a bridge between agents and customers
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='customers')

    class Meta:
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
    date = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField()
    transcript = models.TextField()
    sentiment = models.FloatField(max_length=100, blank=True)
    summary = models.TextField()
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
