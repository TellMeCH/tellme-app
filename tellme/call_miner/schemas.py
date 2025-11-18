from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, OpenApiResponse


ID_PARAMETER_SCHEMA = OpenApiParameter(
    name='id',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    description='Primary key of the model instance.',
    required=True,
)

SUMMARY_PERIOD_PARAMETER_SCHEMA = OpenApiParameter(
    name='period',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    description='Summarization period (week, month, quarter)',
    required=False,
    default='month',
)

SUMMARY_ROLLING_PARAMETER_SCHEMA = OpenApiParameter(
    name='rolling',
    type=OpenApiTypes.BOOL,
    location=OpenApiParameter.QUERY,
    description='Whether the summarization window is rolling (week, month, quarter)',
    required=False,
    default=False,
)

TREND_PERIOD_PARAMETER_SCHEMA = OpenApiParameter(
    name='trend_period',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    description='Trend period (e.g., daily, weekly, monthly).',
    required=False,
    default='monthly',
)

PER_TOPIC_PARAMETER_SCHEMA = OpenApiParameter(
    name='per_topic',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    description='Whether to aggregate the trend also per topic level (e.g true or false)',
    required=False,
    default='false',
)

SEARCH_QUERY_PARAMETER_SCHEMA = OpenApiParameter(
    name='query',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    description='Search query',
    required=True,
)

CONVERSATION_ORDERING_PARAMETER_SCHEMA = OpenApiParameter(
    name='ordering',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    description='Field(s) to order by. Allowed fields: date, sentiment, resolved. Use "-" prefix for descending order (e.g., -date). Multiple fields can be comma-separated (e.g., "resolved,-sentiment"). Note: When using cursor pagination, changing the ordering parameter while navigating pages may produce unexpected results.',
    required=False,
)

CUSTOMER_ORDERING_PARAMETER_SCHEMA = OpenApiParameter(
    name='ordering',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    description='Field(s) to order by. Allowed fields: last_conversation_date, conversation_count, created, total_revenue, avg_sentiment. Use "-" prefix for descending order (e.g., -total_revenue). Multiple fields can be comma-separated (e.g., "total_revenue,-avg_sentiment"). Note: When using cursor pagination, changing the ordering parameter while navigating pages may produce unexpected results.',
    required=False,
)

PAGE_SIZE_PARAMETER_SCHEMA = OpenApiParameter(
    name='page_size',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    description='Number of results per page',
    required=False,
)

CURSOR_PARAMETER_SCHEMA = OpenApiParameter(
    name='cursor',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    description='Cursor for pagination (obtained from previous response)',
    required=False,
)

def get_search_parameters_schema(ordering_schema):
    """Generate search endpoint parameters including query, ordering, and pagination"""
    return [
        SEARCH_QUERY_PARAMETER_SCHEMA,
        ordering_schema,
        PAGE_SIZE_PARAMETER_SCHEMA,
        CURSOR_PARAMETER_SCHEMA,
    ]

REGENERATE_API_KEY_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
                'description': 'Name of the newly regenerated API key.'
            },
            'organization': {
                'type': 'integer',
                'description': 'Primary key of the associated organization.'
            },
            'plain_key': {
                'type': 'string',
                'description': 'Plain text value of the newly generated API key. Shown only once.'
            }
        },
        'required': ['name', 'organization', 'plain_key'],
        'example': {
            'name': 'My Regenerated Key',
            'organization': 42,
            'plain_key': 'pk_live_a1b2c3d4'
        }
    },
    description="Response returned when an API key has been successfully regenerated."
)

TOPIC_DATA_RESPONSE_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the topic.'},
            'description': {'type': 'string', 'description': 'Detailed description of the topic.'},
            'is_active': {'type': 'boolean', 'description': 'Indicates whether the topic is active.'},
            'url': {'type': 'string', 'format': 'uri', 'description': 'Hyperlink to the topic detail.'},
        },
        'example': {
            'name': 'Customer Support',
            'description': 'Support for customer queries and issues.',
            'is_active': True,
            'url': 'https://example.com/api/topics/1/'
        },
    }
}

