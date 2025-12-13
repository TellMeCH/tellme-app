import os
import sys
import argparse
import json
import hashlib
import traceback
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import Mock
from pathlib import Path
import zoneinfo

# Ensure Django is set up before importing anything that relies on settings
import django
from django.conf import settings

# Setup Django if not already configured
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tellme.settings')
    django.setup()

from google import genai
from google.genai import types
from tellme.call_processing.utils.meta_summarization import MetaSummarizer
from tellme.evaluation.metadata import CONVERSATIONS


# LLM evaluation prompt and configuration
EVALUATION_PROMPT = """
You are an expert evaluator assessing the quality of customer meta-summaries.
Your task is to evaluate how well the meta-summary captures insights from multiple customer interactions.

Rate the following aspects on a scale from 0.0 to 1.0 where:
- 0.0 = Completely inadequate or missing critical information
- 0.5 = Partially captures insights, some gaps present
- 1.0 = Excellent, comprehensive, and actionable

Consider the following aspects:
- Favorite Products/Services: Accurately identifies customer preferences
- Liked Features: Captures positive feedback themes
- Disliked Features: Identifies pain points and frustrations
- Expectations Met: Assesses customer satisfaction levels
- Churn Potential: Reasonable assessment of customer retention risk
- Customer Value: Realistic evaluation of customer worth
- Customer Interests: Identifies patterns in customer behavior
- Demographic Profile: Extracts relevant demographic information
- Improvement Suggestions: Provides actionable recommendations
- Suggested Email Body: Professional, empathetic, and addresses key issues
- Suggested Email Subject: Clear and relevant
- Jira Ticket Body: Technical, comprehensive, and actionable
- Jira Ticket Title: Clear and specific

Be objective and focus on comprehensiveness, accuracy, and actionability.
"""

EVALUATION_CONFIG = {
    'model': 'gemini-2.5-pro',
    'temperature': 0.1,
    'response_format': {
        'json_schema': {
            'schema': {
                'type': 'object',
                'properties': {
                    'favorite_products_quality': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Quality of favorite products/services analysis'
                    },
                    'liked_features_quality': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Quality of liked features analysis'
                    },
                    'disliked_features_quality': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Quality of disliked features analysis'
                    },
                    'expectations_met_quality': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Quality of expectations assessment'
                    },
                    'churn_potential_quality': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Quality of churn potential analysis'
                    },
                    'customer_value_quality': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Quality of customer value assessment'
                    },
                    'customer_interests_quality': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Quality of customer interests identification'
                    },
                    'demographic_profile_quality': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Quality of demographic profile'
                    },
                    'improvement_suggestions_quality': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Quality and actionability of improvement suggestions'
                    },
                    'email_quality': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Quality of suggested email (body + subject)'
                    },
                    'jira_quality': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Quality of Jira ticket (body + title)'
                    },
                    'overall_quality': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Overall quality of the meta-summary'
                    }
                },
                'required': [
                    'favorite_products_quality', 'liked_features_quality', 'disliked_features_quality',
                    'expectations_met_quality', 'churn_potential_quality', 'customer_value_quality',
                    'customer_interests_quality', 'demographic_profile_quality', 'improvement_suggestions_quality',
                    'email_quality', 'jira_quality', 'overall_quality'
                ],
                'additionalProperties': False
            }
        }
    }
}


