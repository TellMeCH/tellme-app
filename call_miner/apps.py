from django.apps import AppConfig
import firebase_admin
from django.conf import settings


class CallMinerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'call_miner'

    def ready(self):
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            firebase_admin.initialize_app()

        # Check that the OpenAI API Key has been provided
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

        # Register the signals when the app is ready
        from call_miner.models import Topic, Agent, Customer, Conversation
        Topic.register_signals(Conversation, related_field='topics')
        Agent.register_signals(Conversation, related_field='agent')
        Customer.register_signals(Conversation, related_field='customer')
