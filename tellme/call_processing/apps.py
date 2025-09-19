from django.apps import AppConfig


class CallProcessingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tellme.call_processing'

    def ready(self):
        # Import Extensions for drf-spectacular
        import tellme.call_processing.authentication_extensions