SUGGESTED_TOPIC_DATA_RESPONSE_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'description': 'Name of the topic.'},
            'description': {'type': 'string', 'description': 'Detailed description of the topic.'},
            'conversation_count': {'type': 'integer', 'description': 'Conversations associated to the topic.'},
        },
        'example': {
            'name': 'Customer Support',
            'description': 'Support for customer queries and issues.',
            'conversation_count': 4
        },
    }
}

SUMMARY_DATA_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'properties': {
            'summary': {
                'type': 'object',
                'description': """
                    Dictionary with a series of meta-summary questions and answers. Each key corresponds to a different
                    meta-summary title, whereas each value corresponds to its meta-summary. Will be null if no the
                    respective object has no associated conversations. 
                """
            },
            'summary_date': {
                'type': 'string',
                'format': 'date-time',
                'description': 'Date of this summarization.'
            },
            'summary_call_count': {
                'type': 'integer',
                'description': 'Number of calls included in the summary.'
            },
            'period_label': {
                'type': 'string',
                'description': 'Described the period for which the summary was obtained. Three formats: 2025-W14 for weeks, 2025-03 for months, 2025-Q1 for quarters.'
            },
        },
        'required': ['summary', 'summary_date', 'summary_call_count', 'period_label'],
        'example': {
            'summary': {'Reasons for Calling': 'Billing issues and account setup inquiries are common.'},
            'summary_date': '2023-10-15T12:34:56Z',
            'summary_call_count': 150,
            'period_label': '2023-10'
        }
    }
)

ALL_SUMMARIES_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'patternProperties': {
            r'^\d+$': {
                'type': 'object',
                'properties': {
                    'summary': {
                        'type': ['object', 'null'],
                        'description': 'Detailed summary data for the object.'
                    },
                    'summary_date': {
                        'type': 'string',
                        'format': 'date-time',
                        'description': 'Date and time when this summary was generated.'
                    },
                    'summary_call_count': {
                        'type': 'integer',
                        'description': 'Number of calls included in the summary.'
                    },
                    'period_label': {
                        'type': 'string',
                        'description': 'Period over which recorded calls were taken'
                    },
                    'name': {
                        'type': ['object', 'null'],
                        'description': 'Name of the conversation topic, if the summary pertains to a topic'
                    },
                },
                'required': ['summary', 'summary_date', 'summary_call_count', 'period_label', 'name'],
            }
        },
        'additionalProperties': False,
        'example': {
            "1": {
                "summary": {
                    "Reasons for Calling": "Customers frequently contact the call center regarding delayed packages and order status updates.",
                    "Stages of the Customer Journey": "These callers are predominantly found in the fulfillment stage of the customer journey, particularly when awaiting delivery of their orders.",
                    "Call Resolution Rates": "Most issues are resolved during the initial call, especially when agents provide updates or arrange expedited shipping.",
                    "Churn Potential": "Customers are more likely to strengthen their relationship with the company, as agents are responsive and proactive in addressing delivery issues.",
                    "Causes for Dissatisfaction": "The primary cause of dissatisfaction stems from delays in package delivery, which can lead to urgency and frustration for customers.",
                    "Causes for Engagement": "Customers express engagement and loyalty when agents provide timely updates and solutions, such as expedited shipping.",
                    "Suggested Actions": "The company could improve customer satisfaction by enhancing communication about delivery timelines and proactively notifying customers of potential delays."
                },
                "summary_date": "2025-03-28T16:23:14.593689Z",
                "summary_call_count": 6,
                "name": "Order Status"
            },
            "9": {
                "summary": None,
                "summary_date": "2025-04-10T16:23:14.210357Z",
                "summary_call_count": 0,
                "name": "Product Quality"
            }
        }
    }
)

CONVERSATIONS_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'properties': {
            'results': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'title': {'type': 'string', 'description': 'Conversation title.'},
                        'date': {'type': 'string', 'format': 'date-time',
                                 'description': 'Date of the conversation.'},
                        'url': {'type': 'string', 'format': 'uri',
                                'description': 'URL to the conversation detail.'}
                    }
                }
            },
            'next': {'type': 'string', 'format': 'uri', 'nullable': True, 'description': 'URL to the next page.'},
            'previous': {'type': 'string', 'format': 'uri', 'nullable': True,
                         'description': 'URL to the previous page.'},
        },
        'example': {
            'results': [
                {'title': 'Call with John Doe', 'date': '2023-10-01T10:00:00Z',
                 'url': 'https://example.com/conversations/1/'},
                {'title': 'Follow-up with Jane Smith', 'date': '2023-10-02T14:30:00Z',
                 'url': 'https://example.com/conversations/2/'}
            ],
            'next': 'https://example.com/conversations/?page=2',
            'previous': None
        }
    }
)

