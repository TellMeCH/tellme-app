import re
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from firebase_admin import auth
from django.contrib.contenttypes.models import ContentType
from call_miner.utils.summary_mining import condense_summaries
from django.db.models.signals import post_save, post_delete


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

    def get_or_create_summary(self, trace_data: dict = None):
        """
        Extract all the object's related conversations, as well as their summaries. If enough new summaries have
        been produced, condense them into a new meta-summary for the object.
        Args:
            trace_data (dict): A dictionary containing data to store in the corresponding Langfuse trace

        """
        if trace_data is None:
            trace_data = {}

        relevant_summaries = [conv.summary for conv in self.conversations.order_by('-date')]
        latest_date = self.conversations.aggregate(latest_date=models.Max('date'))['latest_date']
        actual_call_count = len(relevant_summaries)

        # Compare the count with the Summary object's count field
        if self.is_deviation_significant(actual_call_count):
            # Call the external function with the list of summaries
            new_summary_text = condense_summaries(relevant_summaries, trace_data)
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
            return actual_count > 0
        deviation = abs((actual_count - self.summary_call_count) / self.summary_call_count) * 100
        return deviation > self.DEVIATION_THRESHOLD


class ConversationStatsAbstractModel(models.Model):
    """
    Abstract class used to keep a counter of the existing conversations associated to a model instance.
    These statistics are stored in the related object's memory, and are updated every time a new conversation is saved.
    """
    conversation_count = models.IntegerField(default=0)
    first_conversation_date = models.DateTimeField(null=True, blank=True)
    last_conversation_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def update_conversation_stats(self):
        """
        Updates the stored conversation_count, first_conversation_date, and last_conversation_date fields
        based on the associated conversations.
        """
        stats = self.conversations.aggregate(
            count=models.Count('id'),
            first_date=models.Min('date'),
            last_date=models.Max('date')
        )

        # Update fields if there are any conversations
        self.conversation_count = stats['count']
        self.first_conversation_date = stats['first_date']
        self.last_conversation_date = stats['last_date']
        self.save()

    @staticmethod
    def register_signals(conversation_model, related_field):
        """
        Registers signals to automatically update the conversation count for different models.

        Args:
            conversation_model: The model that has the conversations (e.g., Conversation).
            related_field: The name of the field on the conversation_model that links to the related object
                           (e.g., 'customer', 'agent', 'organization').
        """
        @receiver(post_save, sender=conversation_model)
        def update_stats_on_save(sender, instance, **kwargs):
            if related_field == 'topics':
                for topic in instance.topics.all():
                    topic.update_conversation_stats()
            else:
                related_object = getattr(instance, related_field)
                related_object.update_conversation_stats()

        @receiver(post_delete, sender=conversation_model)
        def update_stats_on_delete(sender, instance, **kwargs):
            if related_field == 'topics':
                for topic in instance.topics.all():
                    topic.update_conversation_stats()
            else:
                related_object = getattr(instance, related_field)
                related_object.update_conversation_stats()


class ConversationTrendMixin:
    """
    Mixin containing the trends of the conversations associated with a given object, now including
    average call duration and sentiment. These are separated from the stats since these are never
    stored in memory, but are produced when required.
    """
    period_truncations = {
        'daily': models.functions.TruncDay('date'),
        'weekly': models.functions.TruncWeek('date'),
        'monthly': models.functions.TruncMonth('date'),
    }
    field_aggregations = {
        'count': models.Count('id'),
        'sentiment': models.Avg('sentiment'),
        'duration': models.Avg('duration')
    }

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

    def get_trend(self, period: str, per_topic: bool = False, field: str = None):
        """
        Obtain the evolution of a field over a time period. If specified, will return the evolution at a topic level.

        Args:
            period (str): The time period granularity to use for the trend. Must be one of "daily", "weekly", "monthly"
            per_topic (bool): Indicates whether to group by the time period AND the topic, or just by the time period
            field (str): Specifies what field to examine. If none is specified, the call count, average sentiment and
                average duration will be used.

        Returns:
            QuerySet: Trend of the specified fields
        """
        # Validate user input
        if period not in self.period_truncations:
            raise ValueError(f'Specify a period that is one of: "{'", "'.join(self.period_truncations.keys())}".')
        if field:
            if field not in self.field_aggregations:
                raise ValueError(f'Specify a field that is one of: "{'", "'.join(self.field_aggregations.keys())}".')
            else:
                aggregations = {field: self.field_aggregations[field]}
        else:
            aggregations = self.field_aggregations.copy()

        # Determine what columns to group by
        if per_topic:
            group_by_cols = ['topics__name', 'topics__id', 'period']
            renamed_cols = {
                'date': models.F('period'),
                'topic_name': models.F('topics__name'),
                'topic_id': models.F('topics__id')
            }
        else:
            group_by_cols = ['period']
            renamed_cols = {'date': models.F('period')}

        # Rename columns holding aggregation results
        old_col_names = aggregations.copy().keys()
        for col in old_col_names:
            if col != 'count':
                aggregations[f'avg_{col}'] = aggregations.pop(col)

        trend = (
            self.conversations_scope
            .annotate(period=self.period_truncations[period])
            .values(*group_by_cols)
            .annotate(**aggregations)
            .values(*aggregations.keys(), **renamed_cols)
            .order_by()
        )
        return trend


