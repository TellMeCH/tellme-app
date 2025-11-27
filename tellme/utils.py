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