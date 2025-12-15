import os
import sys
import time
import argparse
import requests
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import concurrent.futures
from dataclasses import dataclass
import json

# Firebase imports
import firebase_admin
from firebase_admin import credentials, auth

# THIS IS A WIP


def get_user_id_token(email: str) -> str:
    """
    Get a Firebase ID token for a user by email.

    Args:
        email: User email address

    Returns:
        Firebase ID token string
    """
    # Get the user by email
    user = auth.get_user_by_email(email)

    # Create a custom token
    custom_token = auth.create_custom_token(user.uid)

    # Exchange custom token for ID token using Firebase Auth REST API
    api_key = os.environ.get('FIREBASE_API_KEY')
    if not api_key:
        raise ValueError("FIREBASE_API_KEY environment variable not set")

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}"
    response = requests.post(url, json={'token': custom_token.decode('utf-8'), 'returnSecureToken': True})

    if response.status_code != 200:
        raise Exception(f"Failed to get ID token: {response.text}")

    return response.json()['idToken']


@dataclass
class TaskQueueMetrics:
    """Metrics collected during task queue evaluation"""
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    total_duration_seconds: float
    avg_task_latency_seconds: float
    min_task_latency_seconds: float
    max_task_latency_seconds: float
    tasks_per_second: float
    min_backoff: str
    max_concurrent_requests: int
    timestamp: str

    def to_dict(self) -> Dict:
        return {
            'total_tasks': self.total_tasks,
            'successful_tasks': self.successful_tasks,
            'failed_tasks': self.failed_tasks,
            'total_duration_seconds': round(self.total_duration_seconds, 2),
            'avg_task_latency_seconds': round(self.avg_task_latency_seconds, 2),
            'min_task_latency_seconds': round(self.min_task_latency_seconds, 2),
            'max_task_latency_seconds': round(self.max_task_latency_seconds, 2),
            'tasks_per_second': round(self.tasks_per_second, 2),
            'min_backoff': self.min_backoff,
            'max_concurrent_requests': self.max_concurrent_requests,
            'timestamp': self.timestamp
        }


