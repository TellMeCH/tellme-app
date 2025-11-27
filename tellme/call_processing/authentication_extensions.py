from drf_spectacular.extensions import OpenApiAuthenticationExtension


class OrganizationAPIKeyAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'tellme.call_processing.authentication.OrganizationAPIKeyAuthentication'
    name = 'OrganizationApiKeyAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Use format: "X-API-KEY <API_KEY>"',
        }


class ProcessingKeyAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'tellme.call_processing.authentication.ProcessingKeyAuthentication'
    name = 'ProcessingKeyAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Processing pipeline token. Use format: "Token <PROCESSING_PIPELINE_KEY>"',
        }