class Organization(models.Model, ConversationTrendMixin):
    """
    Organization: One of the many organizations that make use of the app. Separates the data for every group of users
    """

    name = models.CharField(max_length=100, unique=True, null=False)
    max_user_count = models.IntegerField(default=10)
    max_topic_count = models.IntegerField(default=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name',)
        verbose_name_plural = "Organizations"


class Topic(MetaSummaryAbstractModel, ConversationStatsAbstractModel, ConversationTrendMixin):
    """
    Topic: One of the many topics that can be discussed in the customer calls. These are to be detected by a
    multi-label classification task.
    """
    name = models.CharField(max_length=100, null=False)
    description = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='topics')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'organization')
        indexes = [
            models.Index(fields=['organization', 'name']),
        ]


class CustomUserManager(BaseUserManager):
    """
    This Model Manager is aimed at making sure that whenever a user is created, a Firebase User is associated to it
    """
    def create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set.')
        email = self.normalize_email(email)

        if not password:
            raise ValueError('The password must be set.')

        # Create the Firebase user first
        firebase_user = auth.create_user(
            email=email,
            password=password,
            display_name=username
        )
        uid = firebase_user.uid

        try:
            # Try creating a user with the Firebase UID as ID. If this fails, delete the Firebase User
            user = self.model(id=uid, username=username, email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user
        except Exception as e:
            auth.delete_user(uid)
            raise e

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user class, making use of the CustomUserManager and defining the email as main field
    """
    id = models.CharField(primary_key=True, max_length=128)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.username


class Employee(models.Model):
    """
    A versatile role. An employee can be an analyst, an agent, or a manager. Contains the basic attributes that all
    these user types inherit.
    - An analyst is a simple employee. Basically, a user with an organization label
    - An agent is an employee that can be tagged in Conversations
    - A manager is an agent that is related to another agent in a hierarchical relationship. Managers can hold calls.
    """
    ROLE_CHOICES = [
        ('ANALYST', 'Analyst'),
        ('AGENT', 'Agent'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='employees')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='employee', null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ANALYST')
    is_organization_admin = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.organization.name} - {self.get_role_display()}"

    class Meta:
        unique_together = ('user', 'organization')
        verbose_name_plural = "Employees"

    def delete(self, *args, **kwargs):
        user = self.user
        super().delete(*args, **kwargs)
        if user:
            user.delete()


class Analyst(Employee):
    """
    Analyst: A subclass of Employee, describing employees that do not take part in Conversations and only explore the
    broader trends of the topics being discussed.
    """
    class Meta:
        verbose_name_plural = "Analysts"


class Agent(Employee, MetaSummaryAbstractModel, ConversationStatsAbstractModel, ConversationTrendMixin):
    """
    Agent: A subclass of Employee describing Customer Center agents. Agents can appear related to Conversations, thus
    resulting in their associated trend, stats, and summary actions.
    """
    manager = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL,
        related_name='agents'
    )

    def save(self, *args, **kwargs):
        self.role = 'AGENT'

        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Agents"


class Customer(MetaSummaryAbstractModel, ConversationStatsAbstractModel, ConversationTrendMixin):
    """
    Customer: One of the many customers belonging to an organization. Customers have calls with one agent at a time.
    Calls act as a bridge between agents and customers
    """
    name = models.CharField(max_length=100, null=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='customers')
    created = models.DateTimeField(auto_now_add=True)

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
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='conversations')
    agent = models.ForeignKey(Agent, on_delete=models.PROTECT, related_name='conversations')
    created = models.DateTimeField(auto_now_add=True)

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
        Save applying checks to the given associated objects. These checks are placed here because they are relevant to
        the data model's integrity
        """
        # Ensure that agent and customer have the same associated organization
        if self.customer.organization != self.agent.organization:
            raise ValueError("The assigned customer and agent must be associated with the same organization.")
        super().save(*args, **kwargs)

    def process_transcript(self):
        """
        This method processes the call transcript to separate it into messages.
        """

        messages = re.split(r'(?=(<agent>:|<customer>:))', self.transcript)

        processed_messages = []
        for message_id, i in enumerate(range(1, len(messages), 2)):  # Avoid the leading empty string from the split
            speaker = messages[i].strip()
            message_text = messages[i + 1][len(speaker):].strip()  # The message following the speaker identifier
            processed_messages.append({
                'id': message_id,
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