TREND_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'properties': {
            'results': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'count': {'type': 'integer', 'description': 'Number of conversations.', 'nullable': True},
                        'date': {'type': 'string', 'format': 'date', 'description': 'Date for the trend period.'},
                        'topic_name': {'type': 'string', 'description': 'Name of the topic.', 'nullable': True},
                        'topic_id': {'type': 'integer', 'description': 'ID of the topic.', 'nullable': True},
                        'avg_duration': {'type': 'number', 'format': 'float',
                                         'description': 'Average duration in seconds.', 'nullable': True},
                        'avg_sentiment': {'type': 'number', 'format': 'float',
                                         'description': 'Average sentiment.', 'nullable': True}

                    }
                }
            },
            'next': {'type': 'string', 'format': 'uri', 'nullable': True, 'description': 'URL to the next page.'},
            'previous': {'type': 'string', 'format': 'uri', 'nullable': True,
                         'description': 'URL to the previous page.'},
        },
        'example': {
            'results': [
                {'count': 5, 'date': '2023-10-01'},
                {'count': 8, 'date': '2023-11-01'}
            ],
            'next': 'https://example.com/trend/?page=2',
            'previous': None
        }
    }
)

ORGANIZATION_TREND_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'additionalProperties': {
            'type': 'object',
            'properties': {
                'results': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'count': {
                                'type': 'integer',
                                'description': 'Number of conversations.',
                                'nullable': True
                            },
                            'date': {
                                'type': 'string',
                                'format': 'date',
                                'description': 'Date for the trend period.'
                            },
                            'topic_name': {
                                'type': 'string',
                                'description': 'Name of the topic.',
                                'nullable': True
                            },
                            'topic_id': {
                                'type': 'integer',
                                'description': 'ID of the topic.',
                                'nullable': True
                            },
                            'avg_duration': {
                                'type': 'number',
                                'format': 'float',
                                'description': 'Average duration in seconds.',
                                'nullable': True
                            },
                            'avg_sentiment': {
                                'type': 'number',
                                'format': 'float',
                                'description': 'Average sentiment.',
                                'nullable': True
                            }
                        }
                    }
                },
                'next': {
                    'type': 'string',
                    'format': 'uri',
                    'nullable': True,
                    'description': 'URL to the next page.'
                },
                'previous': {
                    'type': 'string',
                    'format': 'uri',
                    'nullable': True,
                    'description': 'URL to the previous page.'
                },
            }
        },
        'example': {
            '1': {
                'results': [
                    {'count': 5, 'date': '2023-10-01', 'topic_name': None, 'topic_id': None,
                     'avg_duration': None, 'avg_sentiment': None},
                    {'count': 8, 'date': '2023-11-01', 'topic_name': None, 'topic_id': None,
                     'avg_duration': None, 'avg_sentiment': None}
                ],
                'next': 'https://example.com/trend/?page=2',
                'previous': None
            },
            '2': {
                'results': [
                    {'count': 10, 'date': '2023-10-01', 'topic_name': None, 'topic_id': None,
                     'avg_duration': 120.5, 'avg_sentiment': 0.7}
                ],
                'next': None,
                'previous': None
            }
        }
    }
)

