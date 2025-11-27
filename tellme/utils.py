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

            # Fix inline response schemas that are missing $ref
            if ('content' in obj and
                isinstance(obj['content'], dict) and
                'application/json' in obj['content'] and
                'schema' in obj['content']['application/json']):

                schema = obj['content']['application/json']['schema']

                # If schema has properties but no $ref and no type, make it a generic object
                if (isinstance(schema, dict) and
                    'properties' in schema and
                    '$ref' not in schema and
                    'type' not in schema):
                    schema['type'] = 'object'

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

    return result