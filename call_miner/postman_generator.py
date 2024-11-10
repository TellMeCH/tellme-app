import json

# Define user types and variables
user_types = [
    'superuser',
    'organization_admin',
    'manager',
    'analyst',
    'agent',
    'analyst_other_org',
]

# Initialize the variables list with the base_url
variables = [
    {'key': 'base_url', 'value': 'http://0.0.0.0:8000/api/v1'},
    {'key': 'id', 'value': '1'}  # Placeholder value for 'id' variable
]

# Add bearer token variables for each user type
for user_type in user_types:
    variable_name = f'bearer_token_{user_type}'
    variables.append({'key': variable_name, 'value': 'your_token_here'})  # Replace 'your_token_here' with actual tokens

# Define viewsets and actions based on the provided views.py
viewsets = {
    'conversations': {
        'actions': {
            'list': {'method': 'GET', 'url': '/conversations/'},
            'retrieve': {'method': 'GET', 'url': '/conversations/{id}/'},
            'create': {'method': 'POST', 'url': '/conversations/'},
            'update': {'method': 'PUT', 'url': '/conversations/{id}/'},
            'partial_update': {'method': 'PATCH', 'url': '/conversations/{id}/'},
            'destroy': {'method': 'DELETE', 'url': '/conversations/{id}/'},
            'transcript': {'method': 'GET', 'url': '/conversations/{id}/transcript/'},
            'search': {'method': 'GET', 'url': '/conversations/search/?query=Olivia'}
        }
    },
    'organizations': {
        'actions': {
            'list': {'method': 'GET', 'url': '/organizations/'},
            'retrieve': {'method': 'GET', 'url': '/organizations/{id}/'},
            'create': {'method': 'POST', 'url': '/organizations/'},
            'update': {'method': 'PUT', 'url': '/organizations/{id}/'},
            'partial_update': {'method': 'PATCH', 'url': '/organizations/{id}/'},
            'destroy': {'method': 'DELETE', 'url': '/organizations/{id}/'},
            'conversations': {'method': 'GET', 'url': '/organizations/{id}/conversations/'},
            'conversation_trend': {'method': 'GET', 'url': '/organizations/{id}/conversation_trend/'},
            'conversation_topic_trend': {'method': 'GET', 'url': '/organizations/{id}/conversation_topic_trend/'},
            'duration_trend': {'method': 'GET', 'url': '/organizations/{id}/duration_trend/'},
            'sentiment_trend': {'method': 'GET', 'url': '/organizations/{id}/sentiment_trend/'},
        }
    },
    'topics': {
        'actions': {
            'list': {'method': 'GET', 'url': '/topics/'},
            'retrieve': {'method': 'GET', 'url': '/topics/{id}/'},
            'create': {'method': 'POST', 'url': '/topics/'},
            'update': {'method': 'PUT', 'url': '/topics/{id}/'},
            'partial_update': {'method': 'PATCH', 'url': '/topics/{id}/'},
            'destroy': {'method': 'DELETE', 'url': '/topics/{id}/'},
            'list_active': {'method': 'GET', 'url': '/topics/list_active/'},
            'summary_data': {'method': 'GET', 'url': '/topics/{id}/summary_data/'},
            'conversations': {'method': 'GET', 'url': '/topics/{id}/conversations/'},
            'conversation_trend': {'method': 'GET', 'url': '/topics/{id}/conversation_trend/'},
            'duration_trend': {'method': 'GET', 'url': '/topics/{id}/duration_trend/'},
            'sentiment_trend': {'method': 'GET', 'url': '/topics/{id}/sentiment_trend/'},
        }
    },
    'agents': {
        'actions': {
            'list': {'method': 'GET', 'url': '/agents/'},
            'retrieve': {'method': 'GET', 'url': '/agents/{id}/'},
            'summary_data': {'method': 'GET', 'url': '/agents/{id}/summary_data/'},
            'conversations': {'method': 'GET', 'url': '/agents/{id}/conversations/'},
            'conversation_trend': {'method': 'GET', 'url': '/agents/{id}/conversation_trend/'},
            'conversation_topic_trend': {'method': 'GET', 'url': '/agents/{id}/conversation_topic_trend/'},
            'duration_trend': {'method': 'GET', 'url': '/agents/{id}/duration_trend/'},
            'sentiment_trend': {'method': 'GET', 'url': '/agents/{id}/sentiment_trend/'},
            'managed_agents': {'method': 'GET', 'url': '/agents/{id}/managed_agents/'},
        }
    },
    'customers': {
        'actions': {
            'list': {'method': 'GET', 'url': '/customers/'},
            'retrieve': {'method': 'GET', 'url': '/customers/{id}/'},
            'create': {'method': 'POST', 'url': '/customers/'},
            'update': {'method': 'PUT', 'url': '/customers/{id}/'},
            'partial_update': {'method': 'PATCH', 'url': '/customers/{id}/'},
            'destroy': {'method': 'DELETE', 'url': '/customers/{id}/'},
            'summary_data': {'method': 'GET', 'url': '/customers/{id}/summary_data/'},
            'conversations': {'method': 'GET', 'url': '/customers/{id}/conversations/'},
            'conversation_trend': {'method': 'GET', 'url': '/customers/{id}/conversation_trend/'},
            'conversation_topic_trend': {'method': 'GET', 'url': '/customers/{id}/conversation_topic_trend/'},
            'duration_trend': {'method': 'GET', 'url': '/customers/{id}/duration_trend/'},
            'sentiment_trend': {'method': 'GET', 'url': '/customers/{id}/sentiment_trend/'},
        }
    },
    'employees': {
        'actions': {
            'list': {'method': 'GET', 'url': '/employees/'},
            'retrieve': {'method': 'GET', 'url': '/employees/{id}/'},
            'create': {'method': 'POST', 'url': '/employees/'},
            'update': {'method': 'PUT', 'url': '/employees/{id}/'},
            'partial_update': {'method': 'PATCH', 'url': '/employees/{id}/'},
            'destroy': {'method': 'DELETE', 'url': '/employees/{id}/'},
        }
    },
}

