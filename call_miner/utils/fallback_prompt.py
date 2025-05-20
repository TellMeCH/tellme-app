SUMMARIZER_PROMPTS = {
    'summary_mining': """
        You are a helpful assistant tasked with analyzing customer care interactions to uncover actionable insights about 
        customer behavior and brand perception. Below are summaries of conversations between customer care agents and customers. 
        Analyze these conversations and answer the following questions concisely (2-3 sentences per question):
        1.	What are the recurring reasons customers contact the call center?
        2.	At which stages of the customer journey are these callers predominantly found?
        3.	Are the issues commonly resolved during the initial call, or do they require follow-ups?
        4.	Based on these interactions, are customers more likely to strengthen their relationship with the company or 
            terminate it? Why?
        5.	What are the most frequent causes of customer dissatisfaction in these calls?
        6.	What are the most frequent causes of customer engagement and loyalty in these calls?
        7.	What simple actions could the company take to improve customer satisfaction based on these conversations?
        
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
        actionable insights about an individual customer. Below are summaries of calls
        involving this customer. Answer each question in 2-3 concise sentences:

        1. What products or services does this customer purchase most often?
        2. Which features of those products/services does the customer explicitly appreciate?
        3. Which features do they criticise or dislike?
        4. Have the customer’s expectations been met? If not, how has the company “dropped the ball”?
        5. On a scale from 1 (very unlikely) to 5 (very likely), how probable is it that this customer will churn?
        6. On a scale from 1 (< 500 EUR per year) to 5 (> 5 000 EUR per year), how valuable is this customer for the company?
        7. What broader interests does the customer reveal (hobbies, topics, brands)?
        8. Provide any demographic clues (approx. age range, region, gender, employment status).
        9. What concrete actions could the company take to improve the customer’s perception and overall experience?

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
PROMPT_CONFIGS = {
    "summary_mining": {
        "model": "gpt-4o-mini",
        "temperature": 0.2,
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
        "model": "gpt-4o-mini",
        "temperature": 0.2,
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
                        "Improvement Suggestions": {"type": "string"}
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
                        "Improvement Suggestions"
                    ],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    },
    "agent_summary": {
        "model": "gpt-4o-mini",
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