class MetaSummarizationEvaluator:
    """
    Evaluation framework for MetaSummarizer that generates customer summaries
    from all conversations in metadata.py and evaluates their quality using LLM-based comparison.
    """

    def __init__(self, results_file_path: str = "./tellme/evaluation/meta_summarization_results.txt",
                 verbose: bool = False, period: str = 'eternity', rolling: bool = False):
        """
        Initialize the evaluator.

        Args:
            results_file_path: Path to text file for storing evaluation results
            verbose: If True, prints detailed output
            period: Time period for meta-summarization ('week', 'month', 'quarter', 'eternity')
            rolling: Whether to use rolling window for summarization
        """
        self.results_path = results_file_path
        self.verbose = verbose
        self.period = period
        self.rolling = rolling
        self.evaluation_date = datetime.now()
        self.pipeline_hash = self._calculate_pipeline_hash()

        # VertexAI Client for evaluation
        self.vertexai = genai.Client(vertexai=True, project=settings.GOOGLE_CLOUD_PROJECT, location='us-central1')
        self.llm_prompt = EVALUATION_PROMPT
        self.llm_config = EVALUATION_CONFIG

    @staticmethod
    def _calculate_pipeline_hash() -> str:
        """Calculate hash of current meta_summarization script for version tracking."""
        pipeline_file = Path(__file__).parent.parent / "call_processing" / "utils" / "meta_summarization.py"
        if pipeline_file.exists():
            with open(pipeline_file, 'r') as f:
                content = f.read()
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        return "unknown"

    def _create_mock_customer(self) -> Mock:
        """
        Create a mock Customer object with all conversations from metadata.py.

        All conversations are treated as belonging to the same customer.

        Returns:
            Mock: Mock customer object with all conversations
        """
        customer = Mock()
        customer.id = 1
        customer.external_id = "PKZ_TEST_CUSTOMER"
        customer.first_name = "Test"
        customer.last_name = "Customer"

        # Create mock conversations from metadata
        utc = zoneinfo.ZoneInfo("UTC")
        mock_conversations = []

        for i, conv_data in enumerate(CONVERSATIONS):
            conv = Mock()
            conv.id = i + 1
            conv.date = datetime.fromisoformat(conv_data['input']['timestamp']).astimezone(utc)
            conv.summary = conv_data['output'].get('summary', '')
            conv.transcript = conv_data['output'].get('transcript', '')
            conv.sentiment = float(conv_data['output'].get('sentiment', 3))
            conv.revenue_at_stake = float(conv_data['output'].get('revenue_at_stake', 0)) if conv_data['output'].get('revenue_at_stake') else 0
            conv.resolved = conv_data['output'].get('resolved', False)

            mock_conversations.append(conv)

        # Create QuerySet-like object that mimics Django QuerySet behavior
        conversations_qs = Mock()

        # Create a mock that behaves like a QuerySet after filter().order_by()
        # It needs to support: .count(), iteration, and be the final result
        mock_ordered_result = Mock()
        mock_ordered_result.count.return_value = len(mock_conversations)
        # Make it iterable by returning the list of conversations when iterated
        # Note: lambda must accept 'self' parameter since it's called as a method
        mock_ordered_result.__iter__ = lambda self: iter(mock_conversations)

        # Mock filter().order_by() chain to return our QuerySet-like mock
        mock_filter_result = Mock()
        mock_filter_result.order_by.return_value = mock_ordered_result
        conversations_qs.filter.return_value = mock_filter_result

        # Mock values_list().first() chain for getting latest date
        mock_values_list = Mock()
        mock_values_list.first.return_value = mock_conversations[0].date if mock_conversations else None
        conversations_qs.values_list.return_value = mock_values_list

        customer.conversations = conversations_qs
        customer.last_conversation_date = mock_conversations[0].date if mock_conversations else None

        return customer

    def _evaluate_with_llm(self, meta_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to evaluate the quality of the meta-summary.

        Args:
            meta_summary: Generated meta-summary from MetaSummarizer

        Returns:
            Dict containing LLM evaluation results
        """
        # Prepare conversation context for evaluation
        conversation_summaries = []
        for conv in CONVERSATIONS:
            conv_summary = f"""
File: {conv['input']['file_name']}
Date: {conv['input']['timestamp']}
Summary: {conv['output'].get('summary', 'N/A')}
Sentiment: {conv['output'].get('sentiment', 'N/A')}
Topics: {', '.join(conv['output'].get('topics', []))}
Resolved: {conv['output'].get('resolved', 'N/A')}
Revenue at Stake: {conv['output'].get('revenue_at_stake', 'N/A')}
"""
            conversation_summaries.append(conv_summary)

        conversations_context = "\n---\n".join(conversation_summaries)

        # Format meta-summary for evaluation
        meta_summary_text = json.dumps(meta_summary, indent=2)

        try:
            generation = self.vertexai.models.generate_content(
                model=self.llm_config['model'],
                contents=f"""
                Here are all the individual conversations from this customer:

                {conversations_context}

                ---

                Here is the generated customer meta-summary:

                {meta_summary_text}

                Please evaluate the quality of this meta-summary based on how well it captures
                insights from all the conversations above.
                """,
                config=types.GenerateContentConfig(
                    system_instruction=self.llm_prompt,
                    temperature=self.llm_config['temperature'],
                    response_mime_type="application/json",
                    response_schema=self.llm_config["response_format"]["json_schema"]["schema"]
                ),
            )

            llm_response = json.loads(generation.candidates[0].content.parts[0].text)
            return llm_response

        except Exception as e:
            print(f"LLM evaluation failed: {e}")
            traceback.print_exc()
            # Return default scores
            return {
                'favorite_products_quality': 0.0,
                'liked_features_quality': 0.0,
                'disliked_features_quality': 0.0,
                'expectations_met_quality': 0.0,
                'churn_potential_quality': 0.0,
                'customer_value_quality': 0.0,
                'customer_interests_quality': 0.0,
                'demographic_profile_quality': 0.0,
                'improvement_suggestions_quality': 0.0,
                'email_quality': 0.0,
                'jira_quality': 0.0,
                'overall_quality': 0.0
            }

    def print_meta_summary(self, meta_summary: Dict[str, Any], evaluation: Dict[str, Any]):
        """Print the meta-summary and evaluation results."""
        print("\n" + "="*80)
        print("GENERATED CUSTOMER META-SUMMARY")
        print("="*80)

        for key, value in meta_summary.items():
            print(f"\n{key}:")
            # Truncate very long values
            value_str = str(value)
            if len(value_str) > 500:
                print(f"  {value_str[:500]}...")
                print(f"  [... {len(value_str) - 500} more characters]")
            else:
                print(f"  {value_str}")

            # Print evaluation score if available
            quality_key = f"{key.lower().replace(' ', '_').replace('/', '_')}_quality"
            if quality_key in evaluation:
                score = evaluation[quality_key]
                status = "✓" if score >= 0.7 else "~" if score >= 0.4 else "✗"
                print(f"  [{status} Quality Score: {score:.2f}]")

        print("\n" + "="*80)
        print("EVALUATION SCORES")
        print("="*80)

        for metric, score in evaluation.items():
            status = "✓" if score >= 0.7 else "~" if score >= 0.4 else "✗"
            print(f"{status} {metric:40}: {score:.2f}")

    def run_evaluation(self) -> Dict[str, Any]:
        """
        Run the complete evaluation on customer meta-summarization.

        Returns:
            Dict containing evaluation results
        """
        print(f"Starting meta-summarization evaluation at {self.evaluation_date}")
        print(f"Pipeline hash: {self.pipeline_hash}")
        print(f"Period: {self.period}, Rolling: {self.rolling}")
        print(f"Total conversations in metadata.py: {len(CONVERSATIONS)}")
        print("All conversations will be treated as belonging to the same customer.")

        try:
            # Initialize MetaSummarizer
            print("\nInitializing MetaSummarizer...")
            summarizer = MetaSummarizer()

            # Create mock customer with all conversations
            print("Creating mock customer with all conversations...")
            customer = self._create_mock_customer()

            # Prepare trace data for Langfuse
            trace_data = {
                'name': 'customer_meta_summary_evaluation',
                'tags': ['evaluation', 'customer_summary', 'metadata'],
                'metadata': {
                    'object': "<class 'tellme.call_miner.models.Customer'>",
                    'evaluation_date': self.evaluation_date.isoformat(),
                    'period': self.period,
                    'rolling': self.rolling,
                    'conversation_count': len(CONVERSATIONS)
                }
            }

            # Run meta-summarization
            print("\nRunning MetaSummarizer on all conversations...")
            meta_summary, latest_date, call_count, label = summarizer(
                obj=customer,
                period=self.period,
                rolling=self.rolling,
                trace_data=trace_data
            )

            if meta_summary is None:
                print("✗ MetaSummarizer returned None (no conversations to summarize)")
                return {
                    'success': False,
                    'error': 'No summary generated',
                    'meta_summary': None,
                    'evaluation': None
                }

            print(f"✓ Meta-summary generated successfully")
            print(f"  Latest conversation date: {latest_date}")
            print(f"  Call count: {call_count}")
            print(f"  Period label: {label}")

            # Evaluate the meta-summary
            print("\nEvaluating meta-summary quality with LLM...")
            evaluation = self._evaluate_with_llm(meta_summary)

            # Print results
            if self.verbose:
                self.print_meta_summary(meta_summary, evaluation)

            # Calculate average score
            scores = [v for v in evaluation.values() if isinstance(v, (int, float))]
            avg_score = sum(scores) / len(scores) if scores else 0

            print(f"\n✓ Evaluation completed")
            print(f"  Average quality score: {avg_score:.3f}")

            # Prepare result
            result = {
                'success': True,
                'evaluation_date': self.evaluation_date.isoformat(),
                'pipeline_hash': self.pipeline_hash,
                'period': self.period,
                'rolling': self.rolling,
                'conversation_count': call_count,
                'latest_date': latest_date.isoformat() if latest_date else None,
                'period_label': label,
                'meta_summary': meta_summary,
                'evaluation': evaluation,
                'average_score': avg_score,
                'error': None
            }

            # Save results
            self._save_results(result)

            return result

        except Exception as e:
            print(f"✗ Error during evaluation: {str(e)}")
            traceback.print_exc()

            result = {
                'success': False,
                'evaluation_date': self.evaluation_date.isoformat(),
                'pipeline_hash': self.pipeline_hash,
                'period': self.period,
                'rolling': self.rolling,
                'error': str(e),
                'meta_summary': None,
                'evaluation': None,
                'average_score': 0.0
            }

            self._save_results(result)
            return result

    def _save_results(self, result: Dict[str, Any]):
        """Save evaluation results to text file."""
        with open(self.results_path, 'a', encoding='utf-8') as f:
            f.write("\n" + "="*80 + "\n")
            f.write(f"EVALUATION RUN: {result['evaluation_date']}\n")
            f.write("="*80 + "\n\n")

            f.write(f"Pipeline Hash: {result['pipeline_hash']}\n")
            f.write(f"Period: {result['period']}\n")
            f.write(f"Rolling: {result['rolling']}\n")
            f.write(f"Success: {result['success']}\n")

            if result['error']:
                f.write(f"\nERROR: {result['error']}\n")
            else:
                f.write(f"Conversation Count: {result['conversation_count']}\n")
                f.write(f"Period Label: {result['period_label']}\n")
                f.write(f"Latest Date: {result['latest_date']}\n")
                f.write(f"Average Quality Score: {result['average_score']:.3f}\n\n")

                f.write("META-SUMMARY:\n")
                f.write("-"*80 + "\n")
                f.write(json.dumps(result['meta_summary'], indent=2))
                f.write("\n\n")

                f.write("EVALUATION SCORES:\n")
                f.write("-"*80 + "\n")
                for metric, score in result['evaluation'].items():
                    status = "✓" if score >= 0.7 else "~" if score >= 0.4 else "✗"
                    f.write(f"{status} {metric:40}: {score:.3f}\n")

            f.write("\n")

        print(f"\n✓ Results saved to: {self.results_path}")


def main():
    """Main entry point for the evaluation script."""

    # Verify required API keys are available
    required_keys = [
        'OPENAI_API_KEY',
        'GOOGLE_CLOUD_PROJECT'
    ]

    missing_keys = []
    for key in required_keys:
        if not hasattr(settings, key) or not getattr(settings, key):
            missing_keys.append(key)

    if missing_keys:
        print(f"Warning: Missing required API keys: {', '.join(missing_keys)}")
        print("Some features may not work correctly.")
        print("Make sure these are set in your .env file or environment variables.")
        print("Continuing with limited functionality...\n")
    else:
        print("Environment setup complete. All required API keys found.\n")

    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description='Evaluate MetaSummarizer performance on customer data from metadata.py'
        )
        parser.add_argument('--verbose', '-v', action='store_true',
                          help='Show detailed output including full meta-summary')
        parser.add_argument('--period', type=str, default='eternity',
                          choices=['week', 'month', 'quarter', 'eternity'],
                          help='Time period for summarization (default: eternity)')
        parser.add_argument('--rolling', action='store_true',
                          help='Use rolling window for summarization')
        parser.add_argument('--output', type=str,
                          default='./tellme/evaluation/meta_summarization_results.txt',
                          help='Output file path for results')

        args = parser.parse_args()

        evaluator = MetaSummarizationEvaluator(
            results_file_path=args.output,
            verbose=args.verbose,
            period=args.period,
            rolling=args.rolling
        )

        print("Configuration:")
        print(f"  Period:          {evaluator.period}")
        print(f"  Rolling:         {evaluator.rolling}")
        print(f"  Verbose:         {evaluator.verbose}")
        print(f"  Output file:     {evaluator.results_path}")
        print(f"  Pipeline hash:   {evaluator.pipeline_hash}")
        print(f"  Conversations:   {len(CONVERSATIONS)} (from metadata.py)")
        print()

        # Run evaluation
        result = evaluator.run_evaluation()

        # Print summary
        print("\n" + "="*80)
        print("EVALUATION SUMMARY")
        print("="*80)

        if result['success']:
            print(f"\n✓ Evaluation completed successfully")

            evaluation = result['evaluation']

            # Print score breakdown
            print("\nQuality Score Breakdown:")
            for metric, score in sorted(evaluation.items(), key=lambda x: x[1], reverse=True):
                status = "✓" if score >= 0.7 else "~" if score >= 0.4 else "✗"
                print(f"  {status} {metric:40}: {score:.3f}")

            print(f"\nOverall Average: {result['average_score']:.3f}")
            print(f"\nResults saved to: {evaluator.results_path}")
        else:
            print(f"\n✗ Evaluation failed: {result['error']}")

        print("\nEvaluation completed!")

    except Exception as e:
        print(f"Error running evaluation: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
