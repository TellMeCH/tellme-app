from drf_spectacular.extensions import OpenApiAuthenticationExtension
from django.conf import settings


class FirebaseAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    Standard definition for Swagger UI (Http Bearer).
    The conversion to GCP format happens in utils.py specifically for file generation.
    """
    target_class = 'tellme.call_miner.authentication.FirebaseAuthentication'
    name = 'FirebaseAuth'

    def get_security_definition(self, auto_schema):
        # 1. This enables the simple "Paste Token" box in Swagger UI
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'Enter your Firebase JWT token'
        }
