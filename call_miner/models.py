from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from call_miner.utils.summary_mining import condense_summaries


class SlugAbstractModel(models.Model):
    """Abstract model with a slug field"""

    slug = models.SlugField(default="", unique=True, null=False)
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


class MetaSummaryMixin:
    """
    A Mixin that handles the creation and retrieval of MetaSummary objects for the model.
    Applicable to Agent, Customer, and Topic models.
    """

    def get_or_create_meta_summary(self):
        # Get the ContentType for the current model
        content_type = ContentType.objects.get_for_model(self.__class__)

        # Check if MetaSummary already exists for this instance
        meta_summary, created = MetaSummary.objects.get_or_create(
            content_type=content_type,
            object_id=self.id,
            defaults={
                'text': '',
                'call_count': 0
            }
        )

        # Safely access the 'name' field using getattr, providing a default value
        model_name = getattr(self, 'name', 'Unnamed')

        # If the MetaSummary was just created, print a message (or handle initialization logic)
        if created:
            print(f"Created new MetaSummary for {self.__class__.__name__} {model_name}")

        # Call the get_summary() method of the MetaSummary
        return meta_summary.get_summary()


class Organization(SlugAbstractModel):
    """
    Organization: One of the many organizations that make use of the app. Separates the data for every group of users
    """

    name = models.CharField(max_length=100, unique=True, null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Organizations"


class Topic(SlugAbstractModel, MetaSummaryMixin):
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


class Agent(SlugAbstractModel, MetaSummaryMixin):
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


class Customer(SlugAbstractModel, MetaSummaryMixin):
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


class MetaSummary(models.Model):
    """
    MetaSummary: Summary of call summaries, related to an agent, customer or topic. Only created whenever a summary
    view is triggered. Results are stored to avoid further re-calculations.
    """
    text = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    call_count = models.IntegerField(default=0)

    # Generic foreign key fields
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Deviation Threshold (in %) for Re-calculation
    DEVIATION_THRESHOLD = 10

    def save(self, *args, **kwargs):
        # Call full_clean() to trigger validation before saving
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        # Get ContentType for allowed models
        allowed_models = [Agent, Customer, Topic]
        allowed_content_types = ContentType.objects.get_for_models(*allowed_models).values()

        # Validate that content_type is in the allowed content types
        if self.content_type not in allowed_content_types:
            raise ValidationError(f"Invalid content type: {self.content_type}. Must be Agent, Customer or Topic.")

    def get_summary(self):
        # Collect summaries of the relevant calls
        summaries = self.get_relevant_summaries()

        # Count the number of calls
        actual_call_count = len(summaries)

        # Compare the count with the Summary object's count field
        if self.is_deviation_significant(actual_call_count):
            # Call the external function with the list of summaries
            new_summary_text = condense_summaries(summaries)
            self.text = new_summary_text
            self.call_count = actual_call_count
            self.save()  # Save the updated MetaSummary with the new data
        return self.text

    def get_relevant_summaries(self):
        # Retrieve the relevant call summaries based on content_type (Agent, Customer, or Topic)
        if isinstance(self.content_object, Agent):
            calls = Conversation.objects.filter(agent=self.content_object).order_by('-date')
        elif isinstance(self.content_object, Customer):
            calls = Conversation.objects.filter(customer=self.content_object).order_by('-date')
        elif isinstance(self.content_object, Topic):
            calls = Conversation.objects.filter(topics=self.content_object).order_by('-date')
        else:
            raise ValidationError("Invalid content type for Summary")

        # Assuming each Conversation object has a 'summary' field
        return [call.summary for call in calls]

    def is_deviation_significant(self, actual_count):
        # Calculate the percentage deviation
        if self.call_count == 0:  # Prevent division by zero
            return True
        deviation = abs((actual_count - self.call_count) / self.call_count) * 100
        return deviation > self.DEVIATION_THRESHOLD


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
    topics = models.ManyToManyField(Topic, related_name='conversations')
    input_tokens = models.IntegerField()
    output_tokens = models.IntegerField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='conversations')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='conversations')

    def __str__(self):
        return self.path

    class Meta:
        verbose_name_plural = "Conversations"
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['agent']),
        ]
