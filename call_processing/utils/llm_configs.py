TRANSCRIPTION_METHOD_CHOICES = [('deepgram', 'Deepgram'), ('groq', 'Groq')]
ENRICHMENT_METHOD_CHOICES = [('openai', 'OpenAI'), ('vertexai', 'VertexAI')]

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

ENRICHMENT_PROMPT = """
You have the task of summarizing and classifying transcribed calls between two speakers.
One of the speakers in the call is an agent for a company, and the other speaker is a customer. 
The different speakers are indicated by 'Speaker 0' and 'Speaker 1'.
Follow these steps:

STEP 1: SPEAKER IDENTIFICATION
Read through the transcribed dialogue. Identify which of the speakers is the company's agent (usually 
'Speaker 0') and which one is the customer. For extra speaker labels (f.e. 'Speaker 2') that may be present in 
the transcript, assume they are either the customer or the agent. Keep track of the speaker labels that 
correspond to the agent and to the customer.

STEP 2: ACTIVE TOPIC CLASSIFICATION
These are the company's ESTABLISHED TOPICS for call classification:
{topics_string}

Review the conversation and identify which of these established topics apply. Present a list containing the associated
topic names. If none of these topics match, simply return an empty list. Do not invent topics!

STEP 3: SUGGESTED TOPIC CLASSIFICATION
These are PENDING TOPIC SUGGESTIONS that may become official topics:
{suggested_string}

Check if the conversation matches any of these suggested topics. Present a list 
containing the associated topic names. If none of these topics match, simply return an empty list. Do not invent 
topics!

STEP 4: NEW TOPIC DISCOVERY
Identify any conversation themes NOT covered by the established or suggested topics above. Think about what this call is really about and what category would help classify similar future calls. Present them as a list of dictionaries
with keys "name" and "description". The complete list of existing topics is: {topics_string}, {suggested_string}.

STEP 5: CALL SUMMARY
Summarize the call paying attention to: the reason for the call, the topics discussed during the call, and
the agreed upon next steps as a result of the call. Try to keep this summary to six sentences. Do not include 
the names of customers or agents.

STEP 6: CALL TITLE
Define a title that briefly captures the content of the call. Do not include names of customers or agents.

STEP 7: SATISFACTION RATING
Represent probability of customer churn in a scale from 1 to 5, 1 being a customer who will certainly never
interact with the company again, and 5 being a customer that is completely satisfied with the product or service
in question. This is a proxy of the call sentiment.

STEP 8: OUTPUT FORMAT
The output must strictly be in a JSON format with keys "agent_speaker_labels", "customer_speaker_labels", 
"topics", "suggested_topics", "new_topics", "summary", "title", and "sentiment". Do not add any text before or after 
the json.
"""

"""
The following schema contains:
- agent_speaker_labels: A list of speaker label strings that identify the agent in the conversation
- customer_speaker_labels: A list of speaker label strings that identify the customer in the conversation
- topics: A list of established topic strings that match the conversation
- suggested_topics: A list of pending suggested topic strings that match the conversation
- new_topics: A list of objects with "name" and "description" keys for newly discovered topics
- summary: A string summarizing the key points of the conversation
- title: A string that represents the content of the call
- sentiment: An integer that represents the overall sentiment of the call (1-5 scale)
"""
ENRICHMENT_CONFIG = {
    "model": {"openai": "gpt-4.1-mini", "vertexai": "gemini-2.5-flash"},
    "temperature": 0.2,
    "response_format": {
        "type": "json_schema",
        "json_schema": {
            "name": "enrichment_response",
            "schema": {
                "type": "object",
                "properties": {
                    "agent_speaker_labels": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "customer_speaker_labels": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "topics": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "suggested_topics": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "new_topics": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string"
                                },
                                "description": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "name",
                                "description"
                            ]
                        }
                    },
                    "summary": {
                        "type": "string"
                    },
                    "title": {
                        "type": "string"
                    },
                    "sentiment": {
                        "type": "integer"
                    }
                },
                "required": [
                    "agent_speaker_labels",
                    "customer_speaker_labels",
                    "topics",
                    "suggested_topics",
                    "new_topics", 
                    "summary",
                    "title",
                    "sentiment"
                ]
            },
            "strict": True
        }
    }
}
