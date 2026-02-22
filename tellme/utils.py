from django.conf import settings


def spectacular_postprocess_schema(result, generator, request, public):
    """
    Postprocess the OpenAPI schema to convert union types and JSON Schema features to OpenAPI 3.0.3 compatible format.

    API Gateway requires strict OpenAPI 3.0.3 compliance:
    - Union types like ['number', 'null'] need to be converted to {type: 'number', nullable: true}
    - patternProperties needs to be converted to additionalProperties
    - Inline schemas should reference components when possible
    """

    # Apply the fix to the entire schema
    fix_schema_issues(result)

    # Add required Google Cloud extensions
    add_google_cloud_extensions(result)

    # Add CORS configuration to match Django settings
    # add_cors_configuration(result)

    # Add missing endpoints that aren't auto-discovered
    add_missing_endpoints(result)

    # Add OPTIONS methods for CORS preflight handling
    add_cors_preflight_options(result)

    # Remove internal processing endpoints from API Gateway spec
    remove_internal_endpoints(result)

    # If request is None, we are running via CLI (generating spec.yaml for Gateway).
    if request is None:
        fix_api_gateway_paths(result)  # We must remove trailing slashes
        convert_auth_for_gcp_gateway(result)  # We must convert the standard Bearer auth to GCP OAuth2 format.

    return result


def fix_schema_issues(obj):
    if isinstance(obj, dict):
        # Convert patternProperties to additionalProperties
        if 'patternProperties' in obj:
            pattern_props = obj['patternProperties']
            # Take the first pattern property and use it as additionalProperties
            if pattern_props:
                first_pattern_key = list(pattern_props.keys())[0]
                obj['additionalProperties'] = pattern_props[first_pattern_key]
            del obj['patternProperties']

        # Fix inline response schemas that are missing proper structure
        if ('content' in obj and
            isinstance(obj['content'], dict) and
            'application/json' in obj['content'] and
            'schema' in obj['content']['application/json']):

            schema = obj['content']['application/json']['schema']

            # Fix schemas with 'detail' as a direct property (should be in example/properties)
            if isinstance(schema, dict) and 'detail' in schema:
                detail_value = schema.pop('detail')
                # If no type is set, make it an object
                if 'type' not in schema:
                    schema['type'] = 'object'
                # Move detail to example or create properties
                if 'example' not in schema:
                    if 'properties' not in schema:
                        schema['properties'] = {}
                    schema['properties']['detail'] = {
                        'type': 'string',
                        'example': detail_value
                    }
                # Enable additional properties
                if 'additionalProperties' not in schema:
                    schema['additionalProperties'] = True

            # If schema has properties but no $ref and no type, make it a generic object
            if (isinstance(schema, dict) and
                ('properties' in schema or any(key for key in schema.keys() if key not in ['description', 'example', 'examples', 'type', '$ref', 'anyOf', 'allOf', 'oneOf', 'nullable', 'additionalProperties'])) and
                '$ref' not in schema and
                'type' not in schema and
                'anyOf' not in schema and
                'allOf' not in schema and
                'oneOf' not in schema):
                schema['type'] = 'object'
                # Enable additional properties to allow flexible response structures
                if 'additionalProperties' not in schema:
                    schema['additionalProperties'] = True

        # Handle the 'type' field with union types
        if 'type' in obj and isinstance(obj['type'], list):
            type_list = obj['type']

            # Handle union with null
            if 'null' in type_list or None in type_list:
                # Remove null/None from the type list
                non_null_types = [t for t in type_list if t not in ('null', None)]

                if len(non_null_types) == 1:
                    # Single type with null -> use nullable
                    obj['type'] = non_null_types[0]
                    obj['nullable'] = True
                elif len(non_null_types) > 1:
                    # Multiple non-null types -> use anyOf with nullable
                    obj['anyOf'] = [{'type': t} for t in non_null_types]
                    obj['nullable'] = True
                    del obj['type']
                else:
                    # Only null type
                    obj['type'] = 'string'
                    obj['nullable'] = True
            elif len(type_list) > 1:
                # Multiple types without null -> use anyOf
                obj['anyOf'] = [{'type': t} for t in type_list]
                del obj['type']
            elif len(type_list) == 1:
                # Single type in array -> extract it
                obj['type'] = type_list[0]

        # Recursively process all dictionary values
        for key, value in obj.items():
            fix_schema_issues(value)

    elif isinstance(obj, list):
        # Recursively process all list items
        for item in obj:
            fix_schema_issues(item)


