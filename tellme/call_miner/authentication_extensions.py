from drf_spectacular.extensions import OpenApiAuthenticationExtension
from django.conf import settings


class FirebaseAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    Authentication Extension used only for documentation purposes (hence the OpenAPI)

    Note: API Gateway only supports 'oauth2' and 'apiKey' types, not 'http' with 'bearer' scheme.
    We define this as apiKey for API Gateway compatibility while actual implementation remains Bearer token.
    """
    target_class = 'tellme.call_miner.authentication.FirebaseAuthentication'
    name = 'FirebaseAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'oauth2',
            'flows': {
                'implicit': {
                    'authorizationUrl': '',
                    'scopes': {}
                }
            },
            'x-google-auth': {
                'issuer': f'https://securetoken.google.com/{settings.GOOGLE_CLOUD_PROJECT}',
                'jwksUri': 'https://www.googleapis.com/service_accounts/v1/metadata/x509/securetoken@system.gserviceaccount.com',
                'audiences': [settings.GOOGLE_CLOUD_PROJECT]
            }
        }


class DummyApiKeyScheme(OpenApiAuthenticationExtension):
    """
    Dummy API key scheme to satisfy API Gateway requirements.
    API Gateway requires all operations to have at least one apiKey security scheme.
    This is just for API Gateway validation - actual auth is handled by Firebase.
    """
    target_class = 'tellme.call_miner.authentication.FirebaseAuthentication'
    name = 'api_key'
    priority = -1  # Lower priority than Firebase

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'query',
            'name': 'key',
            'description': 'Dummy API key for API Gateway project tracking (actual auth via Firebase)'
        }
