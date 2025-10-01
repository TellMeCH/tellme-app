from django.apps import AppConfig
import firebase_admin
import posthog
from django.conf import settings


class CallMinerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tellme.call_miner'

    def ready(self):
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            firebase_admin.initialize_app()

        # Initialize PostHog
        if hasattr(settings, 'POSTHOG_API_KEY') and settings.POSTHOG_API_KEY:
            posthog.api_key = settings.POSTHOG_API_KEY
            posthog.host = settings.POSTHOG_HOST

        # Import signals from module
        import tellme.call_miner.signals

        # Import Extensions for drf-spectacular
        import tellme.call_miner.authentication_extensions
