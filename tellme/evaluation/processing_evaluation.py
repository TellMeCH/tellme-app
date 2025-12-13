import os
import sys
import argparse
import csv
import json
import hashlib
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional
from unittest.mock import patch
from pathlib import Path

# Ensure Django is set up before importing anything that relies on settings
import django
from django.conf import settings

# Setup Django if not already configured
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tellme.settings')
    django.setup()

from google import genai
from google.genai import types, errors
from tellme.call_processing.utils.call_processing import CallProcessingPipeline
from tellme.evaluation.metadata import CONVERSATIONS, TOPICS, SUGGESTED_TOPICS, SEARCH_PREFIX, SEARCH_LANGUAGE


# LLM evaluation prompt and configuration
EVALUATION_PROMPT = """
You are an expert evaluator comparing the outputs of a call processing AI pipeline.
Your task is to compare the actual outputs with expected outputs and provide similarity scores.

For each comparison type, rate the similarity on a scale from 0.0 to 1.0 where:
- 0.0 = Completely different or wrong
- 0.5 = Partially similar, captures some key elements
- 1.0 = Identical or semantically equivalent

Consider the following aspects:
- Summary: Overall content accuracy and completeness
- Title: Appropriateness and descriptiveness
- Transcript: Speaker diarization accuracy and content preservation
- New Topics: Relevance and appropriateness of suggested new topics
- Search Query: Relevance for finding related products/services

Be objective and focus on functional similarity rather than exact word matching.
"""

EVALUATION_CONFIG = {
    'model': 'gemini-2.5-pro',
    'temperature': 0.1,
    'response_format': {
        'json_schema': {
            'schema': {
                'type': 'object',
                'properties': {
                    'summary_similarity': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Similarity score for summary comparison'
                    },
                    'title_similarity': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Similarity score for title comparison'
                    },
                    'transcript_similarity': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Similarity score for transcript comparison'
                    },
                    'new_topics_similarity': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Similarity score for new topics comparison'
                    },
                    'search_query_similarity': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Similarity score for search query comparison'
                    },
                    'overall_quality': {
                        'type': 'number',
                        'minimum': 0.0,
                        'maximum': 1.0,
                        'description': 'Overall quality assessment of the pipeline output'
                    }
                },
                'required': ['summary_similarity', 'title_similarity', 'transcript_similarity', 'new_topics_similarity', 'search_query_similarity', 'overall_quality'],
                'additionalProperties': False
            }
        }
    }
}

REVENUE_THRESHOLD = 0.5

