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
            'x-google-issuer': f'https://securetoken.google.com/{settings.GOOGLE_CLOUD_PROJECT}',
            'x-google-jwks_uri': 'https://www.googleapis.com/service_accounts/v1/metadata/x509/securetoken@system.gserviceaccount.com',
            'x-google-audiences': settings.GOOGLE_CLOUD_PROJECT
        }
