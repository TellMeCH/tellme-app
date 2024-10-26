import os
from django.apps import AppConfig
import firebase_admin
from firebase_admin import credentials


class CallMinerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'call_miner'

    def ready(self):
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            firebase_config = os.getenv('FIREBASE_CONFIG')
            if firebase_config:
                cred = credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)
            else:
                raise ValueError("FIREBASE_CONFIG environment variable is not set")

        # Register the signals when the app is ready
        from call_miner.models import Topic, Agent, Customer, Conversation
        Topic.register_signals(Conversation, related_field='topics')
        Agent.register_signals(Conversation, related_field='agent')
        Customer.register_signals(Conversation, related_field='customer')