# Map viewset names to permission summaries
folder_descriptions = {
    'conversations': (
        "Permissions:\n"
        "- Superusers can do anything.\n"
        "- Employees can list and retrieve conversations belonging to their organization.\n"
        "- Only superusers can create, update, or delete conversations."
    ),
    'organizations': (
        "Permissions:\n"
        "- Superusers can do anything.\n"
        "- Analysts can retrieve their own organization, but cannot list all organizations.\n"
        "- Only superusers can create, update, or delete organizations."
    ),
    'topics': (
        "Permissions:\n"
        "- Superusers and analysts can create, update, and delete topics.\n"
        "- All employees can list and retrieve topics.\n"
        "- Access is limited to topics belonging to the user's organization."
    ),
    'agents': (
        "Permissions:\n"
        "- Superusers can do anything.\n"
        "- Organization admins can access agents in their organization.\n"
        "- Managers can access their managed agents.\n"
        "- Agents can access their own records.\n"
        "- Only superusers can modify agents."
    ),
    'customers': (
        "Permissions:\n"
        "- Superusers can do anything.\n"
        "- Employees can list and retrieve customers in their organization.\n"
        "- Only superusers can create, update, or delete customers."
    ),
    'employees': (
        "Permissions:\n"
        "- Superusers and organization admins can create, update, and delete employees in their organization.\n"
        "- Employees can retrieve their own employee record."
    ),
}

# Initialize the collection
collection = {
    "info": {
        "name": "Tell Me Backend API",
        "_postman_id": "unique-id",  # You can generate a unique ID here
        "description": "Generated collection for the Tell Me Backend API",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [],
    "variable": variables
}

# Generate the collection items
for viewset_name, viewset_data in viewsets.items():
    folder = {
        'name': viewset_name.capitalize(),  # Capitalize the viewset name for readability
        'description': folder_descriptions.get(viewset_name, ''),
        'item': []
    }
    actions = viewset_data['actions']
    for action_name, action_data in actions.items():
        method = action_data['method']
        url = action_data['url']  # e.g., '/conversations/{id}/'
        for user_type in user_types:
            request_name = f"{action_name} - {user_type}"

            # Build the request
            request_url = url.replace('{id}', '{{id}}')
            full_url = "{{base_url}}" + request_url
            path_segments = [segment for segment in request_url.split('/') if segment]
            if request_url.endswith('/'):
                path_segments.append('')

            request = {
                'name': request_name,
                'request': {
                    'method': method,
                    'header': [
                        {
                            'key': 'Authorization',
                            'value': f"Bearer {{{{bearer_token_{user_type}}}}}",
                            'type': 'text'
                        }
                    ],
                    'url': {
                        'raw': full_url,
                        'host': ["{{base_url}}"],
                        'path': path_segments,
                    }
                }
            }
            folder['item'].append(request)
    collection['item'].append(folder)

# Write the collection to a JSON file
with open('tellme_postman.json', 'w') as f:
    json.dump(collection, f, indent=2)