OVERVIEW_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'description': (
            "When `per_topic=False`, the top-level object has a single key 'general', and "
            "includes a 'most_popular_topic' entry. When `per_topic=True`, the top-level "
            "object has multiple keys (one for each topic name) without 'most_popular_topic'.\n\n"
            "Each sub-object (topic or 'general') contains metrics: 'count', 'avg_sentiment', "
            "'avg_duration', each of which has keys for the two relevant months plus a 'change' key."
        ),
        'example': {
            # Example if per_topic=False:
            'general': {
                'avg_sentiment': {
                    '2024-01-01T00:00:00Z': 0.65,
                    '2024-02-01T00:00:00Z': 0.72,
                    'change': 10.77
                },
                'avg_duration': {
                    '2024-01-01T00:00:00Z': 42.1,
                    '2024-02-01T00:00:00Z': 46.3,
                    'change': 10.0
                },
                'count': {
                    '2024-01-01T00:00:00Z': 10,
                    '2024-02-01T00:00:00Z': 11,
                    'change': 10.0
                },
                'most_popular_topic': {
                    '2024-01-01T00:00:00Z': 'Topic A',
                    '2024-02-01T00:00:00Z': 'Topic B'
                }
            }
            # Example if per_topic=True (multiple keys, no "most_popular_topic"):
            # "Topic A": {
            #     "avg_sentiment": {
            #         "2024-01-01T00:00:00Z": 0.65,
            #         "2024-02-01T00:00:00Z": 0.72,
            #         "change": 10.77
            #     },
            #     "avg_duration": { ... },
            #     "count": { ... }
            # },
            # "Topic B": { ... }
        },
        'additionalProperties': {
            'type': 'object',
            'description': (
                "Either 'general' (when per_topic=False) or a topic name "
                "(when per_topic=True)."
            ),
            'properties': {
                'avg_sentiment': {
                    'type': 'object',
                    'description': "Overview of average sentiment for the last two months.",
                    'properties': {
                        'change': {
                            'type': ['number', 'null'],
                            'format': 'float',
                            'description': "Percentage change between the two months, or null if no prior data."
                        }
                    },
                    # We allow other month-based keys like "2024-01-01T00:00:00Z"
                    # to be floats, so we use additionalProperties
                    'additionalProperties': {
                        'type': ['number', 'null'],
                        'format': 'float'
                    }
                },
                'avg_duration': {
                    'type': 'object',
                    'description': "Overview of average duration (seconds) for the last two months.",
                    'properties': {
                        'change': {
                            'type': ['number', 'null'],
                            'format': 'float'
                        }
                    },
                    'additionalProperties': {
                        'type': ['number', 'null'],
                        'format': 'float'
                    }
                },
                'count': {
                    'type': 'object',
                    'description': "Overview of conversation count for the last two months.",
                    'properties': {
                        'change': {
                            'type': ['number', 'null'],
                            'format': 'float'
                        }
                    },
                    'additionalProperties': {
                        'type': ['number', 'null'],
                        'format': 'float'
                    }
                },
                'most_popular_topic': {
                    'type': 'object',
                    'description': (
                        "Only present when per_topic=False. Maps each relevant month-start to the most "
                        "popular topic name (string), or null if no data."
                    ),
                    'nullable': True,
                    'additionalProperties': {
                        'type': ['string', 'null']
                    }
                }
            }
        }
    }
)

