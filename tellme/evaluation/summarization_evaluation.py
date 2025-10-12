import os
import sys
import time
import json
import argparse
import csv
from datetime import datetime
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock
from pathlib import Path

# Ensure Django is set up before importing anything that relies on settings
import django
from django.conf import settings

# Setup Django if not already configured
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tellme.settings')
    django.setup()

from tellme.call_miner.utils.summary_mining import condense_summaries
from tellme.evaluation.metadata import CONVERSATIONS


# Model configurations for evaluation
MODELS_TO_EVALUATE = [
    # GPT-4 Family
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",

    # GPT-5 Family
    "gpt-5",
    "gpt-5-mini",
    "gpt-5-nano"
]

# OpenAI pricing per 1K tokens (Standard tier - as of latest official pricing)
# Prices are per 1M tokens from OpenAI, converted to per 1K tokens
PRICING_PER_1K_TOKENS = {
    # Current GPT-4o models
    "gpt-4o": {"input": 0.0025, "output": 0.010},  # $2.50/$10.00 per 1M tokens
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},  # $0.15/$0.60 per 1M tokens

    # GPT-5 family (current official pricing)
    "gpt-5": {"input": 0.00125, "output": 0.010},  # $1.25/$10.00 per 1M tokens
    "gpt-5-mini": {"input": 0.00025, "output": 0.002},  # $0.25/$2.00 per 1M tokens
    "gpt-5-nano": {"input": 0.00005, "output": 0.0004},  # $0.05/$0.40 per 1M tokens

    # Additional current models
    "gpt-4.1": {"input": 0.002, "output": 0.008},  # $2.00/$8.00 per 1M tokens
    "gpt-4.1-mini": {"input": 0.0004, "output": 0.0016},  # $0.40/$1.60 per 1M tokens
    "gpt-4.1-nano": {"input": 0.0001, "output": 0.0004},  # $0.10/$0.40 per 1M tokens
}