def fix_api_gateway_paths(schema):
    """
    Fix paths to be compatible with API Gateway requirements.
    API Gateway doesn't accept paths ending with '/'.
    """
    if 'paths' in schema:
        # Create new paths dict without trailing slashes
        new_paths = {}
        for path, path_item in schema['paths'].items():
            # Remove trailing slash unless it's the root path
            clean_path = path.rstrip('/') if path != '/' else path
            new_paths[clean_path] = path_item

        schema['paths'] = new_paths


def add_google_cloud_extensions(schema):
    """
    Add required Google Cloud API Gateway extensions to the OpenAPI spec.

    For OpenAPI 3.0, x-google-backend MUST be a string reference to a backend
    defined in x-google-api-management, NOT an object.
    """
    # Define the backend in x-google-api-management
    schema['x-google-api-management'] = {
        'backends': {
            'cloud-run-backend': {
                'address': '${cloud_run_url}',
                'deadline': 60,
                'jwt_audience': '${cloud_run_url}',
                'path_translation': 'APPEND_PATH_TO_ADDRESS'
            }
        }
    }

    # Reference the backend by NAME ONLY (must be a string, not object)
    schema['x-google-backend'] = 'cloud-run-backend'


def add_missing_endpoints(schema):
    """
    Add endpoints that aren't auto-discovered by drf-spectacular.

    Note: /admin endpoints are NOT added here as they are served directly
    through IAP-protected Cloud Run backend, bypassing the API Gateway.
    """
    if 'paths' not in schema:
        schema['paths'] = {}

    # Add health check endpoint
    schema['paths']['/health'] = {
        'get': {
            'operationId': 'health_check',
            'tags': ['health'],
            'summary': 'Health Check',
            'description': 'Check the health status of the application',
            'responses': {
                '200': {
                    'description': 'Health check successful',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'status': {'type': 'string', 'example': 'ok'}
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    # Add schema endpoint
    schema['paths']['/api/schema'] = {
        'get': {
            'operationId': 'api_schema',
            'tags': ['schema'],
            'summary': 'OpenAPI Schema',
            'description': 'Get the OpenAPI schema for this API',
            'responses': {
                '200': {
                    'description': 'OpenAPI schema',
                    'content': {
                        'application/vnd.oai.openapi': {
                            'schema': {
                                'type': 'object'
                            }
                        }
                    }
                }
            }
        }
    }

    # Add Swagger UI endpoint
    schema['paths']['/api/schema/swagger-ui'] = {
        'get': {
            'operationId': 'swagger_ui',
            'tags': ['schema'],
            'summary': 'Swagger UI',
            'description': 'Interactive API documentation with Swagger UI',
            'responses': {
                '200': {
                    'description': 'Swagger UI HTML page',
                    'content': {
                        'text/html': {
                            'schema': {
                                'type': 'string'
                            }
                        }
                    }
                }
            }
        }
    }

    # Add the session token issuance endpoint — goes through the API Gateway (unlike /queue and /ws/audiohook/).
    # Clients call this once with their long-lived Org API Key to receive a short-lived ephemeral token.
    schema['paths']['/processing/v1/start'] = {
        'get': {
            'operationId': 'processing_v1_start',
            'tags': ['processing'],
            'summary': 'Issue Ephemeral Session Token',
            'description': (
                'Authenticates with the Organization API Key and returns a short-lived session token. '
                'The token is used to authenticate direct Cloud Run calls to /processing/v1/queue/ '
                'and /ws/audiohook/, which bypass the API Gateway.'
            ),
            'security': [{'OrganizationApiKeyAuth': []}],
            'responses': {
                '200': {
                    'description': 'Ephemeral session token issued',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'session_token': {'type': 'string'},
                                    'expires_at': {'type': 'string', 'format': 'date-time'},
                                }
                            }
                        }
                    }
                }
            }
        }
    }


