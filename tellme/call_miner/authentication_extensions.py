from drf_spectacular.extensions import OpenApiAuthenticationExtension


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
            'type': 'apiKey',
            'in': 'header',
            'name': 'x-api-key',
            'description': 'Firebase JWT token. Use format: "Bearer <firebase_jwt_token>" in x-api-key header',
        }
