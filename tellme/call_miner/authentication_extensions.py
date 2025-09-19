from drf_spectacular.extensions import OpenApiAuthenticationExtension


class FirebaseAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    Authentication Extension used only for documentation purposes (hence the OpenAPI)
    """
    target_class = 'call_miner.authentication.FirebaseAuthentication'
    name = 'BearerAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'Firebase',
        }
