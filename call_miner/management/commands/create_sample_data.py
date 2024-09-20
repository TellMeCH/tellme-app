from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from call_miner.models import Organization, Analyst, Agent, Topic, Customer, Conversation

COMMON_PASSWORD = 'tell_me_long'
CALL_TRANSCRIPT = """
<agent>: Good afternoon, what can I do for you?
<customer>: Hello, there is a snake in my pickles!
<agent>: Oh dear! That's for sure not Kosher!
<customer>: I shart my pants.
"""
CALL_SUMMARY = "Reptilian causes defecation."


class Command(BaseCommand):
    help = "Creates a sample set of data to test the app"

    def handle(self, *args, **options):
        try:
            self.stdout.write('Creating Sample Organizations')
            org = Organization(name='ACME Org')
            org.save()

            other_org = Organization(name='Competitors Inc.')
            other_org.save()
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Organizations: {e}')

        try:
            self.stdout.write('Creating Sample Topics')
            topic_1 = Topic(
                name='Animals',
                description='The animal kingdom is upon us.',
                organization=org
            )
            topic_1.save()

            topic_2 = Topic(
                name='Preserved Foods',
                description='Excessive harvests should be kept for future years.',
                organization=org
            )
            topic_2.save()
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Topics: {e}')

        try:
            self.stdout.write('Creating Sample Analysts')
            user = User.objects.create_user(
                username='analyst_01',
                password=COMMON_PASSWORD,
                email='analyst_01@acme.org'
            )
            analyst = Analyst(
                organization=org,
                user=user
            )
            analyst.save()

            user = User.objects.create_user(
                username='competitor_analyst_01',
                password=COMMON_PASSWORD,
                email='analyst_01@competitors.inc'
            )
            competitor_analyst = Analyst(
                organization=other_org,
                user=user
            )
            competitor_analyst.save()
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Analysts: {e}')

        try:
            self.stdout.write('Creating Sample Agents')
            user = User.objects.create_user(
                username='manager_01',
                password=COMMON_PASSWORD,
                email='manager_01@acme.org'
            )
            manager = Agent(
                organization=org,
                user=user
            )
            manager.save()

            user = User.objects.create_user(
                username='agent_01',
                password=COMMON_PASSWORD,
                email='agent_01@acme.org'
            )
            agent = Agent(
                organization=org,
                user=user,
                manager=manager
            )
            agent.save()
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Agents: {e}')

        try:
            self.stdout.write('Creating Sample Customer')
            customer = Customer(
                name='Anna Boweles',
                organization=org
            )
            customer.save()
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Customer: {e}')

        try:
            self.stdout.write('Creating Sample Conversation')
            conversation = Conversation(
                path='/random/path/in/gcs/',
                date='2024-03-15',
                duration=15,
                transcript=CALL_TRANSCRIPT,
                sentiment=0.8,
                summary=CALL_SUMMARY,
                input_tokens=50,
                output_tokens=15,
                customer=customer,
                agent=agent
            )
            conversation.save()
            conversation.topics.add(topic_1, topic_2)
            conversation.save()
        except Exception as e:
            raise CommandError(f'Failed creation of Conversation: {e}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data')
        )