ORGANIZATION_OVERVIEW_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'description': (
            "A mapping of organization IDs to their conversation overview data. Each value "
            "in this mapping is the same structure as a single organization's overview:\n\n"
            "- If `per_topic=False`, the key in each sub-dictionary is `'general'` plus a "
            "`'most_popular_topic'` field.\n"
            "- If `per_topic=True`, each sub-dictionary has multiple topic-name keys and no "
            "`'most_popular_topic'`."
        ),
        # We don't know in advance which org IDs might appear, so use additionalProperties
        'additionalProperties': {
            'type': 'object',
            'description': (
                "The same shape as the single-organization OVERVIEW_RESPONSE_SCHEMA. "
                "Either `'general'` or topic names as keys."
            ),
            'additionalProperties': {
                'type': 'object',
                'description': (
                    "Either a metric object (e.g. `avg_sentiment`, `avg_duration`, `count`) "
                    "or the `'most_popular_topic'` key (which only appears for `per_topic=False`)."
                ),
                'properties': {
                    'most_popular_topic': {
                        'type': 'object',
                        'nullable': True,
                        'description': (
                            "Maps each month-start datetime to the name of the most popular topic "
                            "for that month. Present only if `per_topic=False`."
                        ),
                        'additionalProperties': {
                            'type': ['string', 'null']
                        }
                    }
                },
                'additionalProperties': {
                    'type': 'object',
                    'description': (
                        "For metric objects (like 'avg_sentiment', 'avg_duration', or 'count'), "
                        "keys are month-start datetimes in ISO8601 string form, and the 'change' "
                        "key contains the percentage change. Example:\n"
                        "`{'2024-01-01T00:00:00Z': 10, '2024-02-01T00:00:00Z': 12, 'change': 20.0}`"
                    ),
                    'properties': {
                        'change': {
                            'type': ['number', 'null'],
                            'description': "Percentage change from the prior month, or null if not applicable."
                        }
                    },
                    'additionalProperties': {
                        'type': ['number', 'null']
                    }
                }
            }
        },
        'example': {
            # In this example, we're returning overviews for org ID=1 and org ID=2
            '1': {
                # If per_topic=False => "general" + "most_popular_topic"
                'general': {
                    'avg_sentiment': {
                        '2024-01-01T00:00:00Z': 0.5,
                        '2024-02-01T00:00:00Z': 0.6,
                        'change': 20.0
                    },
                    'avg_duration': {
                        '2024-01-01T00:00:00Z': 35.3,
                        '2024-02-01T00:00:00Z': 42.0,
                        'change': 19.07
                    },
                    'count': {
                        '2024-01-01T00:00:00Z': 10,
                        '2024-02-01T00:00:00Z': 12,
                        'change': 20.0
                    },
                    'most_popular_topic': {
                        '2024-01-01T00:00:00Z': 'Billing Issues',
                        '2024-02-01T00:00:00Z': 'Technical Problems'
                    }
                }
            },
            '2': {
                # If per_topic=True => multiple topics instead of "general", no "most_popular_topic"
                'Topic A': {
                    'avg_sentiment': {
                        '2024-01-01T00:00:00Z': 0.7,
                        '2024-02-01T00:00:00Z': 0.65,
                        'change': -7.14
                    },
                    'avg_duration': {
                        '2024-01-01T00:00:00Z': 38.0,
                        '2024-02-01T00:00:00Z': 40.0,
                        'change': 5.26
                    },
                    'count': {
                        '2024-01-01T00:00:00Z': 8,
                        '2024-02-01T00:00:00Z': 9,
                        'change': 12.5
                    }
                },
                'Topic B': {
                    'avg_sentiment': {
                        '2024-01-01T00:00:00Z': 0.5,
                        '2024-02-01T00:00:00Z': 0.55,
                        'change': 10.0
                    },
                    'avg_duration': {
                        '2024-01-01T00:00:00Z': 45.1,
                        '2024-02-01T00:00:00Z': 45.1,
                        'change': 0
                    },
                    'count': {
                        '2024-01-01T00:00:00Z': 10,
                        '2024-02-01T00:00:00Z': 10,
                        'change': 0
                    }
                }
            }
        }
    }
)

SEARCH_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'properties': {
            'results': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        # Note: Actual fields depend on the serializer.
                        'example_field_1': {'type': 'string', 'description': 'Description of example field 1.'},
                        'example_field_2': {'type': 'integer', 'description': 'Description of example field 2.'},
                    },
                    'example': {
                        'example_field_1': 'Sample Value',
                        'example_field_2': 123,
                    },
                },
                'description': 'List of search results with fields defined by the serializer used.'
            },
            'next': {'type': 'string', 'format': 'uri', 'nullable': True,
                     'description': 'URL to the next page of results.'},
            'previous': {'type': 'string', 'format': 'uri', 'nullable': True,
                         'description': 'URL to the previous page of results.'},
        },
        'example': {
            'results': [
                {
                    "url": "http://0.0.0.0:8000/api/v1/customers/7/",
                    "name": "Olivia Blue",
                    "conversation_count": 0,
                    "first_conversation_date": None,
                    "last_conversation_date": None,
                    "created": "2024-11-19T06:59:04.438161Z"
                }
            ],
            'next': 'https://example.com/search/?cursor=next',
            'previous': None,
        }
    }
)

