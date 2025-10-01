from django.apps import AppConfig
import posthog
from django.conf import settings


class CallProcessingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tellme.call_processing'

    def ready(self):
        # Ensure PostHog is initialized (fallback if call_miner app didn't initialize it)
        if hasattr(settings, 'POSTHOG_API_KEY') and settings.POSTHOG_API_KEY:
            if not hasattr(posthog, 'api_key') or not posthog.api_key:
                posthog.api_key = settings.POSTHOG_API_KEY
                posthog.host = settings.POSTHOG_HOST

        # Import Extensions for drf-spectacular
        import tellme.call_processing.authentication_extensions
