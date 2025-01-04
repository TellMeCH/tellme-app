ENRICHMENT_PROMPT = """
    You have the task of summarizing and classifying transcribed calls between two speakers.
    One of the speakers in the call is an agent for a company, and the other speaker is a customer. 
    The different speakers are indicated by 'Speaker 0' and 'Speaker 1'.
    Follow these steps:

    1. Read through the transcribed dialogue. Identify which of the speakers is the company's agent (usually 
    'Speaker 0') and which one is the customer. For extra speaker labels (f.e. 'Speaker 2') that may be present in 
    the transcript, assume they are either the customer or the agent. Keep track of the speaker labels that 
    correspond to the agent and to the customer.
    2. Classify the dialogue into the following topics: {topics_string}. Present a list containing the associated
    topic names. If none of these topics match, simply return an empty list. Do not invent topics!
    3. Summarize the call paying attention to: the reason for the call, the topics discussed during the call, and
    the agreed upon next steps as a result of the call. Try to keep this summary to six sentences. Do not include 
    the names of customers or agents.
    4. Define a title that briefly captures the content of the call. Do not include names of customers or agents.
    5. Represent probability of customer churn in a scale from 1 to 5, 1 being a customer who will certainly never
    interact with the company again, and 5 being a customer that is completely satisfied with the product or service
    in question. This is a proxy of the call sentiment.
    4. The output must strictly be in a JSON format with keys "agent_speaker_labels", "customer_speaker_labels", 
    "topics", "summary", "title", and "sentiment". Do not add any text before or after the json.
"""

"""
The following schema contains:
- agent_speaker_labels: A list of speaker label strings that identify the agent in the conversation
- customer_speaker_labels: A list of speaker label strings that identify the customer in the conversation
- topics: A list of topic strings that classify the conversation.
- summary: A string summarizing the key points of the conversation.
- title: A string that represents the content of the call
- sentiment: An integer that represents the overall sentiment of the call
"""
PROMPT_CONFIG = {
    "model": "gpt-4o-mini-2024-07-18",
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
                    "summary",
                    "title",
                    "sentiment"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    }
}
