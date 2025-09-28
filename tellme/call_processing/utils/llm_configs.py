TRANSCRIPTION_METHOD_CHOICES = [('deepgram', 'Deepgram'), ('groq', 'Groq')]
ENRICHMENT_METHOD_CHOICES = [('openai', 'OpenAI'), ('vertexai', 'VertexAI')]
CUSTOMER_IDENTIFICATION_METHOD_CHOICES = [('enrichment', 'Enrichment'), ('redaction', 'Redaction')]

DIARIZATION_PROMPT = """
    You are a helpful diarization assistant, working with transcribed calls between TWO speakers.
    Users provide you with a list of transcribed phrases where the speaker label is always 'Speaker X'.
    Your task is to interpret the conversation and figure out which speaker is saying what.

    Bear in mind the following:

    1. Consecutive messages can come from the same speaker. 
    Check whether the meaning and intent of multiple consecutive messages remains the same.
    For example, one message could be "Speaker X: Regarding the cooking", and the next one could be "Speaker X: Who is the cook?". Both belong to the same speaker.

    2. Within a conversation, one speaker takes the role of "question asker', and the other one responds.
    If you see a questionnaire-like conversation, assume that questions come from one speaker and answers from another.

    The output should have the exact same format and content as the input, substituting 'Speaker X' with 
    'Speaker 0' or 'Speaker 1' as you see fit.
"""

DIARIZATION_CONFIG = {
    "model": "gemini-2.0-flash-001",
    "temperature": 0.2
}

ENRICHMENT_PIPELINE = [
    {
        "name": "speaker_identification",
        "prompt": """
            You have the task of analyzing a transcribed call between a company agent and a customer.
            The speakers are labeled as 'Speaker 0', 'Speaker 1', etc.
            Follow these steps:

            STEP 1: SPEAKER IDENTIFICATION
            Read through the transcribed dialogue and identify which speaker is the company agent and which is the customer.
            The agent typically introduces the company, asks verification questions, provides solutions, or follows company procedures.
            The customer typically seeks help, provides personal information, expresses concerns, or asks questions about services.
            If additional speaker labels appear (e.g., 'Speaker 2'), assign them to either the agent or customer role based on their behavior.

            STEP 2: CUSTOMER INFORMATION EXTRACTION
            From the customer's statements, extract any personal information mentioned during the call:
            - Full name (first and last name if available)
            - Address or location details
            - Birth date, age, or date-related information
            - Phone number or other contact information
            Use empty strings for any information not mentioned in the call.

            STEP 3: OUTPUT FORMAT
            The output must be in JSON format with the following structure:
            {
                "agent_speaker_labels": ["Speaker 0"],
                "customer_speaker_labels": ["Speaker 1"],
                "customer_info": {
                    "full_name": "extracted name or empty string",
                    "address": "extracted address or empty string",
                    "birth_date": "extracted birth date or empty string",
                    "phone_number": "extracted phone number or empty string"
                }
            }
            Do not add any text before or after the JSON.
            """,
        "uses_redacted": False,
        "to_compile": [],
        "config": {
            "model": {"openai": "gpt-4o-mini", "vertexai": "gemini-2.0-flash-001"},
            "temperature": 0.2,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "speaker_identification_response",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "agent_speaker_labels": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "customer_speaker_labels": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "customer_info": {
                                "type": "object",
                                "properties": {
                                    "full_name": {"type": "string"},
                                    "address": {"type": "string"},
                                    "birth_date": {"type": "string"},
                                    "phone_number": {"type": "string"}
                                },
                                "required": ["full_name", "address", "birth_date", "phone_number"]
                            }
                        },
                        "required": ["agent_speaker_labels", "customer_speaker_labels", "customer_info"],
                        "strict": True
                    }
                }
            }
        }
    },
    {
        "name": "topic_analysis",
        "prompt": """
            You have the task of analyzing and classifying a transcribed call between a company agent and a customer.
            The speakers are identified as <agent> and <customer> in the transcript.
            Follow these steps:

            STEP 1: ESTABLISHED TOPIC CLASSIFICATION
            These are the company's ESTABLISHED TOPICS for call classification:
            {{topics_string}}

            Review the conversation and identify which established topics apply. Return a list of matching
            topic names. If no topics match, return an empty list. Do not invent new topics in this step.

            STEP 2: SUGGESTED TOPIC CLASSIFICATION
            These are PENDING TOPIC SUGGESTIONS that may become official topics:
            {{suggested_string}}

            Check if the conversation matches any suggested topics. Return a list of matching topic names.
            If no suggested topics match, return an empty list. Do not invent new topics in this step.

            STEP 3: NEW TOPIC DISCOVERY
            Identify conversation themes NOT covered by established or suggested topics above. Consider what
            this call is fundamentally about and what categories would help classify similar future calls.
            Present new topics as objects with "name" and "description" keys. Be specific and actionable
            in your topic definitions.

            STEP 4: CALL SUMMARY
            Summarize the call focusing on: the reason for the call, main topics discussed, and any agreed-upon
            next steps. Keep the summary to approximately six sentences. Use generic terms like "the customer"
            or "the agent" rather than specific names.

            STEP 5: CALL TITLE
            Create a concise title that captures the essence of the call. Focus on the primary purpose or
            outcome. Do not include customer or agent names.

            STEP 6: SATISFACTION ASSESSMENT
            Evaluate the likelihood of customer churn on a scale of 1-5:
            - 1: Customer will definitely not continue with the company (very dissatisfied)
            - 2: Customer is dissatisfied and likely to leave
            - 3: Customer is neutral, outcome uncertain
            - 4: Customer is satisfied and likely to remain
            - 5: Customer is highly satisfied and will definitely continue

            STEP 7: REVENUE SEARCH QUERY
            Based on the conversation content, generate a specific search query that would
            help identify the products or services being discussed. This should be a realistic product search
            query that could be used on a fashion retail website. Focus on specific product categories, styles,
            or types mentioned in the call. Examples of valid queries: "men sneakers", "women dresses",
            "men sweatshirts", "leather jackets", "running shoes". If the conversation doesn't relate to
            fashion products, return an empty string.

            STEP 8: OUTPUT FORMAT
            The output must be in JSON format with the following structure:
            {
                "topics": ["list of matching established topics"],
                "suggested_topics": ["list of matching suggested topics"],
                "new_topics": [{"name": "topic name", "description": "topic description"}],
                "summary": "call summary text",
                "title": "call title",
                "sentiment": 3,
                "revenue_search_query": "product search query or empty string"
            }
            Do not add any text before or after the JSON.
            """,
        "uses_redacted": True,
        "to_compile": ["topics_string", "suggested_string"],
        "config": {
            "model": {"openai": "gpt-4o-mini", "vertexai": "gemini-2.0-flash-001"},
            "temperature": 0.2,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "topic_analysis_response",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "topics": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "suggested_topics": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "new_topics": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "description": {"type": "string"}
                                    },
                                    "required": ["name", "description"]
                                }
                            },
                            "summary": {"type": "string"},
                            "title": {"type": "string"},
                            "sentiment": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5
                            },
                            "revenue_search_query": {"type": "string"}
                        },
                        "required": ["topics", "suggested_topics", "new_topics", "summary", "title", "sentiment", "revenue_search_query"],
                        "strict": True
                    }
                }
            }
        }
    }
]