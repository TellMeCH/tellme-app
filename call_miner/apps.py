from django.apps import AppConfig


class CallMinerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'call_miner'

    def ready(self):
        from call_miner.models import Topic, Agent, Customer, Conversation
        # Register the signals when the app is ready
        Topic.register_signals(Conversation, related_field='topics')
        Agent.register_signals(Conversation, related_field='agent')
        Customer.register_signals(Conversation, related_field='customer')
