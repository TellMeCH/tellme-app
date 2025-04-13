from django.apps import AppConfig
import firebase_admin


class CallMinerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'call_miner'

    def ready(self):
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            firebase_admin.initialize_app()

        # Import signals from module
        import call_miner.signals

        # Import Extensions for drf-spectacular
        import call_miner.authentication_extensions
