def spectacular_postprocess_schema(result, generator, request, public):
    """
    Postprocess the OpenAPI schema to convert union types and JSON Schema features to OpenAPI 3.0.3 compatible format.

    API Gateway requires strict OpenAPI 3.0.3 compliance:
    - Union types like ['number', 'null'] need to be converted to {type: 'number', nullable: true}
    - patternProperties needs to be converted to additionalProperties
    - Inline schemas should reference components when possible
    """
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

    # Apply the fix to the entire schema
    fix_schema_issues(result)

    # Fix API Gateway path requirements (no trailing slashes)
    fix_api_gateway_paths(result)

    # Add required Google Cloud extensions
    add_google_cloud_extensions(result)

    # Add CORS configuration to match Django settings
    add_cors_configuration(result)

    # Add missing endpoints that aren't auto-discovered
    add_missing_endpoints(result)

    # Remove internal processing endpoints from API Gateway spec
    remove_internal_endpoints(result)

    return result


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
                'deadline': 60
            }
        }
    }

    # Reference the backend by NAME ONLY (must be a string, not object)
    schema['x-google-backend'] = 'cloud-run-backend'


def add_missing_endpoints(schema):
    """
    Add endpoints that aren't auto-discovered by drf-spectacular.
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


def add_cors_configuration(schema):
    """
    Add CORS configuration to the API Gateway that inherits from Django's CORS settings.
    This ensures consistency between direct Django access and API Gateway access.
    """
    from django.conf import settings

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


def remove_internal_endpoints(schema):
    """
    Remove internal processing endpoints that should not be exposed via API Gateway.
    These endpoints are for internal use by Cloud Tasks and should only be accessible directly.
    """
    if 'paths' not in schema:
        return

    # List of internal endpoints to remove
    internal_endpoints = [
        '/processing/v1/process',
        '/processing/v1/process/',
        '/processing/v1/summarize',
        '/processing/v1/summarize/'
    ]

    # Remove internal endpoints from the schema
    for endpoint in internal_endpoints:
        if endpoint in schema['paths']:
            del schema['paths'][endpoint]