class CallProcessingEvaluator:
    """
    Evaluation framework for CallProcessingPipeline that compares pipeline outputs
    with expected results using test data and LLM-based comparison.
    """

    def __init__(self, results_csv_path: str = "./tellme/evaluation/evaluation_results.csv", verbose: bool = False,
                 audio_file_path: str = None, transcription_method: str = 'groq', enrichment_method: str = 'vertexai'):
        """
        Initialize the evaluator.

        Args:
            results_csv_path: Path to CSV file for storing evaluation results
            verbose: If True, prints detailed side-by-side comparisons of all outputs
            audio_file_path: Path to audio files directory for evaluation
            transcription_method: Transcription method to use in the pipeline
            enrichment_method: Enrichment method to use in the pipeline
        """
        self.results_csv_path = results_csv_path
        self.verbose = verbose
        self.audio_file_path = audio_file_path or str(Path(__file__).parent / "audio")
        self.transcription_method = transcription_method
        self.enrichment_method = enrichment_method
        self.evaluation_date = datetime.now()
        self.pipeline_hash = self._calculate_pipeline_hash()

        # Setup paths for local audio files
        self.audio_base_path = Path(self.audio_file_path)
        self.audio_base_path.mkdir(exist_ok=True)

        # VertexAI Client
        self.vertexai = genai.Client(vertexai=True, project=settings.GOOGLE_CLOUD_PROJECT, location='us-central1')
        self.llm_prompt = EVALUATION_PROMPT
        self.llm_config = EVALUATION_CONFIG


    @staticmethod
    def _calculate_pipeline_hash() -> str:
        """Calculate hash of current call_processing script for version tracking."""
        pipeline_file = Path(__file__).parent.parent / "call_processing" / "utils" / "call_processing.py"
        if pipeline_file.exists():
            with open(pipeline_file, 'r') as f:
                content = f.read()
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        return "unknown"

    def _mock_gcs_download(self, file_path: str) -> bytes:
        """
        Mock for gcs_utils.download_from_gcs that reads from local files.

        Args:
            file_path: Original GCS path (e.g., "pkz_1.wav")

        Returns:
            bytes: File content as bytes
        """
        # Extract filename from path
        filename = os.path.basename(file_path)
        local_path = self.audio_base_path / filename

        # If local file doesn't exist, use the sample recording for testing
        if not local_path.exists():
            raise FileNotFoundError(f"No audio file found for {filename}")

        with open(local_path, 'rb') as f:
            return f.read()

    def _mock_gcs_list_files(self, directory_path: str, match_glob: str = None) -> List[str]:
        """
        Mock for gcs_utils.list_files_in_gcs that returns local file paths.

        Args:
            directory_path: Directory path to search
            match_glob: Glob pattern to match

        Returns:
            List[str]: List of matching file paths
        """
        if directory_path.endswith('.wav'):
            return [directory_path]

        # For directory paths, return all wav files in the audio directory
        audio_files = []
        for file_path in self.audio_base_path.glob("*.wav"):
            audio_files.append(str(file_path.name))

        return audio_files if audio_files else [directory_path]

    @staticmethod
    def _mock_db_obtain_active_topics(organization_id: int) -> str:
        """
        Mock for db_handler.obtain_active_topics that returns topics from metadata.

        Args:
            organization_id: Organization ID

        Returns:
            str: Formatted string of active topics
        """
        topics_string = "\n"
        for topic in TOPICS:
            topics_string += f"\t - {topic['name']}: {topic['description']}\n"
        return topics_string

    @staticmethod
    def _mock_db_obtain_suggested_topics(organization_id: int) -> str:
        """
        Mock for db_handler.obtain_suggested_topics that returns suggested topics from metadata.

        Args:
            organization_id: Organization ID

        Returns:
            str: Formatted string of suggested topics
        """
        suggested_string = "\n"
        for topic in SUGGESTED_TOPICS:
            suggested_string += f"\t - {topic['name']}: {topic['description']}\n"
        return suggested_string

    @staticmethod
    def _mock_retrieve_organization_search_prefix(organization_id: int) -> str:
        """
        Mock for db_handler.retrieve_organization_search_prefix that returns a test search prefix.

        Args:
            organization_id: Organization ID

        Returns:
            str: Test search prefix for revenue queries
        """
        return SEARCH_PREFIX

    @staticmethod
    def _mock_retrieve_organization_language(organization_id: int) -> str:
        """
        Mock for db_handler.retrieve_organization_language that returns the test language.

        Args:
            organization_id: Organization ID

        Returns:
            str: Test search prefix for revenue queries
        """
        return SEARCH_LANGUAGE

    @staticmethod
    def _process_expected_customer_id(expected: Dict[str, Any]) -> Dict[str, Any]:
        raw_id = expected.get('customer_id')
        if raw_id is not None:
            expected['customer_id'] = hashlib.sha256(
                (settings.HASH_KEY + raw_id + settings.HASH_KEY).encode('utf8')
            ).hexdigest()
        return expected

    @staticmethod
    def _compare_basic_metrics(actual: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare basic metrics that don't require LLM evaluation.

        Args:
            actual: Actual pipeline output
            expected: Expected output from metadata

        Returns:
            Dict containing basic comparison results
        """
        results = {}

        # Topic matching
        actual_topics = set(actual.get('topics', []))
        expected_topics = set(expected.get('topics', []))

        results['topics_exact_match'] = actual_topics == expected_topics
        results['topics_precision'] = len(actual_topics & expected_topics) / len(actual_topics) if actual_topics else 0
        results['topics_recall'] = len(actual_topics & expected_topics) / len(expected_topics) if expected_topics else 0

        # Suggested topics matching
        actual_suggested = set(actual.get('suggested_topics', []))
        expected_suggested = set(expected.get('suggested_topics', []))

        results['suggested_topics_exact_match'] = actual_suggested == expected_suggested
        results['suggested_topics_precision'] = len(actual_suggested & expected_suggested) / len(actual_suggested) if actual_suggested else 0
        results['suggested_topics_recall'] = len(actual_suggested & expected_suggested) / len(expected_suggested) if expected_suggested else 0

        # Sentiment comparison (allowing some tolerance)
        actual_sentiment = float(actual.get('sentiment', 0))
        expected_sentiment = float(expected.get('sentiment', 0))
        results['sentiment_exact_match'] = actual_sentiment == expected_sentiment
        results['sentiment_diff'] = abs(actual_sentiment - expected_sentiment)
        results['sentiment_close_match'] = results['sentiment_diff'] <= 1.0  # Within 1 point

        # Starting sentiment comparison
        actual_starting = float(actual.get('starting_sentiment', 0))
        expected_starting = float(expected.get('starting_sentiment', 0))
        results['starting_sentiment_exact_match'] = actual_starting == expected_starting
        results['starting_sentiment_diff'] = abs(actual_starting - expected_starting)
        results['starting_sentiment_close_match'] = results['starting_sentiment_diff'] <= 1.0

        # Ending sentiment comparison
        actual_ending = float(actual.get('ending_sentiment', 0))
        expected_ending = float(expected.get('ending_sentiment', 0))
        results['ending_sentiment_exact_match'] = actual_ending == expected_ending
        results['ending_sentiment_diff'] = abs(actual_ending - expected_ending)
        results['ending_sentiment_close_match'] = results['ending_sentiment_diff'] <= 1.0

        # Customer ID extraction
        results['customer_id_match'] = (actual.get('customer_id') == expected.get('customer_id')) or (expected.get('customer_id') is None)

        # Revenue comparison (if available)
        actual_revenue = actual.get('revenue_at_stake')
        expected_revenue = expected.get('revenue_at_stake')
        if actual_revenue is not None and expected_revenue is not None:
            try:
                actual_rev = float(actual_revenue)
                expected_rev = float(expected_revenue)
                results['revenue_diff'] = abs(actual_rev - expected_rev)
                results['revenue_relative_diff'] = abs(actual_rev - expected_rev) / expected_rev if expected_rev != 0 else 0
                results['revenue_match'] = results['revenue_relative_diff'] < REVENUE_THRESHOLD
            except (ValueError, TypeError):
                results['revenue_match'] = False
                results['revenue_diff'] = None
                results['revenue_relative_diff'] = None
        else:
            results['revenue_match'] = None
            results['revenue_diff'] = None
            results['revenue_relative_diff'] = None

        return results

    def _compare_with_llm(self, actual: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to compare complex outputs like summaries and transcripts.

        Args:
            actual: Actual pipeline output
            expected: Expected output from metadata

        Returns:
            Dict containing LLM comparison results
        """
        # This is a placeholder for LLM-based comparison
        # You would implement actual LLM calls here

        results = {}

        # For now, implement basic string similarity
        actual_summary = actual.get('summary', '')
        expected_summary = expected.get('summary', '')

        # Title comparison
        actual_title = actual.get('title', '').lower()
        expected_title = expected.get('title', '').lower()

        # Similar for transcript comparison
        actual_transcript = actual.get('transcript', '')
        expected_transcript = expected.get('transcript', '')

        # New topic comparison
        actual_new_topics = actual.get('new_topics', [])
        expected_new_topics = expected.get('new_topics', [])

        # Search query comparison
        actual_search_query = actual.get('search_query', '')
        expected_search_query = expected.get('search_query', '')

        # Only perform LLM comparison if configuration is available
        if self.llm_prompt and self.llm_config:
            try:
                generation = self.vertexai.models.generate_content(
                    model=self.llm_config['model'],
                    contents=f"""
                    Here are the compared items:
                    Summary:
                        - Expected: {expected_summary}
                        - Actual: {actual_summary}
                    Title:
                        - Expected: {expected_title}
                        - Actual: {actual_title}
                    Transcript:
                        - Expected: {expected_transcript}
                        - Actual: {actual_transcript}
                    New Topics:
                        - Expected: {expected_new_topics}
                        - Actual: {actual_new_topics}
                    Search Query:
                        - Expected: {expected_search_query}
                        - Actual: {actual_search_query}
                    """,
                    config=types.GenerateContentConfig(
                        system_instruction=self.llm_prompt,
                        temperature=self.llm_config['temperature'],
                        response_mime_type="application/json",
                        response_schema=self.llm_config["response_format"]["json_schema"]["schema"]
                    ),
                )

                llm_response = json.loads(generation.candidates[0].content.parts[0].text)
                results.update(llm_response)

            except Exception as e:
                print(f"LLM comparison failed: {e}")
                # Fallback to basic similarity metrics
                results.update(self._basic_similarity_fallback(actual, expected))
        else:
            # Use basic similarity metrics as fallback
            results.update(self._basic_similarity_fallback(actual, expected))

        return results

    @staticmethod
    def _basic_similarity_fallback(actual: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback similarity calculation when LLM is not available."""
        results = {}

        # Basic string similarity using Jaccard coefficient
        def jaccard_similarity(str1: str, str2: str) -> float:
            if not str1 and not str2:
                return 1.0
            if not str1 or not str2:
                return 0.0
            words1 = set(str1.lower().split())
            words2 = set(str2.lower().split())
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            return intersection / union if union > 0 else 0.0

        results['summary_similarity'] = jaccard_similarity(
            actual.get('summary', ''), expected.get('summary', '')
        )
        results['title_similarity'] = jaccard_similarity(
            actual.get('title', ''), expected.get('title', '')
        )
        results['transcript_similarity'] = jaccard_similarity(
            actual.get('transcript', ''), expected.get('transcript', '')
        )

        # New topics comparison
        actual_new_topics = [t.get('name', '') for t in actual.get('new_topics', [])]
        expected_new_topics = [t.get('name', '') for t in expected.get('new_topics', [])]
        results['new_topics_similarity'] = jaccard_similarity(
            ' '.join(actual_new_topics), ' '.join(expected_new_topics)
        )

        # Search query comparison
        results['search_query_similarity'] = jaccard_similarity(
            actual.get('revenue_search_query', ''), expected.get('revenue_search_query', '')
        )

        # Overall quality as average
        scores = [v for v in results.values() if isinstance(v, float)]
        results['overall_quality'] = sum(scores) / len(scores) if scores else 0.0

        return results
    
    def print_comparison(self, expected_data: Dict[str, Any], actual_data: Dict[str, Any], result: Dict[str, Any]):
        """Print comparison results with optional verbose side-by-side details."""

        def format_text(text: str, max_length: int = 200) -> str:
            """Format text for display, truncating if too long."""
            if not text:
                return "N/A"
            if len(text) <= max_length:
                return text
            return text[:max_length] + "..."

        # Topics comparison
        expected_topics = set(expected_data.get('topics', []))
        actual_topics = set(actual_data.get('topics', []))
        print(f"\nTopics - Expected: {expected_topics}")
        print(f"Topics - Actual:   {actual_topics}")
        if expected_topics == actual_topics:
            print("✓ Topics: EXACT MATCH")
        else:
            print(f"✗ Topics: MISMATCH (Precision: {result.get('topics_precision', 0):.2f}, Recall: {result.get('topics_recall', 0):.2f})")
            if self.verbose:
                missing = expected_topics - actual_topics
                extra = actual_topics - expected_topics
                if missing:
                    print(f"  Missing topics: {missing}")
                if extra:
                    print(f"  Extra topics: {extra}")

        # Sentiment comparison
        expected_sentiment = expected_data.get('sentiment')
        actual_sentiment = actual_data.get('sentiment')
        print(f"\nOverall Sentiment - Expected: {expected_sentiment}, Actual: {actual_sentiment}")
        if result.get('sentiment_exact_match', False):
            print("✓ Overall Sentiment: EXACT MATCH")
        elif result.get('sentiment_close_match', False):
            print(f"~ Overall Sentiment: CLOSE MATCH (diff: {result.get('sentiment_diff', 0):.1f})")
        else:
            print(f"✗ Overall Sentiment: MISMATCH (diff: {result.get('sentiment_diff', 0):.1f})")

        # Starting sentiment comparison
        expected_starting = expected_data.get('starting_sentiment')
        actual_starting = actual_data.get('starting_sentiment')
        print(f"\nStarting Sentiment - Expected: {expected_starting}, Actual: {actual_starting}")
        if result.get('starting_sentiment_exact_match', False):
            print("✓ Starting Sentiment: EXACT MATCH")
        elif result.get('starting_sentiment_close_match', False):
            print(f"~ Starting Sentiment: CLOSE MATCH (diff: {result.get('starting_sentiment_diff', 0):.1f})")
        else:
            print(f"✗ Starting Sentiment: MISMATCH (diff: {result.get('starting_sentiment_diff', 0):.1f})")

        # Ending sentiment comparison
        expected_ending = expected_data.get('ending_sentiment')
        actual_ending = actual_data.get('ending_sentiment')
        print(f"\nEnding Sentiment - Expected: {expected_ending}, Actual: {actual_ending}")
        if result.get('ending_sentiment_exact_match', False):
            print("✓ Ending Sentiment: EXACT MATCH")
        elif result.get('ending_sentiment_close_match', False):
            print(f"~ Ending Sentiment: CLOSE MATCH (diff: {result.get('ending_sentiment_diff', 0):.1f})")
        else:
            print(f"✗ Ending Sentiment: MISMATCH (diff: {result.get('ending_sentiment_diff', 0):.1f})")

        # Suggested topics comparison
        expected_suggested = set(expected_data.get('suggested_topics', []))
        actual_suggested = set(actual_data.get('suggested_topics', []))
        print(f"\nSuggested Topics - Expected: {expected_suggested}")
        print(f"Suggested Topics - Actual:   {actual_suggested}")
        if expected_suggested == actual_suggested:
            print("✓ Suggested Topics: EXACT MATCH")
        else:
            print(f"✗ Suggested Topics: MISMATCH (Precision: {result.get('suggested_topics_precision', 0):.2f}, Recall: {result.get('suggested_topics_recall', 0):.2f})")
            if self.verbose:
                missing = expected_suggested - actual_suggested
                extra = actual_suggested - expected_suggested
                if missing:
                    print(f"  Missing suggested topics: {missing}")
                if extra:
                    print(f"  Extra suggested topics: {extra}")

        # Customer ID comparison
        expected_customer = expected_data.get('customer_id')
        actual_customer = actual_data.get('customer_id')
        print(f"\nCustomer ID - Expected: {expected_customer}, Actual: {actual_customer}")
        if result.get('customer_id_match', False):
            print("✓ Customer ID: MATCH")
        else:
            print("✗ Customer ID: MISMATCH")

        # Revenue comparison
        expected_revenue = expected_data.get('revenue_at_stake')
        actual_revenue = actual_data.get('revenue_at_stake')
        print(f"\nRevenue - Expected: {expected_revenue}, Actual: {actual_revenue}")
        if result.get('revenue_match') is True:
            print("✓ Revenue: EXACT MATCH")
        elif result.get('revenue_match') is False:
            rel_diff = result.get('revenue_relative_diff', 0)
            print(f"✗ Revenue: MISMATCH (Relative diff: {rel_diff:.1%})")
        else:
            print("- Revenue: NOT AVAILABLE")

        # LLM similarity scores if available
        if 'summary_similarity' in result:
            print(f"\nSummary Similarity:     {result.get('summary_similarity', 0):.2f}")
            if self.verbose:
                print(f"  Expected: {format_text(expected_data.get('summary', ''), 300)}")
                print(f"  Actual:   {format_text(actual_data.get('summary', ''), 300)}")

            print(f"\nTitle Similarity:       {result.get('title_similarity', 0):.2f}")
            if self.verbose:
                print(f"  Expected: {format_text(expected_data.get('title', ''))}")
                print(f"  Actual:   {format_text(actual_data.get('title', ''))}")

            print(f"\nTranscript Similarity:  {result.get('transcript_similarity', 0):.2f}")
            if self.verbose:
                expected_transcript = expected_data.get('transcript', '')
                actual_transcript = actual_data.get('transcript', '')
                print(f"  Expected: {format_text(expected_transcript, 500)}")
                print(f"  Actual:   {format_text(actual_transcript, 500)}")

            print(f"\nNew Topics Similarity:  {result.get('new_topics_similarity', 0):.2f}")
            if self.verbose:
                expected_new = expected_data.get('new_topics', [])
                actual_new = actual_data.get('new_topics', [])
                if expected_new:
                    print("  Expected new topics:")
                    for topic in expected_new:
                        print(f"    - {topic.get('name', 'N/A')}: {topic.get('description', 'N/A')}")
                else:
                    print("  Expected new topics: None")

                if actual_new:
                    print("  Actual new topics:")
                    for topic in actual_new:
                        print(f"    - {topic.get('name', 'N/A')}: {topic.get('description', 'N/A')}")
                else:
                    print("  Actual new topics: None")

            print(f"\nSearch Query Similarity: {result.get('search_query_similarity', 0):.2f}")
            if self.verbose:
                expected_query = expected_data.get('revenue_search_query', '')
                actual_query = actual_data.get('revenue_search_query', '')
                print(f"  Expected: {expected_query if expected_query else 'None'}")
                print(f"  Actual:   {actual_query if actual_query else 'None'}")

            print(f"\nOverall Quality:        {result.get('overall_quality', 0):.2f}")

    def run_evaluation(self, conversation_indices: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Run the complete evaluation on specified conversations.

        Args:
            conversation_indices: List of conversation indices to evaluate. If None, evaluates all.

        Returns:
            Dict containing overall evaluation results
        """
        print(f"Starting evaluation at {self.evaluation_date}")
        print(f"Pipeline hash: {self.pipeline_hash}")

        # Select conversations to evaluate
        conversations_to_eval = CONVERSATIONS
        if conversation_indices is not None:
            conversations_to_eval = [CONVERSATIONS[i] for i in conversation_indices if i < len(CONVERSATIONS)]

        evaluation_results = []

        # Mock the external dependencies
        with patch('tellme.call_processing.utils.gcs_utils.download_from_gcs', side_effect=self._mock_gcs_download), \
             patch('tellme.call_processing.utils.gcs_utils.list_files_in_gcs', side_effect=self._mock_gcs_list_files), \
             patch('tellme.call_processing.utils.db_handler.obtain_active_topics', side_effect=self._mock_db_obtain_active_topics), \
             patch('tellme.call_processing.utils.db_handler.obtain_suggested_topics', side_effect=self._mock_db_obtain_suggested_topics), \
             patch('tellme.call_processing.utils.db_handler.retrieve_organization_search_prefix', side_effect=self._mock_retrieve_organization_search_prefix), \
             patch('tellme.call_processing.utils.db_handler.retrieve_organization_language', side_effect=self._mock_retrieve_organization_language):

            pipeline = CallProcessingPipeline()

            for i, conversation in enumerate(conversations_to_eval):
                print(f"Processing conversation {i+1}/{len(conversations_to_eval)}: {conversation['input']['file_name']}")

                try:
                    # Run the pipeline
                    actual_output = pipeline(
                        file_name=conversation['input']['file_name'],
                        organization_id=int(conversation['input']['organization_id']),
                        agent_id=int(conversation['input']['agent_id']),
                        timestamp=datetime.fromisoformat(conversation['input']['timestamp']),
                        transcription_method=self.transcription_method,
                        enrichment_method=self.enrichment_method
                    )

                    # Compare results
                    conversation['output'] = self._process_expected_customer_id(conversation['output'])
                    basic_results = self._compare_basic_metrics(actual_output, conversation['output'])
                    llm_results = self._compare_with_llm(actual_output, conversation['output'])

                    # Compile results for this conversation
                    result = {
                        'conversation_index': i,
                        'file_name': conversation['input']['file_name'],
                        'evaluation_date': self.evaluation_date.isoformat(),
                        'pipeline_hash': self.pipeline_hash,
                        'audio_file_path': self.audio_file_path,
                        'transcription_method': self.transcription_method,
                        'enrichment_method': self.enrichment_method,
                        'success': True,
                        'error': None,
                        **basic_results,
                        **llm_results,
                        'actual_output': json.dumps(actual_output, default=str),
                        'expected_output': json.dumps(conversation['output'], default=str)
                    }

                except Exception as e:
                    print(f"Error processing conversation {i+1}: {str(e)}")
                    result = {
                        'conversation_index': i,
                        'file_name': conversation['input']['file_name'],
                        'evaluation_date': self.evaluation_date.isoformat(),
                        'pipeline_hash': self.pipeline_hash,
                        'audio_file_path': self.audio_file_path,
                        'transcription_method': self.transcription_method,
                        'enrichment_method': self.enrichment_method,
                        'success': False,
                        'error': str(e),
                        'actual_output': None,
                        'expected_output': json.dumps(conversation['output'], default=str)
                    }

                evaluation_results.append(result)

        # Save results to CSV
        self._save_results_to_csv(evaluation_results)

        # Calculate summary statistics
        summary = self._calculate_summary_stats(evaluation_results)

        print(f"Evaluation completed. Results saved to {self.results_csv_path}")
        return {
            'summary': summary,
            'detailed_results': evaluation_results,
            'evaluation_metadata': {
                'date': self.evaluation_date.isoformat(),
                'pipeline_hash': self.pipeline_hash,
                'conversations_evaluated': len(evaluation_results)
            }
        }

    def _save_results_to_csv(self, results: List[Dict[str, Any]]):
        """Save evaluation results to CSV file."""
        if not results:
            return

        # Get all possible field names
        fieldnames = set()
        for result in results:
            fieldnames.update(result.keys())
        fieldnames = sorted(list(fieldnames))

        # Write to CSV
        file_exists = os.path.exists(self.results_csv_path)

        with open(self.results_csv_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header if file is new
            if not file_exists:
                writer.writeheader()

            writer.writerows(results)

    @staticmethod
    def _calculate_summary_stats(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics from evaluation results."""
        if not results:
            return {}

        successful_results = [r for r in results if r.get('success', False)]

        if not successful_results:
            return {
                'total_conversations': len(results),
                'successful_evaluations': 0,
                'success_rate': 0.0
            }

        # Calculate averages for numeric metrics
        summary = {
            'total_conversations': len(results),
            'successful_evaluations': len(successful_results),
            'success_rate': len(successful_results) / len(results),
        }

        # Calculate metric averages
        numeric_metrics = [
            'topics_precision', 'topics_recall',
            'suggested_topics_precision', 'suggested_topics_recall',
            'sentiment_diff', 'starting_sentiment_diff', 'ending_sentiment_diff',
            'revenue_diff', 'revenue_relative_diff',
            'summary_similarity', 'title_similarity', 'transcript_similarity',
            'new_topics_similarity', 'search_query_similarity', 'overall_quality'
        ]

        for metric in numeric_metrics:
            values = [r.get(metric, 0) for r in successful_results if metric in r and r.get(metric) is not None]
            if values:
                summary[f'avg_{metric}'] = sum(values) / len(values)

        # Calculate percentage of exact matches
        boolean_metrics = [
            'topics_exact_match',
            'suggested_topics_exact_match',
            'sentiment_exact_match', 'sentiment_close_match',
            'starting_sentiment_exact_match', 'starting_sentiment_close_match',
            'ending_sentiment_exact_match', 'ending_sentiment_close_match',
            'customer_id_match',
            'revenue_match'
        ]

        for metric in boolean_metrics:
            values = [r.get(metric, False) for r in successful_results if metric in r and r.get(metric) is not None]
            if values:
                summary[f'pct_{metric}'] = sum(values) / len(values) * 100

        return summary


def main():
    """Main entry point for the evaluation script."""

    # Verify required API keys are available
    required_keys = [
        'DEEPGRAM_API_KEY',
        'GROQ_API_KEY',
        'OPENAI_API_KEY',
        'GOOGLE_CLOUD_PROJECT'
    ]

    missing_keys = []
    for key in required_keys:
        if not hasattr(settings, key) or not getattr(settings, key):
            missing_keys.append(key)

    if missing_keys:
        print(f"Warning: Missing required API keys: {', '.join(missing_keys)}")
        print("Some pipeline features may not work correctly.")
        print("Make sure these are set in your .env file or environment variables.")
        print("Continuing with limited functionality...\n")
    else:
        print("Environment setup complete. All required API keys found.\n")

    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description='Evaluate CallProcessingPipeline performance')
        parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed side-by-side comparisons')
        parser.add_argument('--audio-path', type=str, help='Path to audio files directory', default=None)
        parser.add_argument('--transcription-method', type=str, help='Transcription method to use', default='groq')
        parser.add_argument('--enrichment-method', type=str, help='Enrichment method to use', default='vertexai')

        args = parser.parse_args()

        evaluator = CallProcessingEvaluator(
            verbose=args.verbose,
            audio_file_path=args.audio_path,
            transcription_method=args.transcription_method,
            enrichment_method=args.enrichment_method
        )

        if args.verbose:
            print("Running evaluation in VERBOSE mode for all conversations in metadata...\n")
        else:
            print("Running evaluation for all conversations in metadata...\n")
            print("Use --verbose or -v flag for detailed side-by-side comparisons\n")

        print(f"Configuration:")
        print(f"  Audio file path:       {evaluator.audio_file_path}")
        print(f"  Transcription method:  {evaluator.transcription_method}")
        print(f"  Enrichment method:     {evaluator.enrichment_method}")
        print()

        # Run evaluation on all conversations
        results = evaluator.run_evaluation()

        # Print detailed per-conversation results
        print("\n" + "="*80)
        print("PER-CONVERSATION RESULTS")
        print("="*80)

        for result in results['detailed_results']:
            if result['success']:
                expected_data = json.loads(result['expected_output'])
                actual_data = json.loads(result['actual_output'])

                print(f"\nConversation {result['conversation_index']}: {result['file_name']}")
                print(f"Title: {expected_data.get('title', 'N/A')}")

                # Use the unified comparison method
                evaluator.print_comparison(expected_data, actual_data, result)

                print("-" * 80)
            else:
                print(f"\nConversation {result['conversation_index']}: {result['file_name']}")
                print(f"✗ FAILED: {result['error']}")
                print("-" * 80)

        # Print overall summary
        print("\n" + "="*80)
        print("OVERALL SUMMARY")
        print("="*80)

        # Configuration summary
        print("Configuration:")
        print(f"  Audio file path:       {evaluator.audio_file_path}")
        print(f"  Transcription method:  {evaluator.transcription_method}")
        print(f"  Enrichment method:     {evaluator.enrichment_method}")
        print(f"  Pipeline hash:         {evaluator.pipeline_hash}")
        print()

        # Performance metrics in organized groups
        print("Performance Metrics:")

        # General evaluation stats
        general_metrics = ['total_conversations', 'successful_evaluations', 'success_rate']
        for metric in general_metrics:
            if metric in results['summary']:
                value = results['summary'][metric]
                if isinstance(value, float):
                    print(f"  {metric:33}: {value:.3f}")
                else:
                    print(f"  {metric:33}: {value}")

        print("\n  Topics Performance:")
        topic_metrics = ['avg_topics_precision', 'avg_topics_recall', 'pct_topics_exact_match']
        for metric in topic_metrics:
            if metric in results['summary']:
                value = results['summary'][metric]
                print(f"  {metric:33}: {value:.3f}")

        print("\n  Suggested Topics Performance:")
        suggested_metrics = ['avg_suggested_topics_precision', 'avg_suggested_topics_recall', 'pct_suggested_topics_exact_match']
        for metric in suggested_metrics:
            if metric in results['summary']:
                value = results['summary'][metric]
                print(f"  {metric:33}: {value:.3f}")

        print("\n  Sentiment Performance:")
        sentiment_metrics = [
            'avg_sentiment_diff', 'pct_sentiment_exact_match', 'pct_sentiment_close_match',
            'avg_starting_sentiment_diff', 'pct_starting_sentiment_exact_match', 'pct_starting_sentiment_close_match',
            'avg_ending_sentiment_diff', 'pct_ending_sentiment_exact_match', 'pct_ending_sentiment_close_match'
        ]
        for metric in sentiment_metrics:
            if metric in results['summary']:
                value = results['summary'][metric]
                print(f"  {metric:33}: {value:.3f}")

        print("\n  Customer ID Performance:")
        customer_metrics = ['pct_customer_id_match']
        for metric in customer_metrics:
            if metric in results['summary']:
                value = results['summary'][metric]
                print(f"  {metric:33}: {value:.3f}")

        print("\n  Revenue Performance:")
        revenue_metrics = ['avg_revenue_diff', 'avg_revenue_relative_diff', 'pct_revenue_match']
        for metric in revenue_metrics:
            if metric in results['summary']:
                value = results['summary'][metric]
                print(f"  {metric:33}: {value:.3f}")

        print("\n  LLM Similarity Scores:")
        similarity_metrics = ['avg_summary_similarity', 'avg_title_similarity', 'avg_transcript_similarity',
                            'avg_new_topics_similarity', 'avg_search_query_similarity', 'avg_overall_quality']
        for metric in similarity_metrics:
            if metric in results['summary']:
                value = results['summary'][metric]
                print(f"  {metric:33}: {value:.3f}")

        print(f"\nDetailed results saved to: {evaluator.results_csv_path}")
        print("Evaluation completed successfully!")

    except Exception as e:
        print(f"Error running evaluation: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()