class TaskQueueEvaluator:
    """
    Evaluates task queue performance by submitting multiple recording processing tasks
    and measuring end-to-end latency.
    """

    def __init__(self,
                 base_url: str,
                 api_key: str,
                 organization_id: int,
                 agent_id: int,
                 superuser_email: str,
                 num_tasks: int = 200,
                 results_file: str = './tellme/evaluation/task_queue_results.csv'):
        """
        Initialize the task queue evaluator.

        Args:
            base_url: Base URL of the API (e.g., https://staging-api.tell-me.ch)
            api_key: Organization API key for authentication
            organization_id: Organization ID for filtering conversations
            agent_id: Agent ID to use for all queued tasks
            superuser_email: Superuser email for Firebase authentication
            num_tasks: Number of tasks to queue (default: 200)
            results_file: Path to CSV file for storing results
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.organization_id = organization_id
        self.agent_id = agent_id
        self.superuser_email = superuser_email
        self.num_tasks = num_tasks
        self.results_file = results_file

        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            firebase_admin.initialize_app()

        # Get Firebase ID token for superuser
        self.id_token = get_user_id_token(superuser_email)
        self.auth_headers = {
            'Authorization': f'Bearer {self.id_token}'
        }

        # Find the sample recording
        self.sample_recording_path = Path(__file__).parent.parent / 'call_processing' / 'tests' / 'resources' / 'sample_recording.mp3'
        if not self.sample_recording_path.exists():
            raise FileNotFoundError(f"Sample recording not found at {self.sample_recording_path}")

        print(f"Initialized TaskQueueEvaluator:")
        print(f"  Base URL: {self.base_url}")
        print(f"  Organization ID: {self.organization_id}")
        print(f"  Agent ID: {self.agent_id}")
        print(f"  Superuser: {self.superuser_email}")
        print(f"  Number of tasks: {self.num_tasks}")
        print(f"  Sample recording: {self.sample_recording_path}")

    def queue_single_task(self, task_index: int, timestamp: datetime) -> Tuple[bool, float, str]:
        """
        Queue a single recording processing task.

        Args:
            task_index: Index of this task (for tracking)
            timestamp: Timestamp to use for this call

        Returns:
            Tuple of (success, latency_seconds, error_message)
        """
        url = f"{self.base_url}/processing/v1/queue/"
        headers = {
            'X-Tellme-Api-Key': f'X-API-KEY {self.api_key}'
        }

        # Create multipart form data
        # Use unique customer_id based on task_index to avoid conflicts
        data = {
            'customer_id': f'eval_customer_{task_index}',
            'agent_id': str(self.agent_id),
            'timestamp': timestamp.isoformat(),
            'duration': '45.0'  # Approximate duration of sample recording
        }

        start_time = time.time()

        try:
            with open(self.sample_recording_path, 'rb') as f:
                files = {'file': ('sample_recording.mp3', f, 'audio/mpeg')}
                response = requests.post(url, headers=headers, data=data, files=files, timeout=30)

            latency = time.time() - start_time

            if response.status_code == 200 or response.status_code == 201:
                return True, latency, ""
            else:
                return False, latency, f"HTTP {response.status_code}: {response.text}"

        except Exception as e:
            latency = time.time() - start_time
            return False, latency, str(e)

    def queue_tasks_concurrently(self, max_workers: int = 10) -> List[Tuple[bool, float, str]]:
        """
        Queue all tasks concurrently using thread pool.

        Args:
            max_workers: Maximum number of concurrent requests

        Returns:
            List of (success, latency, error_message) tuples
        """
        print(f"\nQueuing {self.num_tasks} tasks with {max_workers} concurrent workers...")

        # Generate timestamps for all tasks
        # Space them out by 1 second to ensure no overlaps for the agent
        base_time = datetime.now()
        timestamps = [base_time + timedelta(seconds=i) for i in range(self.num_tasks)]

        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            futures = [
                executor.submit(self.queue_single_task, i, timestamp)
                for i, timestamp in enumerate(timestamps)
            ]

            # Collect results as they complete
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                success, latency, error = future.result()
                results.append((success, latency, error))

                if (i + 1) % 20 == 0:
                    successful = sum(1 for s, _, _ in results if s)
                    print(f"  Queued {i + 1}/{self.num_tasks} tasks ({successful} successful)")

        return results

    def get_conversation_count_before(self) -> int:
        """Get the count of conversations before queuing tasks using API."""
        url = f"{self.base_url}/api/v1/agents/{self.agent_id}/conversations/"

        try:
            response = requests.get(url, headers=self.auth_headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                # API returns paginated results with 'count' field for total
                return data.get('count', 0)
            else:
                print(f"Warning: Failed to get conversation count: HTTP {response.status_code}")
                return 0

        except Exception as e:
            print(f"Warning: Exception getting conversation count: {e}")
            return 0

    def wait_for_all_tasks_completion(self,
                                     initial_count: int,
                                     expected_count: int,
                                     timeout_seconds: int = 3600,
                                     poll_interval: int = 10) -> Tuple[bool, float]:
        """
        Wait for all tasks to complete by polling the API.

        Args:
            initial_count: Number of conversations before queuing
            expected_count: Expected number of new conversations
            timeout_seconds: Maximum time to wait (default: 1 hour)
            poll_interval: Seconds between polls (default: 10)

        Returns:
            Tuple of (all_completed, total_duration_seconds)
        """
        print(f"\nWaiting for all tasks to complete...")
        print(f"  Initial conversation count: {initial_count}")
        print(f"  Expected new conversations: {expected_count}")

        start_time = time.time()
        last_count = initial_count

        while True:
            elapsed = time.time() - start_time

            if elapsed > timeout_seconds:
                print(f"\n✗ Timeout after {timeout_seconds}s")
                return False, elapsed

            # Get current conversation count via API
            url = f"{self.base_url}/api/v1/agents/{self.agent_id}/conversations/"
            try:
                response = requests.get(url, headers=self.auth_headers, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    current_count = data.get('count', 0)
                else:
                    print(f"  Warning: Failed to get conversation count: HTTP {response.status_code}")
                    time.sleep(poll_interval)
                    continue

            except Exception as e:
                print(f"  Warning: Exception polling API: {e}")
                time.sleep(poll_interval)
                continue

            new_conversations = current_count - initial_count
            progress_pct = (new_conversations / expected_count * 100) if expected_count > 0 else 0

            if current_count != last_count:
                print(f"  [{int(elapsed)}s] Progress: {new_conversations}/{expected_count} "
                      f"({progress_pct:.1f}%) conversations created")
                last_count = current_count

            if new_conversations >= expected_count:
                print(f"\n✓ All tasks completed in {elapsed:.2f}s")
                return True, elapsed

            time.sleep(poll_interval)

    def calculate_metrics(self,
                         queue_results: List[Tuple[bool, float, str]],
                         total_duration: float,
                         min_backoff: str,
                         max_concurrent_requests: int) -> TaskQueueMetrics:
        """
        Calculate evaluation metrics from results.

        Args:
            queue_results: List of (success, latency, error) tuples from queuing
            total_duration: Total time from start to completion
            min_backoff: Cloud Tasks min_backoff setting
            max_concurrent_requests: Cloud Run max_concurrent_requests setting

        Returns:
            TaskQueueMetrics object
        """
        successful = [r for r in queue_results if r[0]]
        failed = [r for r in queue_results if not r[0]]
        latencies = [r[1] for r in queue_results]

        return TaskQueueMetrics(
            total_tasks=len(queue_results),
            successful_tasks=len(successful),
            failed_tasks=len(failed),
            total_duration_seconds=total_duration,
            avg_task_latency_seconds=sum(latencies) / len(latencies) if latencies else 0,
            min_task_latency_seconds=min(latencies) if latencies else 0,
            max_task_latency_seconds=max(latencies) if latencies else 0,
            tasks_per_second=len(successful) / total_duration if total_duration > 0 else 0,
            min_backoff=min_backoff,
            max_concurrent_requests=max_concurrent_requests,
            timestamp=datetime.now().isoformat()
        )

    def save_results(self, metrics: TaskQueueMetrics):
        """
        Save evaluation results to CSV file.

        Args:
            metrics: TaskQueueMetrics object to save
        """
        # Check if file exists to determine if we need to write headers
        file_exists = Path(self.results_file).exists()

        with open(self.results_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=metrics.to_dict().keys())

            if not file_exists:
                writer.writeheader()

            writer.writerow(metrics.to_dict())

        print(f"\n✓ Results saved to: {self.results_file}")

    def print_results(self, metrics: TaskQueueMetrics):
        """Print evaluation results to console."""
        print("\n" + "="*80)
        print("TASK QUEUE EVALUATION RESULTS")
        print("="*80)
        print(f"\nConfiguration:")
        print(f"  Min Backoff:              {metrics.min_backoff}")
        print(f"  Max Concurrent Requests:  {metrics.max_concurrent_requests}")
        print(f"\nTask Queuing:")
        print(f"  Total Tasks:              {metrics.total_tasks}")
        print(f"  Successful:               {metrics.successful_tasks}")
        print(f"  Failed:                   {metrics.failed_tasks}")
        print(f"  Success Rate:             {metrics.successful_tasks/metrics.total_tasks*100:.1f}%")
        print(f"\nProcessing Performance:")
        print(f"  Total Duration:           {metrics.total_duration_seconds:.2f}s")
        print(f"  Throughput:               {metrics.tasks_per_second:.2f} tasks/second")
        print(f"\nQueue Latency:")
        print(f"  Average:                  {metrics.avg_task_latency_seconds:.3f}s")
        print(f"  Min:                      {metrics.min_task_latency_seconds:.3f}s")
        print(f"  Max:                      {metrics.max_task_latency_seconds:.3f}s")
        print(f"\nTimestamp: {metrics.timestamp}")
        print("="*80)

    def run_evaluation(self,
                      min_backoff: str = "20s",
                      max_concurrent_requests: int = 80,
                      cleanup: bool = False) -> TaskQueueMetrics:
        """
        Run the complete task queue evaluation.

        Args:
            min_backoff: Cloud Tasks min_backoff setting (for tracking)
            max_concurrent_requests: Cloud Run max_concurrent_requests setting
            cleanup: If True, delete created conversations after evaluation

        Returns:
            TaskQueueMetrics object
        """
        print(f"\nStarting task queue evaluation at {datetime.now()}")

        # Get initial conversation count
        initial_count = self.get_conversation_count_before()

        # Queue all tasks concurrently
        queue_results = self.queue_tasks_concurrently(max_workers=20)

        successful_queue = sum(1 for r in queue_results if r[0])
        print(f"\n✓ Queued {successful_queue}/{self.num_tasks} tasks successfully")

        if successful_queue == 0:
            print("✗ No tasks were queued successfully. Aborting evaluation.")
            sys.exit(1)

        # Wait for all tasks to complete
        all_completed, total_duration = self.wait_for_all_tasks_completion(
            initial_count=initial_count,
            expected_count=successful_queue,
            timeout_seconds=3600
        )

        if not all_completed:
            print("⚠ Warning: Not all tasks completed within timeout")

        # Calculate metrics
        metrics = self.calculate_metrics(
            queue_results=queue_results,
            total_duration=total_duration,
            min_backoff=min_backoff,
            max_concurrent_requests=max_concurrent_requests
        )

        # Save and print results
        self.save_results(metrics)
        self.print_results(metrics)

        # Optional cleanup
        if cleanup:
            print("\nCleaning up created conversations...")
            print("Note: Cleanup must be done manually via Django admin or database")
            print(f"Filter: customer.external_id starts with 'eval_customer_'")

        return metrics


def main():
    """Main entry point for task queue evaluation."""

    parser = argparse.ArgumentParser(
        description='Evaluate Cloud Tasks queue performance with Cloud Run'
    )
    parser.add_argument('--base-url', type=str, required=True,
                       help='Base URL of the API (e.g., https://staging-api.tell-me.ch)')
    parser.add_argument('--api-key', type=str, required=True,
                       help='Organization API key for authentication')
    parser.add_argument('--organization-id', type=int, required=True,
                       help='Organization ID')
    parser.add_argument('--agent-id', type=int, required=True,
                       help='Agent ID to use for queued tasks')
    parser.add_argument('--superuser-email', type=str, required=True,
                       help='Superuser email for Firebase authentication')
    parser.add_argument('--num-tasks', type=int, default=200,
                       help='Number of tasks to queue (default: 200)')
    parser.add_argument('--min-backoff', type=str, default='20s',
                       help='Cloud Tasks min_backoff setting (for tracking)')
    parser.add_argument('--max-concurrent-requests', type=int, default=80,
                       help='Cloud Run max_concurrent_requests setting')
    parser.add_argument('--cleanup', action='store_true',
                       help='Delete created conversations after evaluation')
    parser.add_argument('--output', type=str,
                       default='./tellme/evaluation/task_queue_results.csv',
                       help='Output CSV file path')

    args = parser.parse_args()

    try:
        evaluator = TaskQueueEvaluator(
            base_url=args.base_url,
            api_key=args.api_key,
            organization_id=args.organization_id,
            agent_id=args.agent_id,
            superuser_email=args.superuser_email,
            num_tasks=args.num_tasks,
            results_file=args.output
        )

        metrics = evaluator.run_evaluation(
            min_backoff=args.min_backoff,
            max_concurrent_requests=args.max_concurrent_requests,
            cleanup=args.cleanup
        )

        print("\nEvaluation completed successfully!")

    except KeyboardInterrupt:
        print("\n\nEvaluation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
