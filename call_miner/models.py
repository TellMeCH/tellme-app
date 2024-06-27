from django.db import models
from django.utils.text import slugify


class SlugMixin(models.Model):
    slug = models.SlugField(default="", unique=True, null=False)
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            if hasattr(self, 'organization') and self.organization:
                base_slug = slugify(f'{self.name}-{self.organization}')
            else:
                base_slug = slugify(self.name)
            unique_slug = base_slug
            num = 1
            while self.__class__.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{base_slug}-{num}'
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)


# Organization: Separates the app data according to the company making use of the app
class Organization(SlugMixin, models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Organizations"


class Topic(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='topics')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'organization')
        indexes = [
            models.Index(fields=['organization', 'name']),
        ]




# Agent: One of the many agents belonging to an organization
class Agent(SlugMixin, models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='agents')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Agents"
        indexes = [
            models.Index(fields=['organization', 'name']),
        ]


# Customer: One of the many customers belonging to an organization. Customers have calls with one agent at a time.
# Calls act as a bridge between agents and customers
class Customer(SlugMixin, models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='customers')

    class Meta:
        verbose_name_plural = "Customers"
        indexes = [
            models.Index(fields=['organization', 'name']),
        ]

    def __str__(self):
        return self.name


# Call: One of the many calls belonging to a customer and an agent.
# Among its attributes, it contains the path to the call recording, the call date and time, the call duration, the call
# transcript, the call topics mentioned, and the call sentiment
class Call(models.Model):
    path = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField()
    transcript = models.TextField()
    sentiment = models.FloatField(max_length=100)
    summary = models.TextField(blank=True)
    topics = models.ManyToManyField(Topic, related_name='calls')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='calls')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='calls')

    def __str__(self):
        return self.path

    class Meta:
        verbose_name_plural = "Calls"
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['agent']),
        ]


