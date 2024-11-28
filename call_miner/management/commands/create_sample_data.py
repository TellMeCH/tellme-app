import time
from datetime import datetime, timedelta
import random
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from firebase_admin import auth
from call_miner.models import Organization, Analyst, Agent, Topic, Customer, Conversation, User

COMMON_PASSWORD = 'tell_me_long'


class Command(BaseCommand):
    help = "Creates a sample set of data to test the app"

    def handle(self, *args, **options):
        try:
            self.stdout.write('Creating Sample Organizations')
            org = Organization(name='ACME Org', max_user_count=20)
            org.save()

            other_org = Organization(name='Competitors Inc.')
            other_org.save()
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Organizations: {e}')

        try:
            self.stdout.write('Creating 10 Sample Topics for ACME Org')
            topics = []
            for i in range(1, 11):
                topic = Topic(
                    name=f'Topic {i}',
                    description=f'This is topic number {i} for ACME Org.',
                    organization=org
                )
                topic.save()
                topics.append(topic)
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Topics: {e}')

        try:
            self.stdout.write('Creating Organization Admin')
            user = User.objects.create_user(
                username='org_admin',
                password=COMMON_PASSWORD,
                email='org_admin@acme.org',
            )
            auth.update_user(
                user.id,
                email_verified=True
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
                username='analyst_01',
                password=COMMON_PASSWORD,
                email='analyst_01@acme.org'
            )
            auth.update_user(
                user.id,
                email_verified=True
            )

            analyst = Analyst(
                organization=org,
                user=user,
                is_organization_admin=False,
            )
            analyst.save()

            user = User.objects.create_user(
                username='competitor_analyst_01',
                password=COMMON_PASSWORD,
                email='analyst_01@competitors.inc'
            )
            auth.update_user(
                user.id,
                email_verified=True
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
                username='manager_01',
                password=COMMON_PASSWORD,
                email='manager_01@acme.org'
            )
            auth.update_user(
                user.id,
                email_verified=True
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
                    username=f'agent_{i:02d}',
                    password=COMMON_PASSWORD,
                    email=f'agent_{i:02d}@acme.org'
                )
                auth.update_user(
                    user.id,
                    email_verified=True
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
            customer_names = [
                'John Smith', 'Jane Doe', 'Alice Brown', 'Charlie Black', 'Emma Green',
                'Michael White', 'Olivia Blue', 'Isabella Gray', 'William Gold', 'Sophia Silver',
                'Liam Violet', 'Lucas Yellow', 'Amelia Orange', 'Elijah Pink', 'Ethan Indigo',
                'James Crimson', 'Henry Teal', 'Alexander Cyan', 'Benjamin Magenta', 'Jackson Olive',
                'Sebastian Ruby', 'Matthew Jade', 'Joseph Emerald', 'David Amber', 'Owen Coral',
                'Gabriel Navy', 'Oliver Lilac', 'Mason Burgundy', 'Samuel Sapphire', 'Logan Pearl',
                'Levi Garnet', 'Jacob Quartz', 'Daniel Topaz', 'Jack Opal', 'Carter Onyx',
                'Isaac Amethyst', 'Noah Diamond', 'Thomas Jasper', 'Lucas Bronze', 'Ryan Steel',
                'Caleb Brass', 'Nathan Copper', 'Hunter Silverleaf', 'Chloe Violet', 'Scarlett Garnet',
                'Hazel Stone', 'Grace Ruby', 'Luna Quartz', 'Penelope Pearl', 'Ellie Topaz'
            ]

            customers = []
            for name in customer_names:
                customer = Customer(
                    name=name,
                    organization=org
                )
                customer.save()
                customers.append(customer)
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Customers: {e}')

        try:
            self.stdout.write('Creating 150 Sample Conversations for ACME Org Customers')
            base_date = datetime(2024, 1, 1)
            for i in range(150):
                agent = random.choice(agents)
                customer = random.choice(customers)
                naive_date = base_date + timedelta(days=random.randint(0, 364))  # Naive datetime
                date = timezone.make_aware(naive_date)  # Convert to aware datetime
                sentiment = random.uniform(0, 5)  # Sentiment between 0 and 5
                duration = random.randint(30, 1800)  # Random duration in seconds

                conversation = Conversation(
                    path=f'/random/path/{i}',
                    date=date,
                    duration=duration,
                    transcript=f"""
                    <agent>: Hello, {agent.user.username}, how can I assist you today?
                    <customer>: Hi, I have an issue with my product. It's acting weird.
                    <agent>: Could you describe the problem?
                    <customer>: Yes, it keeps making a strange noise and flashing red lights.
                    <agent>: That doesn't sound right. Let me look into that for you.
                    <customer>: Thank you, it's driving me crazy!
                    <agent>: Hello, {agent.user.username}, how can I assist you today?
                    <customer>: Hi, I have an issue with my product. It's acting weird.
                    <agent>: Could you describe the problem?
                    <customer>: Yes, it keeps making a strange noise and flashing red lights.
                    <agent>: That doesn't sound right. Let me look into that for you.
                    <customer>: Thank you, it's driving me crazy!
                    <agent>: Hello, {agent.user.username}, how can I assist you today?
                    <customer>: Hi, I have an issue with my product. It's acting weird.
                    <agent>: Could you describe the problem?
                    <customer>: Yes, it keeps making a strange noise and flashing red lights.
                    <agent>: That doesn't sound right. Let me look into that for you.
                    <customer>: Thank you, it's driving me crazy!
                    <agent>: Hello, {agent.user.username}, how can I assist you today?
                    <customer>: Hi, I have an issue with my product. It's acting weird.
                    <agent>: Could you describe the problem?
                    <customer>: Yes, it keeps making a strange noise and flashing red lights.
                    <agent>: That doesn't sound right. Let me look into that for you.
                    <customer>: Thank you, it's driving me crazy!
                    """,
                    sentiment=sentiment,
                    title=f"Conversation {i + 1} - {agent.user.username} assists {customer.name}",
                    summary=f"Agent {agent.user.username} assisted customer {customer.name} with an issue.",
                    input_tokens=random.randint(50, 200),
                    output_tokens=random.randint(20, 100),
                    customer=customer,
                    agent=agent
                )
                conversation.save()

                # Assign random topics
                random_topics = random.sample(topics, random.randint(1, 3))
                conversation.topics.add(*random_topics)
                conversation.save()
        except Exception as e:
            raise CommandError(f'Failed creation of Conversations: {e}')

        try:
            self.stdout.write('Setting the last 2 Sample Topics as Inactive')
            time.sleep(30)
            for i in range(9, 11):
                topic = Topic.objects.filter(name=f'Topic {i}', organization=org)[0]
                topic.is_active = False
                topic.save()
        except Exception as e:
            raise CommandError(f'Failed setting topics to inactive: {e}')

        try:
            self.stdout.write('Creating Superuser')
            user = User.objects.create_superuser(
                username='altogi',
                password=COMMON_PASSWORD,
                email='altogi@tellme.ch'
            )
            auth.update_user(
                user.id,
                email_verified=True
            )
        except Exception as e:
            raise CommandError(f'Failed to create Superuser: {e}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created expanded sample data')
        )
