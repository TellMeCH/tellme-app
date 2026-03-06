import time
import hashlib
import os
import uuid
from datetime import datetime, timedelta, date
import random
from django.conf import settings
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from firebase_admin import auth
from tellme.call_miner.models import Organization, OrganizationAPIKey, Analyst, Agent, Topic, SuggestedTopic, Customer, Conversation, User

COMMON_PASSWORD = 'tell_me_long'

# Sample data for generating realistic customer information
FIRST_NAMES = [
    'Anna', 'Beat', 'Carla', 'Daniel', 'Eva', 'Felix', 'Greta', 'Hans', 'Ines', 'Jakob',
    'Katja', 'Lars', 'Maria', 'Nils', 'Olivia', 'Peter', 'Quirin', 'Rita', 'Stefan', 'Tina',
    'Ulrich', 'Vera', 'Werner', 'Xenia', 'Yves', 'Zora', 'Adrian', 'Brigitte', 'Christian', 'Doris',
    'Ernst', 'Franziska', 'Georg', 'Heidi', 'Ivan', 'Julia', 'Klaus', 'Lena', 'Martin', 'Nicole'
]

LAST_NAMES = [
    'Müller', 'Schmidt', 'Schneider', 'Fischer', 'Weber', 'Meyer', 'Wagner', 'Becker', 'Schulz', 'Hoffmann',
    'Schäfer', 'Koch', 'Bauer', 'Richter', 'Klein', 'Wolf', 'Schröder', 'Neumann', 'Schwarz', 'Zimmermann',
    'Braun', 'Krüger', 'Hofmann', 'Hartmann', 'Lange', 'Schmitt', 'Werner', 'Schmitz', 'Krause', 'Meier',
    'Lehmann', 'Schmid', 'Schulze', 'Maier', 'Köhler', 'Herrmann', 'König', 'Walter', 'Mayer', 'Huber'
]

# Swiss postal codes (selection of real postcodes)
SWISS_POSTCODES = [
    '8001', '8002', '8003', '8004', '8005', '8006', '8008', '8032', '8037', '8044',  # Zurich
    '3001', '3003', '3004', '3005', '3006', '3007', '3008', '3010', '3011', '3012',  # Bern
    '4001', '4002', '4003', '4051', '4052', '4053', '4054', '4055', '4056', '4057',  # Basel
    '1200', '1201', '1202', '1203', '1204', '1205', '1206', '1207', '1208', '1209',  # Geneva
    '1000', '1001', '1003', '1004', '1005', '1006', '1007', '1008', '1010', '1011',  # Lausanne
    '6900', '6901', '6902', '6903', '6904', '6905', '6906', '6907', '6908', '6909',  # Lugano
    '9000', '9001', '9004', '9006', '9007', '9008', '9010', '9011', '9012', '9014'   # St. Gallen
]


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

    def generate_customer_data(self):
        """Generate realistic customer data"""
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)

        # Generate birth date (age between 18 and 80)
        today = date.today()
        min_age = 18
        max_age = 80
        birth_year = today.year - random.randint(min_age, max_age)
        birth_month = random.randint(1, 12)

        # Ensure valid day for the month
        if birth_month == 2:
            birth_day = random.randint(1, 28)  # February (safe for all years)
        elif birth_month in [4, 6, 9, 11]:
            birth_day = random.randint(1, 30)  # Months with 30 days
        else:
            birth_day = random.randint(1, 31)  # Months with 31 days

        birth_date = date(birth_year, birth_month, birth_day)
        postcode = random.choice(SWISS_POSTCODES)

        # Generate loyalty number (format: ABC-123456)
        loyalty_number = f"{random.choice(['ABC', 'DEF', 'GHI', 'JKL', 'MNO', 'PQR', 'STU', 'VWX', 'YZA'])}-{random.randint(100000, 999999)}"

        return {
            'first_name': first_name,
            'last_name': last_name,
            'birth_date': birth_date,
            'postcode': postcode,
            'loyalty_number': loyalty_number
        }

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
            # Fixed UUID so the AudioHook reference-implementation test suite can be pointed
            # at this org without any manual setup. Set [OpenParameters] organizationId to
            # this value in testconfig.cfg when running the reference impl tests locally.
            AUDIOHOOK_TEST_ORG_ID = uuid.UUID('deadbeef-dead-4bee-dead-beefdeadbeef')

            org = Organization(
                name='ACME Org',
                max_user_count=20,
                transcription_method='groq',
                enrichment_method='vertexai',
                language='de',
                revenue_search_prefix='pkz.ch/de/',
                cx_system_org_id=AUDIOHOOK_TEST_ORG_ID,
            )
            org.save()

            # Add Jira ticket configuration if environment variables are available
            ticket_server = os.environ.get('TICKET_SERVER')
            ticket_account = os.environ.get('TICKET_ACCOUNT')
            ticket_key = os.environ.get('TICKET_KEY')
            ticket_project = os.environ.get('TICKET_PROJECT')

            if ticket_server and ticket_account and ticket_key and ticket_project:
                self.stdout.write('Adding Jira ticket configuration from environment variables')
                org.ticket_server = ticket_server
                org.ticket_account = ticket_account
                org.ticket_project = ticket_project
                org.store_ticket_key(ticket_key)
                org.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully configured Jira: {ticket_server} (account: {ticket_account}, project: {ticket_project})'))
            else:
                self.stdout.write(self.style.WARNING('Skipping Jira configuration (TICKET_SERVER, TICKET_ACCOUNT, TICKET_KEY, and TICKET_PROJECT not all set)'))

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
                customer_data = self.generate_customer_data()
                customer = Customer(
                    external_id=hashlib.sha256(f'{i + 1}{int(time.time())}'.encode()).hexdigest(),
                    organization=org,
                    first_name=customer_data['first_name'],
                    last_name=customer_data['last_name'],
                    birth_date=customer_data['birth_date'],
                    postcode=customer_data['postcode'],
                    loyalty_number=customer_data['loyalty_number']
                )
                customer.save()
                customers.append(customer)
            self.stdout.write('Successfully created 50 Sample Customers with realistic data')
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Customers: {e}')

        try:
            self.stdout.write(f'Creating {len(CONVERSATION_DATA)} Sample Conversations for ACME Org Customers')
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

                try:
                    conversation = Conversation(
                        path=f'/random/path/{i}',
                        date=date,
                        duration=duration,
                        transcript=data['transcript'],
                        sentiment=sentiment,
                        starting_sentiment=starting_sentiment,
                        ending_sentiment=ending_sentiment,
                        title=f"Conversation {i + 1} - {agent.user.email} assists {customer.first_name} {customer.last_name}",
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
                except Exception:
                   continue

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
                email='alvaro.tomasgil@tell-me.ch',
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
            self.stdout.write(f'  [OpenParameters] organizationId = {org.cx_system_org_id}')
            self.stdout.write(f'  [OpenParameters] customConfig = {{"agent_id": {manager.id}}}')
        except Exception as e:
            raise CommandError(f'Failed to create Organization API Key: {e}')

        self.stdout.write(self.style.SUCCESS('Successfully created expanded sample data'))