TRANSCRIPT_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'properties': {
            'results': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'description': 'Unique identifier for the message.'},
                        'message': {'type': 'string', 'description': 'The text of the message.'},
                        'class': {
                            'type': 'string',
                            'description': 'The message origin, e.g., "agent-message" or "customer-message".',
                            'enum': ['agent-message', 'customer-message']
                        },
                    },
                    'example': {
                        'id': 0,
                        'message': 'Hello, agent_06, how can I assist you today?',
                        'class': 'agent-message'
                    }
                }
            },
            'next': {
                'type': 'string',
                'format': 'uri',
                'nullable': True,
                'description': 'URL to the next page of results, if applicable.'
            },
            'previous': {
                'type': 'string',
                'format': 'uri',
                'nullable': True,
                'description': 'URL to the previous page of results, if applicable.'
            },
        },
        'required': ['results', 'next', 'previous'],
        'example': {
            "results": [
                {
                    "id": 0,
                    "message": "Hello, agent_06, how can I assist you today?",
                    "class": "agent-message"
                },
                {
                    "id": 1,
                    "message": "Hi, I have an issue with my product. It's acting weird.",
                    "class": "customer-message"
                },
                {
                    "id": 2,
                    "message": "Could you describe the problem?",
                    "class": "agent-message"
                },
                {
                    "id": 3,
                    "message": "Yes, it keeps making a strange noise and flashing red lights.",
                    "class": "customer-message"
                },
                {
                    "id": 4,
                    "message": "That doesn't sound right. Let me look into that for you.",
                    "class": "agent-message"
                }
            ],
            "next": "http://0.0.0.0:8000/api/v1/conversations/1/transcript/?cursor=MTU=",
            "previous": None
        }
    }
)

LIST_ACTIVE_TOPICS_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'properties': {
            'next': {
                'type': 'string',
                'format': 'uri',
                'nullable': True,
                'description': 'URL to the next page of results, if applicable.'
            },
            'previous': {
                'type': 'string',
                'format': 'uri',
                'nullable': True,
                'description': 'URL to the previous page of results, if applicable.'
            },
            'results': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'url': {
                            'type': 'string',
                            'format': 'uri',
                            'description': 'URL to the topic detail.'
                        },
                        'name': {
                            'type': 'string',
                            'description': 'The name of the topic.'
                        },
                        'description': {
                            'type': 'string',
                            'description': 'A description of the topic.'
                        },
                        'conversation_count': {
                            'type': 'integer',
                            'description': 'The total number of conversations associated with the topic.'
                        },
                        'first_conversation_date': {
                            'type': 'string',
                            'format': 'date-time',
                            'description': 'The date of the first conversation associated with the topic.'
                        },
                        'last_conversation_date': {
                            'type': 'string',
                            'format': 'date-time',
                            'description': 'The date of the last conversation associated with the topic.'
                        },
                        'is_active': {
                            'type': 'boolean',
                            'description': 'Indicates whether the topic is active.'
                        },
                        'created': {
                            'type': 'string',
                            'format': 'date-time',
                            'description': 'The date and time when the topic was created.'
                        },
                        'updated': {
                            'type': 'string',
                            'format': 'date-time',
                            'description': 'The date and time when the topic was last updated.'
                        },
                    },
                    'example': {
                        'url': 'http://0.0.0.0:8000/api/v1/topics/4/',
                        'name': 'Topic 4',
                        'description': 'This is topic number 4 for ACME Org.',
                        'conversation_count': 41,
                        'first_conversation_date': '2024-01-05T00:00:00Z',
                        'last_conversation_date': '2024-12-06T00:00:00Z',
                        'is_active': True,
                        'created': '2024-11-19T07:41:16.005957Z',
                        'updated': '2024-11-19T07:41:25.558768Z'
                    }
                },
                'description': 'A list of active topics in the organization.'
            },
        },
        'example': {
            'next': None,
            'previous': None,
            'results': [
                {
                    'url': 'http://0.0.0.0:8000/api/v1/topics/4/',
                    'name': 'Topic 4',
                    'description': 'This is topic number 4 for ACME Org.',
                    'conversation_count': 41,
                    'first_conversation_date': '2024-01-05T00:00:00Z',
                    'last_conversation_date': '2024-12-06T00:00:00Z',
                    'is_active': True,
                    'created': '2024-11-19T07:41:16.005957Z',
                    'updated': '2024-11-19T07:41:25.558768Z'
                },
                {
                    'url': 'http://0.0.0.0:8000/api/v1/topics/1/',
                    'name': 'Topic 1',
                    'description': 'This is topic number 1 for ACME Org.',
                    'conversation_count': 36,
                    'first_conversation_date': '2024-01-03T00:00:00Z',
                    'last_conversation_date': '2024-12-29T00:00:00Z',
                    'is_active': True,
                    'created': '2024-11-19T07:41:16.001602Z',
                    'updated': '2024-11-19T07:41:25.590598Z'
                }
            ]
        }
    }
)

