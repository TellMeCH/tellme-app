def spectacular_postprocess_schema(result, generator, request, public):
    """
    Postprocess the OpenAPI schema to convert union types to OpenAPI 3.0.3 compatible format.

    API Gateway requires strict OpenAPI 3.0.3 compliance. Union types like ['number', 'null']
    need to be converted to {type: 'number', nullable: true}.
    """
    def fix_union_types(obj):
        if isinstance(obj, dict):
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
                fix_union_types(value)

        elif isinstance(obj, list):
            # Recursively process all list items
            for item in obj:
                fix_union_types(item)

    # Apply the fix to the entire schema
    fix_union_types(result)

    return result