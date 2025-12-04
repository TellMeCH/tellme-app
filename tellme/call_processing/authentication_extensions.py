from drf_spectacular.extensions import OpenApiAuthenticationExtension


class OrganizationAPIKeyAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'tellme.call_processing.authentication.OrganizationAPIKeyAuthentication'
    name = 'OrganizationApiKeyAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Organization API key in Authorization header',
        }


class ProcessingKeyAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'tellme.call_processing.authentication.ProcessingKeyAuthentication'
    name = 'ProcessingKeyAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'query',
            'name': 'key',
            'description': 'Processing pipeline key as query parameter',
        }