def add_cors_configuration(schema):
    """
    Add CORS configuration to the API Gateway that inherits from Django's CORS settings.
    This ensures consistency between direct Django access and API Gateway access.
    """

    # Determine allowed origins from Django CORS settings
    if hasattr(settings, 'CORS_ALLOW_ALL_ORIGINS') and settings.CORS_ALLOW_ALL_ORIGINS:
        allowed_origins = ['*']
    elif hasattr(settings, 'CORS_ALLOWED_ORIGINS'):
        allowed_origins = list(settings.CORS_ALLOWED_ORIGINS)
    else:
        # Fallback to FRONTEND_PATH if CORS settings not found
        frontend_path = getattr(settings, 'FRONTEND_PATH', '')
        if frontend_path == '*':
            allowed_origins = ['*']
        else:
            allowed_origins = frontend_path.split(',') if frontend_path else ['*']

    # Get other CORS settings from Django
    cors_headers = getattr(settings, 'CORS_ALLOW_HEADERS', [
        'authorization', 'content-type', 'accept', 'origin', 'user-agent', 'x-csrftoken'
    ])
    cors_methods = getattr(settings, 'CORS_ALLOW_METHODS', [
        'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'
    ])
    cors_credentials = getattr(settings, 'CORS_ALLOW_CREDENTIALS', True)

    # Add x-google-cors configuration
    cors_configs = []
    for origin in allowed_origins:
        cors_configs.append({
            'origin': origin,
            'methods': cors_methods,
            'headers': cors_headers,
            'expose_headers': ['*'],
            'max_age': 3600,
            'allow_credentials': cors_credentials
        })

    schema['x-google-cors'] = cors_configs


def add_cors_preflight_options(schema):
    """
    Add OPTIONS methods to all paths for CORS preflight handling.

    This allows browsers to send preflight requests that pass through to Django,
    which can then respond with proper CORS headers. Each OPTIONS method:
    - Has empty security array to allow unauthenticated preflight requests
    - Uses x-google-backend to pass through to Cloud Run
    - Copies path parameters from existing methods (required for parameterized paths)
    """
    if 'paths' not in schema:
        return

    # Add OPTIONS method to all existing paths
    paths_to_update = list(schema['paths'].keys())
    for path in paths_to_update:
        path_item = schema['paths'][path]
        if 'options' not in path_item:
            # Find path parameters from any existing method
            path_parameters = []
            for method_name in ['get', 'post', 'put', 'patch', 'delete']:
                if method_name in path_item and 'parameters' in path_item[method_name]:
                    # Copy only path parameters
                    for param in path_item[method_name]['parameters']:
                        if param.get('in') == 'path':
                            path_parameters.append(param)
                    break  # Found parameters, no need to check other methods

            # Create a clean path name for operationId
            clean_path = path.replace('/', '_').replace('{', '').replace('}', '').replace('-', '_')
            if clean_path.startswith('_'):
                clean_path = clean_path[1:]
            if not clean_path:
                clean_path = 'root'

            # Create OPTIONS method
            options_method = {
                'operationId': f'cors_preflight_{clean_path}',
                'summary': 'CORS Preflight',
                'description': 'Handle CORS preflight requests for this endpoint',
                'responses': {
                    '200': {
                        'description': 'CORS preflight response',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object'
                                }
                            }
                        }
                    }
                },
                # Critical: Empty security array allows unauthenticated preflight requests
                'security': [],
                # Pass through to backend so Django can handle CORS
                'x-google-backend': 'cloud-run-backend'
            }

            # Add path parameters if found
            if path_parameters:
                options_method['parameters'] = path_parameters

            path_item['options'] = options_method


def remove_internal_endpoints(schema):
    """
    Remove internal processing endpoints that should not be exposed via API Gateway.
    These endpoints are for internal use by Cloud Tasks and should only be accessible directly.
    """
    if 'paths' not in schema:
        return

    # List of internal endpoints to remove — either because they are invoked directly by Cloud Tasks
    # (process, summarize, create_ticket) or because they are routed directly to Cloud Run via the
    # Load Balancer, bypassing the API Gateway entirely (queue, ws/audiohook).
    internal_endpoints = [
        '/processing/v1/process',
        '/processing/v1/process/',
        '/processing/v1/summarize',
        '/processing/v1/summarize/',
        '/processing/v1/create_ticket',
        '/processing/v1/create_ticket/',
        '/processing/v1/queue',
        '/processing/v1/queue/',
    ]

    # Remove internal endpoints from the schema
    for endpoint in internal_endpoints:
        if endpoint in schema['paths']:
            del schema['paths'][endpoint]


def convert_auth_for_gcp_gateway(schema):
    """
    Overwrites the standard HTTP Bearer security scheme with the
    Google Cloud API Gateway specific OAuth2 definition.
    Only runs when generating the static YAML file.
    """
    if 'components' in schema and 'securitySchemes' in schema['components']:
        security_schemes = schema['components']['securitySchemes']

        # Look for the scheme name defined in your AuthenticationExtension ('FirebaseAuth')
        if 'FirebaseAuth' in security_schemes:
            security_schemes['FirebaseAuth'] = {
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