MANAGED_AGENTS_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'properties': {
            'results': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'Unique identifier for the agent in the managed agents list.'
                        },
                        'name': {
                            'type': 'string',
                            'description': 'The name of the agent.'
                        },
                        'url': {
                            'type': 'string',
                            'format': 'uri',
                            'description': 'URL to the detailed information about the agent.'
                        },
                        'conversation_count': {
                            'type': 'integer',
                            'description': 'The total number of conversations handled by the agent.'
                        },
                        'first_conversation_date': {
                            'type': 'string',
                            'format': 'date-time',
                            'description': 'The date of the first conversation handled by the agent.'
                        },
                        'last_conversation_date': {
                            'type': 'string',
                            'format': 'date-time',
                            'description': 'The date of the last conversation handled by the agent.'
                        },
                    },
                    'example': {
                        'id': 0,
                        'name': 'agent_10',
                        'url': 'http://0.0.0.0:8000/api/v1/agents/14/',
                        'conversation_count': 7,
                        'first_conversation_date': '2024-03-17T00:00:00Z',
                        'last_conversation_date': '2024-12-06T00:00:00Z'
                    }
                }
            },
            'next': {
                'type': 'string',
                'format': 'uri',
                'nullable': True,
                'description': 'URL to the next page of results, if applicable.'
            },
            'previous': {
                'type': 'string',
                'format': 'uri',
                'nullable': True,
                'description': 'URL to the previous page of results, if applicable.'
            },
        },
        'required': ['results', 'next', 'previous'],
        'example': {
            'results': [
                {
                    'id': 0,
                    'name': 'agent_10',
                    'url': 'http://0.0.0.0:8000/api/v1/agents/14/',
                    'conversation_count': 7,
                    'first_conversation_date': '2024-03-17T00:00:00Z',
                    'last_conversation_date': '2024-12-06T00:00:00Z'
                },
                {
                    'id': 1,
                    'name': 'agent_04',
                    'url': 'http://0.0.0.0:8000/api/v1/agents/8/',
                    'conversation_count': 13,
                    'first_conversation_date': '2024-01-03T00:00:00Z',
                    'last_conversation_date': '2024-09-03T00:00:00Z'
                }
            ],
            'next': 'http://0.0.0.0:8000/api/v1/agents/4/managed_agents/?cursor=MTU=',
            'previous': None
        }
    }
)

ERROR_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'properties': {
            'error': {'type': 'string', 'description': 'Detailed error message.'},
        },
        'example': {'error': 'Invalid value provided for parameter X.'}
    },
    description='Error response when the request cannot be processed.'
)

FORBIDDEN_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'properties': {
            'detail': {'type': 'string', 'description': 'Error message indicating access is forbidden.'},
        },
        'example': {'detail': 'You do not have permission to perform this action.'}
    },
    description='Error response when the user is not authorized to access the resource.'
)

NOT_FOUND_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'properties': {
            'detail': {'type': 'string', 'description': 'Error message indicating resource not found.'},
        },
        'example': {'detail': 'Resource not found.'}
    },
    description='Error response when the requested resource does not exist.'
)

VALIDATION_ERROR_RESPONSE_SCHEMA = OpenApiResponse(
    response={
        'type': 'object',
        'properties': {
            'field_name': {
                'type': 'array',
                'items': {'type': 'string'},
                'description': 'List of validation error messages for the field.'
            },
            'non_field_errors': {
                'type': 'array',
                'items': {'type': 'string'},
                'description': 'List of general validation error messages.'
            }
        },
        'example': {
            'field_name': ['This field is required.'],
            'non_field_errors': ['Invalid data provided.']
        }
    },
    description='Error response when input validation fails.'
)
