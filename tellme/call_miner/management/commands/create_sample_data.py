import time
import hashlib
import os
from datetime import datetime, timedelta
import random
from django.conf import settings
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from firebase_admin import auth
from tellme.call_miner.models import Organization, OrganizationAPIKey, Analyst, Agent, Topic, SuggestedTopic, Customer, Conversation, User

COMMON_PASSWORD = 'tell_me_long'


class Command(BaseCommand):
    help = "Creates a sample set of data to test the app. Meant to be run locally."

    def get_available_industries(self):
        """Dynamically get available industries from the sample_data module"""
        sample_data_dir = os.path.join(os.path.dirname(__file__), '..', 'sample_data')
        industries = []

        if os.path.exists(sample_data_dir):
            for file in os.listdir(sample_data_dir):
                if file.endswith('.py') and file != '__init__.py':
                    industry = file[:-3]  # Remove .py extension
                    industries.append(industry)

        return sorted(industries)

    def add_arguments(self, parser):
        available_industries = self.get_available_industries()
        default_industry = 'insurance' if 'insurance' in available_industries else (available_industries[0] if available_industries else 'insurance')

        parser.add_argument(
            '--industry',
            type=str,
            default=default_industry,
            choices=available_industries,
            help=f'Industry type for sample data (default: {default_industry}, available: {", ".join(available_industries)})'
        )

    def get_industry_data(self, industry):
        """Import and return industry-specific sample data"""
        try:
            # Dynamic import based on industry
            module = __import__(f'tellme.call_miner.management.sample_data.{industry}',
                              fromlist=['TOPIC_DATA', 'SUGGESTED_TOPIC_DATA', 'CONVERSATION_DATA'])

            TOPIC_DATA = getattr(module, 'TOPIC_DATA')
            SUGGESTED_TOPIC_DATA = getattr(module, 'SUGGESTED_TOPIC_DATA')
            CONVERSATION_DATA = getattr(module, 'CONVERSATION_DATA')

            return TOPIC_DATA, SUGGESTED_TOPIC_DATA, CONVERSATION_DATA
        except (ImportError, AttributeError) as e:
            available_industries = self.get_available_industries()
            raise CommandError(f'Failed to import data for industry "{industry}": {e}. Available industries: {", ".join(available_industries)}')

    def handle(self, *args, **options):
        industry = options['industry']
        self.stdout.write(f'Creating sample data for industry: {industry}')

        # Get industry-specific data
        TOPIC_DATA, SUGGESTED_TOPIC_DATA, CONVERSATION_DATA = self.get_industry_data(industry)
        try:
            self.stdout.write('Creating Sample Organizations')
            org = Organization(
                name='ACME Org',
                max_user_count=20,
                enrichment_method='vertexai',
                language='de',
                revenue_search_prefix='pkz.ch/de/'
            )
            org.save()

            other_org = Organization(name='Competitors Inc.')
            other_org.save()
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Organizations: {e}')

        try:
            self.stdout.write('Creating 10 Sample Topics for ACME Org')

            topics = []
            for data in TOPIC_DATA:
                topic = Topic(
                    name=data["name"],
                    description=data["description"],
                    organization=org
                )
                topic.save()
                topics.append(topic)

            self.stdout.write('Successfully created 10 Sample Topics for ACME Org')

        except Exception as e:
            raise CommandError(f'Failed creation of Sample Topics: {e}')

        try:
            self.stdout.write('Creating 2 Sample Suggested Topics for ACME Org')

            suggested_topics = []
            for data in SUGGESTED_TOPIC_DATA:
                suggested_topic = SuggestedTopic(
                    name=data["name"],
                    description=data["description"],
                    organization=org
                )
                suggested_topic.save()
                suggested_topics.append(suggested_topic)

            self.stdout.write('Successfully created 2 Sample Suggested Topics for ACME Org')

        except Exception as e:
            raise CommandError(f'Failed creation of Sample Suggested Topics: {e}')

        try:
            self.stdout.write('Creating Organization Admin')
            user = User.objects.create_user(
                email='org_admin@acme.org',
                auth_type='password',
                first_name='Org Admin',
                last_name='Acme'
            )
            auth.update_user(
                user.id,
                email_verified=True,
                password=COMMON_PASSWORD,
            )

            analyst = Analyst(
                organization=org,
                user=user,
                is_organization_admin=True,
            )
            analyst.save()

        except Exception as e:
            raise CommandError(f'Failed creation of Organization Admin: {e}')

        try:
            self.stdout.write('Creating Sample Analysts')
            user = User.objects.create_user(
                email='analyst_01@acme.org',
                auth_type='password',
                first_name='Analyst 1',
                last_name='Acme'
            )
            auth.update_user(
                user.id,
                email_verified=True,
                password=COMMON_PASSWORD
            )

            analyst = Analyst(
                organization=org,
                user=user,
                is_organization_admin=False,
            )
            analyst.save()

            user = User.objects.create_user(
                email='analyst_01@competitors.inc',
                auth_type='password',
                first_name='Analyst 1',
                last_name='Competitors'
            )
            auth.update_user(
                user.id,
                email_verified=True,
                password=COMMON_PASSWORD
            )

            competitor_analyst = Analyst(
                organization=other_org,
                user=user
            )
            competitor_analyst.save()
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Analysts: {e}')

        try:
            self.stdout.write('Creating 15 Sample Agents under manager_01')
            user = User.objects.create_user(
                email='manager_01@acme.org',
                auth_type='password',
                first_name='Manager 1',
                last_name='Acme'
            )
            auth.update_user(
                user.id,
                email_verified=True,
                password=COMMON_PASSWORD
            )

            manager = Agent(
                organization=org,
                user=user,
                is_organization_admin=False,
            )
            manager.save()

            agents = []
            for i in range(1, 17):  # Creating agent_02 to agent_16
                user = User.objects.create_user(
                    email=f'agent_{i:02d}@acme.org',
                    auth_type='password',
                    first_name=f'Agent {i}',
                    last_name='Acme'
                )
                auth.update_user(
                    user.id,
                    email_verified=True,
                    password=COMMON_PASSWORD
                )

                agent = Agent(
                    organization=org,
                    user=user,
                    manager=manager
                )
                agent.save()
                agents.append(agent)
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Agents: {e}')

        try:
            self.stdout.write('Creating 50 Sample Customers for ACME Org')
            customers = []
            for i in range(50):
                customer = Customer(
                    external_id=hashlib.sha256(f'{i + 1}{int(time.time())}'.encode()).hexdigest(),
                    organization=org
                )
                customer.save()
                customers.append(customer)
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Customers: {e}')

        try:
            self.stdout.write(f'Creating {CONVERSATION_DATA} Sample Conversations for ACME Org Customers')
            base_date = datetime.now() - timedelta(days=90)
            for i, data in enumerate(CONVERSATION_DATA):
                agent = random.choice(agents)
                customer = random.choice(customers)
                naive_date = base_date + timedelta(days=random.randint(0, 90))  # Naive datetime
                date = timezone.make_aware(naive_date)  # Convert to aware datetime
                sentiment = random.uniform(0, 5)  # Sentiment between 0 and 5
                starting_sentiment = random.uniform(0, 5)
                ending_sentiment = random.uniform(0, 5)
                duration = random.randint(30, 1800)  # Random duration in seconds

                conversation = Conversation(
                    path=f'/random/path/{i}',
                    date=date,
                    duration=duration,
                    transcript=data['transcript'],
                    sentiment=sentiment,
                    starting_sentiment=starting_sentiment,
                    ending_sentiment=ending_sentiment,
                    title=f"Conversation {i + 1} - {agent.user.email} assists {customer.external_id}",
                    summary=data['summary'],
                    input_tokens=random.randint(50, 200),
                    output_tokens=random.randint(20, 100),
                    revenue_at_stake=random.random() * 800 + 100,
                    resolved=random.random() > 0.5,
                    customer=customer,
                    agent=agent
                )
                conversation.save()

                # Assign random topics
                conversation.topics.add(*data['topics'])
                
                # Assign suggested topics if they exist in the data
                if 'suggested_topics' in data and data['suggested_topics']:
                    conversation.suggested_topics.add(*data['suggested_topics'])
                
                conversation.save()
        except Exception as e:
            raise CommandError(f'Failed creation of Conversations: {e}')

        try:
            self.stdout.write('Setting the last 2 Sample Topics as Inactive')
            time.sleep(1)
            for i in range(8, 10):
                topic = Topic.objects.get(name=TOPIC_DATA[i]['name'], organization=org)
                topic.is_active = False
                topic.save()
        except Exception as e:
            raise CommandError(f'Failed setting topics to inactive: {e}')

        try:
            self.stdout.write('Creating Superuser')
            user = User.objects.create_superuser(
                email='altogi@tellme.ch',
                password=COMMON_PASSWORD,
                first_name='Alvaro',
                last_name='Tomas Gil'
            )
            auth.update_user(
                user.id,
                email_verified=True
            )
        except Exception as e:
            raise CommandError(f'Failed to create Superuser: {e}')

        try:
            self.stdout.write('Creating Superuser Account for Invoking Processing Pipeline')
            user = User.objects.create_superuser(
                email=settings.PROCESSING_PIPELINE_USER,
                password=COMMON_PASSWORD,
                first_name='Processing',
                last_name=settings.TELLME_ENV
            )
            auth.update_user(
                user.id,
                email_verified=True
            )
        except Exception as e:
            raise CommandError(f'Failed to create Superuser: {e}')

        try:
            self.stdout.write('Creating Organization API Key for Processing')
            plain_key = OrganizationAPIKey.create_key(org, name='test_key')
            self.stdout.write(f'Created API Key for {org.name}: {plain_key}')
        except Exception as e:
            raise CommandError(f'Failed to create Organization API Key: {e}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created expanded sample data')
        )