class SummarizationEvaluator:
    """
    Evaluation framework for testing different LLM models on summarization tasks.
    Tests performance, cost, quality, and latency across multiple models.
    """

    def __init__(self, results_file_path: str = "./tellme/evaluation/summarization_evaluation_results.txt"):
        """
        Initialize the summarization evaluator.

        Args:
            results_file_path: Path to TXT file for storing evaluation results
        """
        self.results_file_path = results_file_path
        self.evaluation_date = datetime.now()

        # Extract summaries from conversation metadata
        self._enrich_summary_text()

        print(f"Loaded {len(self.summaries)} summaries for evaluation")

    def _enrich_summary_text(self):
        enriched_template = "({date}, Sentiment: {sentiment}/5, Revenue at Stake: {revenue}, Resolved: {resolved}) {summary}"
        self.summaries = []
        for conv in CONVERSATIONS:
            self.summaries.append(
                enriched_template.format(
                    date=conv['input']['timestamp'],
                    sentiment=conv['output']['sentiment'],
                    revenue=conv['output']['revenue_at_stake'],
                    resolved=conv['output']['resolved'],
                    summary=conv['output']['summary']
                )
            )

    @staticmethod
    def _create_mock_prompt(model_name: str):
        """
        Create a mock prompt object for the given model.

        Args:
            model_name: The model to use in the configuration

        Returns:
            Mock prompt object with fixed prompt text and model-specific config
        """
        mock_prompt = MagicMock()
        mock_prompt.prompt = """
        You are a helpful assistant tasked with analyzing customer care interactions to uncover actionable insights about
        customer behavior and brand perception. Below are summaries of conversations between customer care agents and customers.
        Analyze these conversations and answer the questions below. Follow this reasoning when analyzing these conversations:
        a low sentiment and a high revenue at stake imply high risk of a painful loss of revenue, whereas a high sentiment
        and a relatively low revenue at stake indicate potential for upselling.
        1.	What are the recurring reasons customers contact the call center? Present the result as a bulleted list of 
            descending order of relevance.
        2.	At which stages of the customer journey are these callers predominantly found? Answer in 2-3 lines.
        3.	Are the issues commonly resolved during the initial call, or do they require follow-ups? Answer in 2-3 lines.
        4.	Based on these interactions, are customers more likely to strengthen their relationship with the company or
            terminate it? Why? Answer in 2-3 lines.
        5.	What are the most frequent causes of customer dissatisfaction in these calls? Present the result as a 
            bulleted list of descending order of relevance.
        6.	What are the most frequent causes of customer engagement and loyalty in these calls? Present the result as a
            bulleted list of descending order of relevance.
        7.	What simple actions could the company take to improve customer satisfaction based on these conversations? 
            This is key question. Think of specific, tangible improvements in business processes and customer handling
            that would minimize churn and ensure customer retention. Provide them as a bulleted list of descending 
            impact, so that readers will instantly know the specific actions that really move the needle.

        Provide the results in a JSON format with the following keys:
        "	"Reasons for Calling"
        "	"Stages of the Customer Journey"
        "	"Call Resolution Rates"
        "	"Churn Potential"
        "	"Causes for Dissatisfaction"
        "	"Causes for Engagement"
        "	"Suggested Actions"
        """

        mock_prompt.config = {
            "model": model_name,
            "temperature": 0.2 if '5' not in model_name else 1,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "summarizer_response",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "Reasons for Calling": {"type": "string"},
                            "Stages of the Customer Journey": {"type": "string"},
                            "Call Resolution Rates": {"type": "string"},
                            "Churn Potential": {"type": "string"},
                            "Causes for Dissatisfaction": {"type": "string"},
                            "Causes for Engagement": {"type": "string"},
                            "Suggested Actions": {"type": "string"}
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
        mock_prompt.is_fallback = False

        return mock_prompt

    @staticmethod
    def _calculate_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate the cost for a given model and token usage.

        Args:
            model_name: Name of the model used
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Total cost in USD
        """
        if model_name not in PRICING_PER_1K_TOKENS:
            return 0.0

        pricing = PRICING_PER_1K_TOKENS[model_name]
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]

        return input_cost + output_cost

    def evaluate_model(self, model_name: str) -> Dict[str, Any]:
        """
        Evaluate a single model on the summarization task.

        Args:
            model_name: Name of the model to evaluate

        Returns:
            Dictionary containing evaluation results
        """
        print(f"\n{'='*60}")
        print(f"Evaluating model: {model_name}")
        print(f"{'='*60}")

        # Create mock trace data for the evaluation
        trace_data = {
            'name': f'summarization_eval_{model_name}',
            'tags': ['evaluation'],
            'metadata': {
                'object': "<class 'tellme.call_miner.models.Topic'>",
                'model': model_name,
                'evaluation_date': self.evaluation_date.isoformat()
            }
        }

        try:
            # Mock Langfuse to return our custom prompt with the specified model
            mock_prompt = self._create_mock_prompt(model_name)

            with patch('tellme.call_miner.utils.summary_mining.Langfuse') as mock_langfuse_class:
                mock_langfuse_instance = MagicMock()
                mock_langfuse_instance.get_prompt.return_value = mock_prompt
                mock_langfuse_class.return_value = mock_langfuse_instance

                # Record start time
                start_time = time.time()

                # Call condense_summaries with our test data
                result = condense_summaries(self.summaries, trace_data)

                # Record end time
                end_time = time.time()
                latency = end_time - start_time

                # The function should return a dictionary with the summarization results
                # We need to extract token usage from the actual OpenAI call
                # For now, we'll simulate this since we can't easily intercept the OpenAI client

                # Try to access the mock to get call information
                print(f" Model: {model_name}")
                print(f" Latency: {latency:.2f} seconds")
                print(f" Generated response successfully")

                # Print the response (truncated for readability)
                if isinstance(result, dict):
                    print(f" Response type: Dictionary with {len(result)} keys")
                    print(f"\n📋 FULL GENERATED SUMMARY:")
                    print("-" * 40)
                    for key, value in result.items():
                        print(f"\n🔹 {key}:")
                        print(f"{str(value)}")
                    print("-" * 40)
                else:
                    print(f" Response: {str(result)[:200]}{'...' if len(str(result)) > 200 else ''}")

                # For demonstration purposes, we'll use estimated token counts
                # In a real implementation, you'd intercept the OpenAI client call to get actual usage
                estimated_input_tokens = len(' '.join(self.summaries).split()) * 1.3  # Rough estimate
                estimated_output_tokens = len(str(result).split()) * 1.3 if result else 0

                estimated_cost = self._calculate_cost(model_name, estimated_input_tokens, estimated_output_tokens)

                print(f" Estimated input tokens: {estimated_input_tokens:.0f}")
                print(f" Estimated output tokens: {estimated_output_tokens:.0f}")
                print(f" Estimated cost: ${estimated_cost:.4f}")

                return {
                    'model_name': model_name,
                    'success': True,
                    'latency_seconds': latency,
                    'estimated_input_tokens': int(estimated_input_tokens),
                    'estimated_output_tokens': int(estimated_output_tokens),
                    'estimated_cost_usd': estimated_cost,
                    'response_length': len(str(result)) if result else 0,
                    'response_type': type(result).__name__,
                    'has_response': result is not None,
                    'generated_response': json.dumps(result, indent=2) if result else None,
                    'error': None,
                    'evaluation_date': self.evaluation_date.isoformat()
                }

        except Exception as e:
            print(f" Error evaluating {model_name}: {str(e)}")
            return {
                'model_name': model_name,
                'success': False,
                'latency_seconds': None,
                'estimated_input_tokens': None,
                'estimated_output_tokens': None,
                'estimated_cost_usd': None,
                'response_length': None,
                'response_type': None,
                'has_response': False,
                'generated_response': None,
                'error': str(e),
                'evaluation_date': self.evaluation_date.isoformat()
            }

    def run_evaluation(self, models: List[str] = None) -> Dict[str, Any]:
        """
        Run evaluation across multiple models.

        Args:
            models: List of model names to evaluate. If None, uses default list.

        Returns:
            Dictionary containing overall results
        """
        models_to_test = models or MODELS_TO_EVALUATE

        print(f"Starting summarization evaluation at {self.evaluation_date}")
        print(f"Testing {len(models_to_test)} models on {len(self.summaries)} conversation summaries")

        results = []
        successful_results = []

        for model_name in models_to_test:
            result = self.evaluate_model(model_name)
            results.append(result)

            if result['success']:
                successful_results.append(result)

        # Save results to text file
        self._save_results_to_txt(results)

        # Print summary
        print(f"\n{'='*60}")
        print("EVALUATION SUMMARY")
        print(f"{'='*60}")

        print(f"Total models tested: {len(results)}")
        print(f"Successful evaluations: {len(successful_results)}")
        print(f"Success rate: {len(successful_results)/len(results)*100:.1f}%")

        if successful_results:
            # Sort by latency for performance comparison
            successful_results.sort(key=lambda x: x['latency_seconds'])

            print(f"\nPerformance Ranking (by latency):")
            for i, result in enumerate(successful_results, 1):
                print(f"{i:2d}. {result['model_name']:<20} - {result['latency_seconds']:.2f}s - ${result['estimated_cost_usd']:.4f}")

            # Cost comparison
            successful_results.sort(key=lambda x: x['estimated_cost_usd'])
            print(f"\nCost Ranking (by estimated cost):")
            for i, result in enumerate(successful_results, 1):
                print(f"{i:2d}. {result['model_name']:<20} - ${result['estimated_cost_usd']:.4f} - {result['latency_seconds']:.2f}s")

        print(f"\nDetailed results saved to: {self.results_file_path}")

        return {
            'total_models': len(results),
            'successful_evaluations': len(successful_results),
            'success_rate': len(successful_results)/len(results) if results else 0,
            'results': results,
            'evaluation_date': self.evaluation_date.isoformat()
        }

    def _save_results_to_txt(self, results: List[Dict[str, Any]]):
        """Save evaluation results to text file with full summaries."""
        if not results:
            return

        with open(self.results_file_path, 'w', encoding='utf-8') as f:
            f.write(f"SUMMARIZATION MODEL EVALUATION RESULTS\n")
            f.write(f"Evaluation Date: {self.evaluation_date}\n")
            f.write(f"{'='*80}\n\n")

            for result in results:
                f.write(f"MODEL: {result.get('model_name', 'Unknown')}\n")
                f.write(f"{'-'*60}\n")
                f.write(f"Success: {result.get('success', False)}\n")
                f.write(f"Latency: {result.get('latency_seconds', 0):.2f} seconds\n")
                f.write(f"Input Tokens: {result.get('estimated_input_tokens', 0):,}\n")
                f.write(f"Output Tokens: {result.get('estimated_output_tokens', 0):,}\n")
                f.write(f"Cost: ${result.get('estimated_cost_usd', 0):.4f}\n")

                if result.get('success') and result.get('generated_response'):
                    f.write(f"\nGENERATED RESPONSE:\n")
                    try:
                        response_data = json.loads(result['generated_response'])
                        for key, value in response_data.items():
                            f.write(f"\n🔹 {key}:\n{value}\n")
                    except (json.JSONDecodeError, TypeError):
                        f.write(f"{result.get('generated_response', 'No response')}\n")
                elif result.get('error'):
                    f.write(f"\nERROR: {result.get('error')}\n")

                f.write(f"\n{'='*80}\n\n")

            # Add summary statistics
            successful = [r for r in results if r.get('success')]
            if successful:
                f.write(f"SUMMARY STATISTICS\n")
                f.write(f"{'-'*60}\n")
                f.write(f"Total models tested: {len(results)}\n")
                f.write(f"Successful evaluations: {len(successful)}\n")
                f.write(f"Success rate: {len(successful)/len(results)*100:.1f}%\n\n")

                # Performance ranking
                successful.sort(key=lambda x: x['latency_seconds'])
                f.write(f"PERFORMANCE RANKING (by latency):\n")
                for i, result in enumerate(successful, 1):
                    f.write(f"{i:2d}. {result['model_name']:<20} - {result['latency_seconds']:.2f}s - ${result['estimated_cost_usd']:.4f}\n")

                # Cost ranking
                successful.sort(key=lambda x: x['estimated_cost_usd'])
                f.write(f"\nCOST RANKING (by estimated cost):\n")
                for i, result in enumerate(successful, 1):
                    f.write(f"{i:2d}. {result['model_name']:<20} - ${result['estimated_cost_usd']:.4f} - {result['latency_seconds']:.2f}s\n")


def main():
    """Main entry point for the summarization evaluation script."""
    parser = argparse.ArgumentParser(description='Evaluate different LLM models on summarization tasks')
    parser.add_argument('--models', nargs='+', help='Specific models to evaluate',
                        choices=MODELS_TO_EVALUATE, default=None)
    parser.add_argument('--output', type=str, help='Output text file path',
                        default='./tellme/evaluation/summarization_evaluation_results.txt')

    args = parser.parse_args()

    # Verify OpenAI API key is available
    if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY not found in settings.")
        print("Make sure it's set in your .env file or environment variables.")
        sys.exit(1)

    evaluator = SummarizationEvaluator(results_file_path=args.output)

    try:
        results = evaluator.run_evaluation(models=args.models)
        print("\nEvaluation completed successfully!")
        return results

    except KeyboardInterrupt:
        print("\nEvaluation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during evaluation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()