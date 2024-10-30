from django.apps import AppConfig
import firebase_admin


class CallMinerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'call_miner'

    def ready(self):
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            firebase_admin.initialize_app()

        # Register the signals when the app is ready
        from call_miner.models import Topic, Agent, Customer, Conversation
        Topic.register_signals(Conversation, related_field='topics')
        Agent.register_signals(Conversation, related_field='agent')
        Customer.register_signals(Conversation, related_field='customer')
