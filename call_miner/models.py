import re
import uuid
import secrets
import hashlib
import datetime
import zoneinfo
import threading
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from firebase_admin import auth
from django.contrib.contenttypes.models import ContentType
from call_miner.utils.summary_mining import condense_summaries
import call_miner.utils.email_utils as email
from django.db.models.signals import post_save, post_delete


class MetaSummaryAbstractModel(models.Model):
    """
    An abstract model that handles the creation and retrieval of summaries objects for Agent, Customer, and Topic models
    """
    summary = models.JSONField(null=True)
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
            new_summary = condense_summaries(relevant_summaries, trace_data)
            self.summary = new_summary
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

    @property
    def topics_scope(self):
        """
        Retrieves the topics associated to the object.
        If the object is an Organization, fetches with a direct filter
        If the object is not an Organization, fetches all topics of the associated organization
        """
        if isinstance(self, Organization):
            return Topic.objects.filter(organization=self)
        else:
            return Topic.objects.filter(organization=self.organization)

    def get_trend(self, period: str, per_topic: bool = False, field: str = None, start_date: datetime.datetime = None):
        """
        Obtain the evolution of a field over a time period. If specified, will return the evolution at a topic level.

        Args:
            period (str): The time period granularity to use for the trend. Must be one of "daily", "weekly", "monthly"
            per_topic (bool): Indicates whether to group by the time period AND the topic, or just by the time period
            field (str): Specifies what field to examine. If none is specified, the call count, average sentiment and
                average duration will be used.
            start_date (datetime): If provided, only include conversations on or after this date.

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

        qs = self.conversations_scope
        if start_date:
            qs = qs.filter(date__gte=start_date)

        trend = (
            qs
            .annotate(period=self.period_truncations[period])
            .values(*group_by_cols)
            .annotate(**aggregations)
            .values(*aggregations.keys(), **renamed_cols)
            .order_by()
        )
        return trend

    def get_overview(self, per_topic: bool = False):
        """
        Summarizes conversation metrics for the last two months (count, average sentiment, average duration).
        If per_topic=True, results are grouped by each topic found in ``self.topics_scope``; otherwise,
        a single "general" grouping is returned.

        Args:
            per_topic (bool): If True, group results by topic. Otherwise, return a single "general" entry.

        Returns:
            dict: A nested dictionary of the form:
                {
                    <topic or 'general'>: {
                        'avg_sentiment': {
                            '2023-01-01T00:00:00Z': X,
                            '2023-02-01T00:00:00Z': Y,
                            'change': Z
                        },
                        'avg_duration': ...,
                        'count': ...
                    },
                    ...
                }
        """
        # Determine the relevant months for the overview
        utc = zoneinfo.ZoneInfo("UTC")
        this_month_start = datetime.datetime.now(tz=utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (this_month_start - datetime.timedelta(days=1)).replace(day=1)
        prior_month_start = (last_month_start - datetime.timedelta(days=1)).replace(day=1)
        last_month = last_month_start.strftime('%Y-%m')
        prior_month = prior_month_start.strftime('%Y-%m')

        # Get trend data, aggregated by month
        trend_data = list(self.get_trend(
            period='monthly', field=None, per_topic=per_topic, start_date=prior_month_start
        ))

        # Relevant KPIs
        relevant_metrics = [f'avg_{name}' for name in self.field_aggregations.keys() if name != 'count']
        relevant_metrics.append('count')

        overview_data = {}
        if per_topic:
            topic_list = [topic.name for topic in self.topics_scope]
        else:
            topic_list = ['general']

        for topic in topic_list:
            this_data = {metric: {} for metric in relevant_metrics}

            # Iterate over the trend, extract relevant items
            for item in trend_data:
                if per_topic:
                    name_match = item['topic_name'] == topic
                else:
                    name_match = True
                item_month = item['date'].strftime('%Y-%m')
                if item_month in (last_month, prior_month) and name_match:
                    for metric in relevant_metrics:
                        this_data[metric][item_month] = item[metric]

            # Populate missing months and calculate percentage change
            for metric in relevant_metrics:
                for month in (last_month, prior_month):
                    if month not in this_data[metric]:
                        this_data[metric][month] = 0

                previous = this_data[metric][prior_month]
                latest = this_data[metric][last_month]
                if previous != 0:
                    this_data[metric]['change'] = (latest - previous) * 100 / previous
                else:
                    this_data[metric]['change'] = None

            # Retrieve trends for determining the month's most popular topic
            if not per_topic:
                topic_popularities = list(self.get_trend(
                    period='monthly', field='count', per_topic=True, start_date=prior_month_start
                ))
                this_data['most_popular_topic'] = {last_month: None, prior_month: None}
                max_counts = {last_month: 0, prior_month: 0}
                for item in topic_popularities:
                    item_month = item['date'].strftime('%Y-%m')
                    if item_month in max_counts.keys():
                        if item['count'] > max_counts[item_month]:
                            max_counts[item_month] = item['count']
                            this_data['most_popular_topic'][item_month] = item['topic_name']

            overview_data[topic] = this_data
        return overview_data


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


class OrganizationAPIKey(models.Model):
    """
    Stores a hashed API key for an organization, along with meta information
    such as creation date, expiration date, and name for reference.
    """
    hashed_api_key = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=100, help_text="Descriptive name for the API key.")
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='api_keys'
    )
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField()

    MAX_KEYS_PER_ORG = 3
    KEY_LIFETIME = 90

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

    class Meta:
        unique_together = ('organization', 'name')
        verbose_name_plural = 'Organization API Keys'

    @classmethod
    def create_key(cls, organization, name):
        """
        Creates a new API key for the given organization, ensuring the org does not exceed its allowed maximum number
        of keys.

        :param organization: The Organization instance
        :param name: A descriptive name for this key
        :return: The *plaintext* API key (once), which should be stored securely by the user
        """

        # Check if the organization already has max_keys
        if organization.api_keys.count() >= cls.MAX_KEYS_PER_ORG:
            raise ValueError(f"Organization '{organization.name}' has reached the max number of keys allowed.")

        # Generate and hash an API key
        plain_key = secrets.token_urlsafe(43)
        hashed_key = hashlib.sha256(plain_key.encode('utf-8')).hexdigest()

        # Create the database entry with the hashed key
        api_key = cls.objects.create(
            hashed_api_key=hashed_key,
            name=name,
            organization=organization,
            expires=timezone.now() + datetime.timedelta(days=cls.KEY_LIFETIME)
        )

        # Return the plaintext so the caller can store it securely
        return plain_key


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
    VALID_AUTH_TYPES = ['password', 'google', 'microsoft']

    def create_user(self, email, auth_type, first_name, last_name, password=None, is_superuser=False, **extra_fields):
        if not email:
            raise ValueError('The Email must be set.')
        email = self.normalize_email(email)

        # Check the valid authentication type
        if auth_type not in self.VALID_AUTH_TYPES:
            valid_auth_types_str = '", "'.join(self.VALID_AUTH_TYPES)
            raise ValueError(f'The authentication type must be one of "{valid_auth_types_str}"')

        # Check that superuser accounts can only work with password authentication
        if is_superuser:
            if auth_type != 'password':
                raise ValueError('Superusers can only be created with auth_type set to "password"')
            if not password:
                raise ValueError('The password must be set for creating superuser accounts')
        else:  # Check that the password is not specified for non-superuser accounts
            if auth_type == 'password' and password:
                raise ValueError('User passwords are only set after sending and processing the password reset link')

        # Create the user's UID
        uid = uuid.uuid4().hex

        # Only create the Firebase user if the login method is email + password
        if auth_type == 'password':
            auth.create_user(
                email=email,
                password=password,
                display_name=email,
                uid=uid
            )

        # Try creating a user with the Firebase UID as ID. If this fails, delete the Firebase User
        try:
            user = self.model(
                id=uid,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_superuser=is_superuser,
                auth_type=auth_type,
                **extra_fields
            )
            user.save(using=self._db)
            return user
        except Exception as e:
            if auth_type == 'password':
                auth.delete_user(uid)
            raise e

    def create_superuser(self, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            auth_type='password',
            password=password,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user class, making use of the CustomUserManager and defining the email as main field
    """
    id = models.CharField(primary_key=True, max_length=128)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, default='John')
    last_name = models.CharField(max_length=100, default='Doe')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    auth_type = models.CharField(
        max_length=20,
        choices=[(name, name.capitalize()) for name in CustomUserManager.VALID_AUTH_TYPES],
        default='password'
    )

    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def delete(self, using=None, keep_parents=False):
        """
        Whenever this method is called, delete the corresponding Firebase user first
        and then proceed with deleting from Django's DB.
        No error will be raised in case user can't be found in Firebase
        """
        try:
            auth.delete_user(self.pk)  # self.pk == self.id
        except auth.UserNotFoundError:
            pass
        return super().delete(using=using, keep_parents=keep_parents)

    @staticmethod
    def _send_email_in_background(*args, **kwargs):
        try:
            email.send_email_with_link(*args, **kwargs)
        except Exception as e:
            print(f"Failed to send verification email: {e}")

    def send_onboarding_email(self):
        """
        Simple method to onboard a user by verifying its email. This will be triggered if the serializer create/update
        methods are called.
        """
        if self.auth_type == 'password':
            link = auth.generate_password_reset_link(self.email)
            method = 'email and password'
        else:
            link = settings.FRONTEND_PATH
            method = self.auth_type.capitalize() + ' account'

        full_name = self.first_name + ' ' + self.last_name
        threading.Thread(
            target=self._send_email_in_background,
            args=(full_name, self.email, link, method, email.ONBOARDING_TEMPLATE, email.ONBOARDING_SUBJECT)
        ).start()

    def send_verification_email(self):
        """
        Simple method to send an email verification link to a new user.
        """
        if self.auth_type == 'password':
            method = 'email and password'
        else:
            method = self.auth_type.capitalize() + ' account'

        link = auth.generate_email_verification_link(self.email)
        full_name = self.first_name + ' ' + self.last_name
        threading.Thread(
            target=self._send_email_in_background,
            args=(full_name, self.email, link, method, email.VERIFICATION_TEMPLATE, email.VERIFICATION_SUBJECT)
        ).start()


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
        return f"{self.user.email} - {self.organization.name} - {self.get_role_display()}"

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
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='customers')
    external_id = models.CharField(max_length=128, null=False)  # Comes from call recording software
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('organization', 'external_id')
        verbose_name_plural = "Customers"
        indexes = [
            models.Index(fields=['organization', 'external_id']),
        ]

    def __str__(self):
        return f"Customer [external_id={self.external_id} | org={self.organization_id}]"


class Conversation(models.Model):
    """
    Conversation: One of the many calls belonging to a customer and an agent.
    Among its attributes, it contains the path to the call recording, the call date and time, the call duration,
    the call transcript, the call topics mentioned, and the call sentiment
    """
    path = models.CharField(max_length=500)
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

        # Ensure that the call sentiment is within the expected bounds
        if not (0 <= self.sentiment <= 5):
            raise ValueError(f'Sentiment score must be between 0 and 5. Provided value was {self.sentiment}')
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
