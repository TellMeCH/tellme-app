SUMMARIZER_PROMPT = """
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
"""
PROMPT_CONFIG = {
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
}