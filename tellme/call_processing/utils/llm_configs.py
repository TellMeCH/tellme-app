# API Retry Configuration
API_MAX_RETRIES: int = 5
API_BASE_DELAY: float = 5.0
API_BACKOFF_FACTOR: int = 2
API_REQUEST_TIMEOUT: float = 300

TRANSCRIPTION_METHOD_CHOICES = [('deepgram', 'Deepgram'), ('groq', 'Groq')]

# Transcription Model Names
TRANSCRIPTION_MODEL_NAME_DEEPGRAM: str = 'whisper-medium'
TRANSCRIPTION_MODEL_NAME_GROQ: str = 'whisper-large-v3'

DIARIZATION_CONFIG = {
    "model": "vertex_ai/gemini-2.0-flash-001",
    "fallback_model": "openai/gpt-4o-mini",
    "temperature": 0.2
}

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

ENRICHMENT_METHOD_CHOICES = [('openai', 'OpenAI'), ('vertexai', 'VertexAI')]
CUSTOMER_IDENTIFICATION_METHOD_CHOICES = [('enrichment', 'Enrichment'), ('redaction', 'Redaction')]

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
            - Postcode or postal code (from address or separately mentioned)
            - Loyalty number, membership number, or customer ID
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
                    "phone_number": "extracted phone number or empty string",
                    "postcode": "extracted postcode or empty string",
                    "loyalty_number": "extracted loyalty/membership number or empty string"
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
                                    "phone_number": {"type": "string"},
                                    "postcode": {"type": "string"},
                                    "loyalty_number": {"type": "string"}
                                },
                                "required": ["full_name", "address", "birth_date", "phone_number", "postcode", "loyalty_number"]
                            }
                        },
                        "required": ["agent_speaker_labels", "customer_speaker_labels", "customer_info"],
                    },
                    "strict": True
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
            Evaluate customer satisfaction at three points in the conversation on a scale of 1-5:

            Overall call sentiment (likelihood of customer churn):
            - 1: Customer will definitely not continue with the company (very dissatisfied)
            - 2: Customer is dissatisfied and likely to leave
            - 3: Customer is neutral, outcome uncertain
            - 4: Customer is satisfied and likely to remain
            - 5: Customer is highly satisfied and will definitely continue

            Starting sentiment (customer's initial mood/satisfaction at the beginning of the call):
            - 1: Very upset, frustrated, or angry when the call started
            - 2: Dissatisfied or concerned at the beginning
            - 3: Neutral or business-like at the start
            - 4: Positive or friendly when the call began
            - 5: Very happy or enthusiastic at the beginning

            Ending sentiment (customer's final mood/satisfaction at the end of the call):
            - 1: Very upset, frustrated, or angry when the call ended
            - 2: Still dissatisfied or unresolved at the end
            - 3: Neutral or indifferent when ending
            - 4: Satisfied or pleased at the end
            - 5: Very happy or grateful when the call concluded

            STEP 7: REVENUE SEARCH QUERY
            Identify any distinct products or services being discussed. For example, if the customer is calling to
            complain about an order mix-up, identify what item the customer initially ordered. If the customer asks
            questions about a particular product, identify that product. Then come up with a search query that would
            allow one to find the product online. For example, if the customer is asking about a pair of men's sneakers,
            your query is "men sneakers". If the customer is complaining about a damaged dress, the query is "women
            dresses". Generate the search query in {{organization_language}} language. For example, if this language is
            "English": use "men sneakers", "women dresses",  if organization_language is "German": use "herren sneaker", 
            "damen kleider", etc. If you can't identify a specific item, simply return an empty string. 
            
            STEP 8: RESOLUTION STATUS
            Based on the content of the call, determine whether the conversation resolved the customer issue or not. In
            other words, will the same customer contact the company again to solve the issue? If so, the issue was not
            resolved. Return this as a boolean.

            STEP 9: OUTPUT FORMAT
            The output must be in JSON format with the following structure:
            {
                "topics": ["list of matching established topics"],
                "suggested_topics": ["list of matching suggested topics"],
                "new_topics": [{"name": "topic name", "description": "topic description"}],
                "summary": "call summary text",
                "title": "call title",
                "sentiment": 3,
                "starting_sentiment": 2,
                "ending_sentiment": 4,
                "revenue_search_query": "product search query or empty string",
                "resolved": false
            }
            Do not add any text before or after the JSON.
            """,
        "uses_redacted": True,
        "to_compile": ["topics_string", "suggested_string", "organization_language"],
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
                            "starting_sentiment": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5
                            },
                            "ending_sentiment": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 5
                            },
                            "revenue_search_query": {"type": "string"},
                            "resolved": {"type": "boolean"}
                        },
                        "required": ["topics", "suggested_topics", "new_topics", "summary", "title", "sentiment", "starting_sentiment", "ending_sentiment", "revenue_search_query", "resolved"]
                    },
                    "strict": True
                }
            }
        }
    }
]

# Meta-summarization fallback model (Gemini backup for OpenAI)
META_SUMMARIZATION_MODEL_GEMINI: str = 'vertex_ai/gemini-2.0-flash-001'

SUMMARIZER_PROMPTS = {
    'summary_mining': """
        You are a helpful assistant tasked with analyzing customer care interactions to uncover actionable insights about
        customer behavior and brand perception. Below are summaries of conversations between customer care agents and customers.
        Analyze these conversations and answer the questions below. Follow this reasoning when analyzing these conversations:
        a low sentiment and a high revenue at stake imply high risk of a painful loss of revenue, whereas a high sentiment
        and a relatively low revenue at stake indicate potential for upselling.
        1.	What are the recurring reasons customers contact the call center? Present the result as a bulleted list of 
            descending order of relevance, with maximum 4 items.
        2.	At which stages of the customer journey are these callers predominantly found? Answer in 2-3 lines.
        3.	Are the issues commonly resolved during the initial call, or do they require follow-ups? Answer in 2-3 lines.
        4.	Based on these interactions, are customers more likely to strengthen their relationship with the company or
            terminate it? Why? Answer in 2-3 lines.
        5.	What are the most frequent causes of customer dissatisfaction in these calls? Present the result as a 
            bulleted list of descending order of relevance, with maximum 4 items.
        6.	What are the most frequent causes of customer engagement and loyalty in these calls? Present the result as a
            bulleted list of descending order of relevance, with maximum 4 items.
        7.	What simple actions could the company take to improve customer satisfaction based on these conversations? 
            This is key question. Think of specific, tangible improvements in business processes and customer handling
            that would minimize churn and ensure customer retention. Provide them as a bulleted list of descending 
            impact, so that readers will instantly know the specific actions that really move the needle. 
            Keep the list to maximum 5 items.

        Provide the results in a JSON format with the following keys:
        •	“Reasons for Calling”
        •	“Stages of the Customer Journey”
        •	“Call Resolution Rates”
        •	“Churn Potential”
        •	“Causes for Dissatisfaction”
        •	“Causes for Engagement”
        •	“Suggested Actions”
    """,
    'customer_summary': """
        You are a helpful assistant tasked with analysing customer-care interactions for
        actionable insights about an individual customer. Below are transcripts or summaries of calls
        involving this customer. Follow this reasoning when analyzing these conversations:
        a low sentiment and a high revenue at stake imply high risk of a painful loss of revenue, whereas a high sentiment
        and a relatively low revenue at stake indicate potential for upselling. Answer these questions:
        
        1. What products or services does this customer purchase most often?
        2. Which features of those products/services does the customer explicitly appreciate? Answer in 2-3 lines.
        3. Which features do they criticise or dislike? Answer in 2-3 lines.
        4. Have the customer’s expectations been met? If not, how has the company “dropped the ball”? Present the result as a bulleted list of descending order of relevance, with maximum 4 items.
        5. On a scale from 1 (very unlikely) to 5 (very likely), how probable is it that this customer will churn?
        6. On a scale from 1 (< 100 EUR per year) to 5 (> 10000 EUR per year), how valuable is this customer for the company?
        7. What broader interests does the customer reveal (hobbies, topics, brands)?
        8. Provide any demographic clues (approx. age range, region, gender, employment status).
        9. What concrete actions could the company take to improve the customer’s perception and overall experience? Based on the conversations, is there any potential for upselling or cross-selling that will retain the customer? Present the result as a bulleted list of descending order of relevance, with maximum 4 items.
        10. Generate an email template that would comfort the customer. Be apologetic and show empathy. Your goal is to make sure the customer feels inclined to purchase again. If the topic has/should be forward to someone else, let them know. This should correspond to the email body. Make sure that the resulting format is formal, with an adequate number of line breaks between greeting and body sections.
        11. Following step 10., generate the email subject that would best fit
        12. Create a Jira ticket that can be redirected to the adequate department to take care of the issue. Structure it as follows: brief context (3-4 bullet points), recommended actions (3-4 bullet points).
        13. Following step 12, generate a title for the Jira ticket that would best fit
        
        Provide the results in a JSON object with exactly these keys:
        • “Favorite Products/Services”
        • “Liked Features”
        • “Disliked Features”
        • “Expectations Met”
        • “Churn Potential”
        • “Customer Value”
        • “Customer Interests”
        • “Demographic Profile”
        • “Improvement Suggestions”
        • “Suggested Email Body”
        • “Suggested Email Subject”
        • “Jira Ticket Body”
        • “Jira Ticket Title”
        
        Important: 
            - For all bulleted lists, follow this format: "- Item A\n- Item B\n- Item C"!
            - All responses should be in English, except the Email Body in Subject, which should be in the customer's language!
    """,
    'agent_summary': """
        You are a helpful assistant tasked with analysing customer-care interactions for
        actionable insights about a specific agent. Below are summaries of this agent’s calls.
        Answer each question in 2-3 concise sentences:

        1. Which issues does this agent most frequently handle?
        2. Roughly what percentage of those issues are resolved within the first call?
        3. Does the agent use professional and empathetic language?
        4. Do the transcripts indicate the agent may be close to burnout? Cite behavioural clues.
        5. What specific coaching, resources, or process changes would help this agent improve?

        Provide the results in a JSON object with exactly these keys:
        • “Recurring Issues”
        • “First Call Resolution Rate”
        • “Language Appropriateness”
        • “Burnout Assessment”
        • “Improvement Suggestions”
    """
}

SUMMARIZER_CONFIGS = {
    "summary_mining": {
        "model": "openai/gpt-5-nano",
        "temperature": 1,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "summarizer_response",
                "schema": {
                    "type": "object",
                    "properties": {
                        "Reasons for Calling": {
                            "type": "string"
                        },
                        "Stages of the Customer Journey": {
                            "type": "string"
                        },
                        "Call Resolution Rates": {
                            "type": "string"
                        },
                        "Churn Potential": {
                            "type": "string"
                        },
                        "Causes for Dissatisfaction": {
                            "type": "string"
                        },
                        "Causes for Engagement": {
                            "type": "string"
                        },
                        "Suggested Actions": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "Reasons for Calling",
                        "Stages of the Customer Journey",
                        "Call Resolution Rates",
                        "Churn Potential",
                        "Causes for Dissatisfaction",
                        "Causes for Engagement",
                        "Suggested Actions"
                    ],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    },
    "customer_summary": {
        "model": "openai/gpt-5-nano",
        "temperature": 1,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "customer_summary_response",
                "schema": {
                    "type": "object",
                    "properties": {
                        "Favorite Products/Services": {"type": "string"},
                        "Liked Features": {"type": "string"},
                        "Disliked Features": {"type": "string"},
                        "Expectations Met": {"type": "string"},
                        "Churn Potential": {"type": "string"},
                        "Customer Value": {"type": "string"},
                        "Customer Interests": {"type": "string"},
                        "Demographic Profile": {"type": "string"},
                        "Improvement Suggestions": {"type": "string"},
                        "Suggested Email Body": {"type": "string"},
                        "Suggested Email Subject": {"type": "string"},
                        "Jira Ticket Body": {"type": "string"},
                        "Jira Ticket Title": {"type": "string"},
                    },
                    "required": [
                        "Favorite Products/Services",
                        "Liked Features",
                        "Disliked Features",
                        "Expectations Met",
                        "Churn Potential",
                        "Customer Value",
                        "Customer Interests",
                        "Demographic Profile",
                        "Improvement Suggestions",
                        "Suggested Email Body",
                        "Suggested Email Subject",
                        "Ticket Title",
                        "Ticket Description",
                        "Jira Ticket Body",
                        "Jira Ticket Title"
                    ],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    },
    "agent_summary": {
        "model": "openai/gpt-4o-mini",
        "temperature": 0.2,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "agent_summary_response",
                "schema": {
                    "type": "object",
                    "properties": {
                        "Recurring Issues": {"type": "string"},
                        "First Call Resolution Rate": {"type": "string"},
                        "Language Appropriateness": {"type": "string"},
                        "Burnout Assessment": {"type": "string"},
                        "Improvement Suggestions": {"type": "string"}
                    },
                    "required": [
                        "Recurring Issues",
                        "First Call Resolution Rate",
                        "Language Appropriateness",
                        "Burnout Assessment",
                        "Improvement Suggestions"
                    ],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    }
}
