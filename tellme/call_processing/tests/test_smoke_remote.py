import os
import re
import json
import time
import pytest
import requests
import logging
import subprocess
import firebase_admin
from firebase_admin import auth
from io import BytesIO
from urllib.parse import urlparse
from google.cloud import storage
from google.cloud import logging_v2, tasks_v2
from django.utils import timezone
from django.conf import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmokeTestLogger")


class TestSmokeTestCloudRunWithLogs:
    """
    A smoke test for the call processing pipeline. Uses Firebase to authenticate as a superuser for setup and teardown,
    and posts a new call using a test organization API key. Then, evaluates whether the processing takes place.
    """
    org_name = "TestOrg-Suite"
    api_key_name = "TestAPIKey-Suite"
    customer_id = "smoke_customer_123"
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}'
    timestamp_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}\+00:00'

    @pytest.fixture
    def firebase_app(self):
        """
        Initialize Firebase Admin once for the entire test session.
        """
        app = firebase_admin.initialize_app()
        yield app
        firebase_admin.delete_app(app)

    def user_id_token(self, user_email: str) -> str:
        """
        Obtain an ID token for an existing superuser in Firebase and Django. To do so, creates a custom token and
        immediately exchanges it for an ID token (requires an Identity Toolkit REST call!).
        """
        user = auth.get_user_by_email(user_email)
        custom_token = auth.create_custom_token(user.uid)

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={self.firebase_api_key}"
        payload = {
            "token": custom_token.decode("utf-8"),
            "returnSecureToken": True
        }
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        id_token = resp.json()["idToken"]

        return id_token

    def delete_surrogate_data(self, org_url: str):
        """
        Delete surrogate data, used for setup and teardown. This surrogate data includes: an Organization, an Agent,
        an OrganizationAPIKey, and a Customer. It takes advantage of cascading deletions with the Organization when
        possible.
        """
        # Detect agents to be deleted. For each of them, delete all conversations
        next_url = f"{self.cloud_run_host}/api/v1/agents/"
        agent_list = []
        while next_url:
            agent_response = requests.get(
                next_url,
                headers=self.superuser_headers
            )
            agent_response = agent_response.json()
            agent_list.extend(agent_response["results"])
            next_url = agent_response.get('next')

        for agent in agent_list:
            if agent['email'] == self.agent_email:
                # Iterate over all related conversations and delete them
                conversation_response = requests.get(
                    f"{agent['url']}conversations/",
                    headers=self.superuser_headers
                )
                conversation_list = conversation_response.json()['results']
                if len(conversation_list) > 0:
                    for conversation in conversation_list:
                        requests.delete(conversation['url'], headers=self.superuser_headers)
                        logger.info(f"Deleted test conversation {conversation['url']}")

                # Then, delete the agent itself (via the employees endpoint, taking advantage of the shared ID)
                requests.delete(
                    agent['url'].replace('agents', 'employees'),
                    headers=self.superuser_headers
                )
                logger.info(f"Deleted test agent {agent['email']}")

        # Finally, delete the test organization
        requests.delete(org_url, headers=self.superuser_headers)
        logger.info(f"Deleted test organization {org_url}")

    def retrieve_logs_with_timeout(self, retrieval_query: str, waiting_query: str, timeout: int) -> list:
        """
        Retrieves logs given a query after waiting on a particular pattern specified by a waiting query.
        The method waits until a maximum timeout is reached.

        Parameters:
            retrieval_query (str): The log filter query to retrieve the set of logs after the wait condition is met.
            waiting_query (str): The log filter query to check for a specific pattern before proceeding retrieving logs.
            timeout (int): The maximum time in seconds to wait for logs matching the waiting query.

        Returns:
            list: A list of logs matching the retrieval query, represented as dictionaries.
        """
        logger.info(f'Retrieving logs with filter: {retrieval_query}')
        wait_time = 0
        while wait_time < timeout:
            entries = [entry.to_api_repr() for entry in self.logging_client.list_entries(filter_=waiting_query)]
            if entries:
                break
            time.sleep(5)
            wait_time += 5

        if wait_time >= timeout:
            raise TimeoutError(f'Could not retrieve logs within {timeout} seconds')
        logs = [entry.to_api_repr() for entry in self.logging_client.list_entries(filter_=retrieval_query, )]
        return logs

    def generate_logs_filter(self, trigger_timestamp):
        return f"""
            resource.type = "cloud_run_revision"
            resource.labels.service_name = "{self.service_name}"
            resource.labels.location = "{settings.REGION}"
            severity >= DEFAULT
            timestamp >= "{trigger_timestamp}"
        """

    @staticmethod
    def parse_gcs_uri(gcs_uri: str):
        parsed = urlparse(gcs_uri)
        bucket_name = parsed.netloc
        blob_name = parsed.path.lstrip('/')
        return bucket_name, blob_name

    def setup_method(self):
        # Address to target for calls
        self.cloud_run_host = os.getenv("CLOUD_RUN_HOST")
        if not self.cloud_run_host:
            raise EnvironmentError("CLOUD_RUN_HOST environment variable not set.")

        # Service Name of Cloud Run deployment
        self.service_name = os.getenv("SERVICE_NAME")
        if not self.service_name:
            raise EnvironmentError("SERVICE_NAME environment variable not set")

        # Firebase API Key
        self.firebase_api_key = settings.FIREBASE_WEB_API_KEY

        # Test User Email - For security
        self.agent_email = os.getenv('TEST_USER_EMAIL')
        if not self.agent_email:
            raise EnvironmentError("TEST_USER_EMAIL environment variable not set")

        # Authorization header for setup and teardown
        superuser_id_token = self.user_id_token(f'app.admin.{settings.TELLME_ENV}@tell-me.ch')
        self.superuser_headers = {
            "Authorization": f"Bearer {superuser_id_token}"
        }

        # Before creating an organization, check for existing organizations with the same name
        next_url = f"{self.cloud_run_host}/api/v1/organizations/"
        org_list = []
        while next_url:
            org_list_resp = requests.get(
                next_url,
                headers=self.superuser_headers
            )
            org_list_resp.raise_for_status()
            org_list_resp = org_list_resp.json()
            org_list.extend(org_list_resp.get('results', []))
            next_url = org_list_resp.get('next')

        for org in org_list:
            if org["name"] == self.org_name:
                logger.info(f"Found existing organization with URL {org["url"]}. Deleting it.")
                self.delete_surrogate_data(org["url"])

        # Create a new Organization
        org_data = {
            "name": self.org_name,
            "max_user_count": 10,
            "max_topic_count": 20,
        }

        # Add Jira ticket configuration if environment variables are available
        ticket_server = os.getenv('TICKET_SERVER')
        ticket_account = os.getenv('TICKET_ACCOUNT')
        ticket_project = os.getenv('TICKET_PROJECT')
        ticket_key = os.getenv('TICKET_KEY')

        if all([ticket_server, ticket_account, ticket_project, ticket_key]):
            org_data.update({
                "ticket_server": ticket_server,
                "ticket_account": ticket_account,
                "ticket_project": ticket_project,
                "ticket_api_key": ticket_key
            })
            logger.info("Jira ticket configuration added to organization")

        resp = requests.post(
            f"{self.cloud_run_host}/api/v1/organizations/",
            json=org_data,
            headers=self.superuser_headers
        )
        resp.raise_for_status()
        org_json = resp.json()

        # Extract the Org ID
        self.org_id = re.search(r"/organizations/([^/]+)/", org_json["url"]).group(1)
        logger.info(f"Created test organization {self.org_id}")

        # Create Organization API Key
        apikey_data = {
            "name": self.api_key_name,
            "organization": self.org_id
        }
        resp = requests.post(
            f"{self.cloud_run_host}/api/v1/api-keys/",
            json=apikey_data,
            headers=self.superuser_headers
        )
        resp.raise_for_status()
        apikey_json = resp.json()
        self.__api_key_plain = apikey_json["plain_key"]
        logger.info(f"Created Org API Key {apikey_json['name']}")

        # Create Agent via the Employees endpoint
        agent_data = {
            "role": "AGENT",
            "organization": self.org_id,
            "is_organization_admin": False,
            "user": {
                "email": self.agent_email,
                "first_name": "John",
                "last_name": "Doe",
                "auth_type": "password"
            }
        }
        resp = requests.post(
            f"{self.cloud_run_host}/api/v1/employees/",
            json=agent_data,
            headers=self.superuser_headers
        )
        resp.raise_for_status()
        employee_json = resp.json()
        self.agent_id = employee_json['id']
        logger.info(f"Created employee (Agent) with Email {employee_json['user']['email']}")

        # Email-Verification of the Agent User
        agent_user = auth.get_user_by_email(employee_json['user']['email'])
        agent_user = auth.update_user(agent_user.uid, email_verified=True)

        # Obtaining the Auth Token for the Agent User
        agent_id_token = self.user_id_token(employee_json['user']['email'])
        self.agent_headers = {
            "Authorization": f"Bearer {agent_id_token}"
        }

        # Prepare the logging client
        self.logging_client = logging_v2.Client()
        self.unique_log_identifier = f"smoke_test_{int(time.time())}"

        # Load sample recordings
        sample_recording_path = os.path.join("tellme/call_processing/tests/resources", "sample_recording.wav")
        with open(sample_recording_path, "rb") as f:
            self.sample_file_wav = BytesIO(f.read())
            self.sample_file_wav.name = "sample_recording.wav"

        sample_recording_path = os.path.join("tellme/call_processing/tests/resources", "sample_recording.mp3")
        with open(sample_recording_path, "rb") as f:
            self.sample_file_mp3 = BytesIO(f.read())
            self.sample_file_mp3.name = "sample_recording.mp3"

    def _get_ephemeral_token(self) -> str:
        """
        Exchange the long-lived Org API Key for a short-lived ephemeral session token.
        Calls GET /processing/v1/start/ through the API Gateway and returns the raw token.
        """
        start_url = f"{self.cloud_run_host}/processing/v1/start/"
        resp = requests.get(
            start_url,
            headers={"X-Tellme-Api-Key": f"X-API-KEY {self.__api_key_plain}"}
        )
        resp.raise_for_status()
        return resp.json()["session_token"]

    def test_smoke_post_with_logs(self, exclude_customer_id=False, sample_file='wav'):
        """
        Trigger the /queue endpoint using an ephemeral session token obtained from /processing/v1/start/.
        """
        session_token = self._get_ephemeral_token()
        queue_url = f"{self.cloud_run_host}/processing/v1/queue/"
        trigger_timestamp = timezone.now().isoformat()

        data = {
            "agent_id": self.agent_id,
            "timestamp": trigger_timestamp
        }
        if not exclude_customer_id:
            data["customer_id"] = self.customer_id

        if sample_file == 'wav':
            files = {"file": (self.sample_file_wav.name, self.sample_file_wav, "audio/wav")}
        elif sample_file == 'mp3':
            files = {"file": (self.sample_file_mp3.name, self.sample_file_mp3, "audio/mp3")}
        else:
            raise NotImplementedError('sample_file must be either wav or mp3')

        response = requests.post(
            queue_url,
            data=data,
            files=files,
            headers={"X-Tellme-Session-Token": f"Bearer {session_token}"}
        )
        assert response.status_code == 202, f"Unexpected status code: {response.status_code}"
        response_data = response.json()
        assert "file_name" in response_data, "File name not found in response."
        self.uploaded_gcs_uri = f"gs://{settings.GOOGLE_CLOUD_PROJECT}_{settings.CALL_PROCESSING_BUCKET}/{response_data["file_name"]}"

        # Retrieve logs for /queue and /process
        log_filter = self.generate_logs_filter(trigger_timestamp)
        waiting_filter = log_filter + '\ntextPayload =~ ".*Summary created/updated for <class \'tellme\.call_miner\.models\.Customer\'>.*"'
        logs = self.retrieve_logs_with_timeout(
            retrieval_query=log_filter,
            waiting_query=waiting_filter,
            timeout=600
        )
        assert logs is not None, "No logs retrieved recording processing"
        text_logs = [log['textPayload'] for log in logs if 'textPayload' in log]

        # Verify produced logs
        expected_patterns = [
            r"^Execution Time: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
            r"^Created: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}\+00:00$",
            rf"^Organization: {self.org_id}$",
            rf"^File: {self.org_id}/{self.customer_id}_{self.agent_id}_{self.timestamp_pattern}\.wav$",
            rf"^Creating task in queue with parent projects/{settings.GOOGLE_CLOUD_PROJECT}/locations/{settings.REGION}/queues/{settings.PROCESSING_QUEUE_NAME}$",
            rf"^Created task in {settings.PROCESSING_QUEUE_NAME}$",
            rf"^Processing file {self.org_id}/{self.customer_id}_{self.agent_id}_{self.timestamp_pattern}.wav, size \d+ bytes\.$",
            rf"^Processed file {self.org_id}/{self.customer_id}_{self.agent_id}_{self.timestamp_pattern}.wav, required \d+ seconds$",
            rf"^Processing summarization for <class 'tellme.call_miner.models.Customer'> \d+$",
            rf"^Summary created/updated for <class 'tellme.call_miner.models.Customer'> \d+",
        ]
        for pattern in expected_patterns:
            assert (
                any(re.match(pattern, line) for line in text_logs),
                f"Could not find expected pattern {pattern} in execution logs"
            )

        # Verify conversation creation with a GET call
        resp = requests.get(
            f"{self.cloud_run_host}/api/v1/conversations/",
            headers=self.agent_headers
        )
        resp.raise_for_status()
        conversations = resp.json()["results"]
        assert len(conversations) == 1, f"Expected 1 conversation, found {len(conversations)}."
        assert conversations[0]['agent_email'] == self.agent_email

        # Check corresponding customer
        self.customer_url = conversations[0]['customer']
        resp = requests.get(self.customer_url, headers=self.superuser_headers)
        resp.raise_for_status()
        customer = resp.json()

        if exclude_customer_id:
            assert len(customer["external_id"]) == 64
        else:
            assert customer['external_id'] == self.customer_id

        # Check customer summary
        resp = requests.get(f"{self.customer_url}summary_data/", headers=self.superuser_headers)
        resp.raise_for_status()
        summary = resp.json()
        assert summary.get('status') == 'ready'
        assert summary.get('summary') is not None

        self.conversation_url = conversations[0]['url']
        logger.info(f"Verified conversation creation: {conversations}")

        # Check Cloud Tasks creation, verifying the payload contains the org_id & agent_id
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(settings.GOOGLE_CLOUD_PROJECT, settings.REGION, settings.PROCESSING_QUEUE_NAME)
        tasks_list = list(client.list_tasks(parent=parent))

        # Iterate over existing task and identify those that are test-related. Check that none remain
        test_tasks = []
        for task in tasks_list:
            if task.http_request.url == f"{self.cloud_run_host}/processing/v1/process/":
                test_tasks.append(task)
        assert len(test_tasks) == 0, f"Expected 0 task in queue, found {len(test_tasks)}."

    def test_smoke_post_with_logs_excluding_customer_id(self):
        """
        Trigger the /queue endpoint using X-API-KEY, without specifying a customer ID in the /queue endpoint
        """

        # Reuse the standard smoke test logic
        self.test_smoke_post_with_logs(exclude_customer_id=True)

    def test_smoke_post_with_logs_mp3_file(self):
        """
        Trigger the /queue endpoint using X-API-KEY, now for the mp3 sample file
        """

        # Reuse the standard smoke test logic
        self.test_smoke_post_with_logs(sample_file='mp3')

    def test_smoke_post_with_logs_groq(self):
        """
        Trigger the /queue endpoint using X-API-KEY, after switching the org's transcription_method to 'groq'.
        Reuses the original smoke test logic.
        """
        # Patch the org to use 'groq' transcription method
        patch_url = f"{self.cloud_run_host}/api/v1/organizations/{self.org_id}/"
        patch_payload = {"transcription_method": "groq"}
        patch_resp = requests.patch(patch_url, json=patch_payload, headers=self.superuser_headers)
        patch_resp.raise_for_status()

        # Reuse the standard smoke test logic
        self.test_smoke_post_with_logs()

    def test_smoke_post_with_logs_enrichment_vertexai(self):
        """
        Trigger the /queue endpoint using X-API-KEY, after switching the org's transcription_method to 'openai' and its
        enrichment method to 'vertexai'.
        Reuses the original smoke test logic.
        """
        # Patch the org to use 'deepgram' as transcription method and 'vertexai' for enrichment
        patch_url = f"{self.cloud_run_host}/api/v1/organizations/{self.org_id}/"
        patch_payload = {"transcription_method": "deepgram", "enrichment_method": "vertexai"}
        patch_resp = requests.patch(patch_url, json=patch_payload, headers=self.superuser_headers)
        patch_resp.raise_for_status()

        # Reuse the standard smoke test logic
        self.test_smoke_post_with_logs()

    def test_smoke_post_with_logs_groq_enrichment_vertexai(self):
        """
        Trigger the /queue endpoint using X-API-KEY, after switching the org's transcription_method to 'groq' and its
        enrichment method to 'openai'.
        Reuses the original smoke test logic.
        """
        # Patch the org to use 'groq' as transcription method and 'vertexai' for enrichment
        patch_url = f"{self.cloud_run_host}/api/v1/organizations/{self.org_id}/"
        patch_payload = {"transcription_method": "groq", "enrichment_method": "vertexai"}
        patch_resp = requests.patch(patch_url, json=patch_payload, headers=self.superuser_headers)
        patch_resp.raise_for_status()

        # Reuse the standard smoke test logic
        self.test_smoke_post_with_logs()

    def test_smoke_ticket_creation_with_logs(self):
        """
        Trigger ticket creation after creating a customer with conversations.
        This test verifies the full ticket creation pipeline including Jira API calls.
        Skipped if Jira configuration is not available in environment variables.
        """
        # Check if Jira configuration is available
        if not all([os.getenv('TICKET_SERVER'), os.getenv('TICKET_ACCOUNT'),
                    os.getenv('TICKET_PROJECT'), os.getenv('TICKET_KEY')]):
            pytest.skip("Jira configuration not available in environment variables")

        # First, create customer with conversations and summary
        self.test_smoke_post_with_logs()

        # Now trigger ticket creation
        trigger_timestamp = timezone.now().isoformat()

        # Get customer URL from the conversation
        ticket_url = f"{self.customer_url}ticket/"

        logger.info(f"Triggering ticket creation at {ticket_url}")

        # Call POST to ticket endpoint to trigger creation (as superuser)
        response = requests.post(ticket_url, headers=self.superuser_headers)
        assert response.status_code in [200, 202], f"Unexpected status code: {response.status_code}"
        response_data = response.json()

        # Response should indicate task was created or ticket already exists
        # POST returns: {task_id, status_code, message}
        # Possible status_codes: 202 (task created), 200 (already exists), 204 (no data)
        assert response_data.get('status_code') in [200, 202], \
            f"Unexpected status_code: {response_data.get('status_code')}, message: {response_data.get('message')}"
        logger.info(f"Ticket creation initiated with status_code: {response_data.get('status_code')}, message: {response_data.get('message')}")

        # Build log queries for ticket creation
        base_filter = self.generate_logs_filter(trigger_timestamp)

        # Wait for ticket creation to complete - look for success log from views.py:339
        waiting_query = base_filter + '\ntextPayload =~ "Ticket created successfully for customer.*"'
        retrieval_query = base_filter + '\ntextPayload =~ ".*[Tt]icket.*|.*Jira.*"'

        # Retrieve logs with 60 second timeout (Jira API + Cloud Task processing)
        logs = self.retrieve_logs_with_timeout(
            retrieval_query=retrieval_query,
            waiting_query=waiting_query,
            timeout=60
        )

        # Extract log messages
        log_messages = []
        for log in logs:
            if 'textPayload' in log:
                log_messages.append(log['textPayload'])
            elif 'jsonPayload' in log and 'message' in log['jsonPayload']:
                log_messages.append(log['jsonPayload']['message'])

        # Verify key log messages exist (exact patterns from call_processing/views.py)
        # Line 314: Processing ticket creation for customer {customer_id}
        assert any('Processing ticket creation for customer' in msg for msg in log_messages), \
            "Expected log for ticket creation initiation not found"

        # Line 339: Ticket created successfully for customer {customer_id}: {ticket_link}
        assert any('Ticket created successfully for customer' in msg for msg in log_messages), \
            "Expected log for successful ticket creation not found"

        # From ticket_utils.py line 73: Successfully created Jira ticket: {ticket_link}
        assert any('Successfully created Jira ticket' in msg for msg in log_messages), \
            "Expected log for successful Jira API call not found"

        # Verify customer now has ticket_link set
        customer_resp = requests.get(self.customer_url, headers=self.superuser_headers)
        customer_resp.raise_for_status()
        customer = customer_resp.json()

        assert customer.get('ticket_link') is not None, "Customer should have ticket_link set"
        assert customer.get('ticket_date') is not None, "Customer should have ticket_date set"
        assert 'atlassian.net' in customer['ticket_link'], "Ticket link should be a Jira URL"

    def test_smoke_audiohook_with_logs(self):
        """
        Trigger the /ws/audiohook/ endpoint using the Audiohook emulator with an ephemeral session token.
        /ws/audiohook/ is routed directly to Cloud Run (bypassing the API Gateway) and authenticated
        via X-Tellme-Session-Token rather than the long-lived Org API Key.
        """
        session_token = self._get_ephemeral_token()
        audiohook_ws_url = f"{self.cloud_run_host.replace('https://', 'wss://')}/ws/audiohook/"
        trigger_timestamp = timezone.now().isoformat()
        emulator_image = "genesys_audiohook_emulator:latest"
        docker_cmd = [
            "docker", "run", "-i", "--rm",
            "-v", f"{os.getcwd()}/tellme/call_processing/tests/resources:/app/data",
            "-e", f"AUDIOHOOK_WS_URL={audiohook_ws_url}",
            "-e", f"WAV_FILE=/app/data/sample_recording.wav",
            "-e", f"SESSION_TOKEN={session_token}",
            "-e", f"AGENT_ID={self.agent_id}",
            emulator_image
        ]

        logger.info(f"Running AudioHook emulator Docker cmd")
        try:
            subprocess.run(
                docker_cmd,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Emulator container failed:\n{e.stdout}\n{e.stderr}")
            pytest.fail("Audiohook Emulator container exited with an error.")

        logger.info("Audiohook emulator has finished streaming audio.")

        # Retrieve logs for /queue and /process
        log_filter = f"""
            resource.type = "cloud_run_revision"
            resource.labels.service_name = "{self.service_name}"
            resource.labels.location = "{settings.REGION}"
            severity >= DEFAULT
            timestamp >= "{trigger_timestamp}"
        """
        waiting_filter = log_filter + '\ntextPayload =~ ".*Processed.*"'
        logs = self.retrieve_logs_with_timeout(
            retrieval_query=log_filter,
            waiting_query=waiting_filter,
            timeout=600
        )
        assert logs is not None, "No logs retrieved recording processing"
        text_logs = [log['textPayload'] for log in logs if 'textPayload' in log]

        # Verify produced logs
        expected_patterns = [
            rf"^Creating task in queue with parent projects/{settings.GOOGLE_CLOUD_PROJECT}/locations/{settings.REGION}/queues/{settings.PROCESSING_QUEUE_NAME}$",
            rf"^Created task in {settings.PROCESSING_QUEUE_NAME}$",
            rf"^Processing file {self.org_id}/{self.uuid_pattern}_{self.agent_id}_{self.timestamp_pattern}\.wav, size \d+ bytes\.$",
            rf"^Processed file {self.org_id}/{self.uuid_pattern}__{self.agent_id}_{self.timestamp_pattern}\.wav, required \d+ seconds$"
        ]
        for pattern in expected_patterns:
            assert (
                any(re.match(pattern, line) for line in text_logs),
                f"Could not find expected pattern {pattern} in execution logs"
            )

        # Verify conversation creation with a GET call
        resp = requests.get(
            f"{self.cloud_run_host}/api/v1/conversations/",
            headers=self.agent_headers
        )
        resp.raise_for_status()
        conversations = resp.json()["results"]
        assert len(conversations) == 1, f"Expected 1 conversation, found {len(conversations)}."
        assert conversations[0]['agent_email'] == self.agent_email
        self.uploaded_gcs_uri = f"gs://{settings.GOOGLE_CLOUD_PROJECT}_{settings.CALL_PROCESSING_BUCKET}/{conversations[0]['path']}"

        # Check corresponding customer
        resp = requests.get(conversations[0]['customer'], headers=self.superuser_headers)
        resp.raise_for_status()
        customer = resp.json()
        assert re.match(self.uuid_pattern, customer['external_id']) is not None

        self.conversation_url = conversations[0]['url']
        logger.info(f"Verified conversation creation: {conversations}")

        # Check Cloud Tasks creation, verifying the payload contains the org_id & agent_id
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(settings.GOOGLE_CLOUD_PROJECT, settings.REGION, settings.PROCESSING_QUEUE_NAME)
        tasks_list = list(client.list_tasks(parent=parent))

        # Iterate over existing task and identify those that are test-related. Check that none remain
        test_tasks = []
        for task in tasks_list:
            if task.http_request.url == f"{self.cloud_run_host}/processing/v1/process/":
                test_tasks.append(task)
        assert len(test_tasks) == 0, f"Expected 0 tasks in queue, found {len(test_tasks)}."

    def teardown_method(self):
        # Delete the GCS blob
        if hasattr(self, "uploaded_gcs_uri"):
            storage_client = storage.Client()
            bucket_name, blob_name = self.parse_gcs_uri(self.uploaded_gcs_uri)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.delete()
            logger.info(f"Deleted GCS blob '{blob_name}' from bucket '{bucket_name}'")

        # List tasks again and delete any whose payload references our org/agent
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(settings.GOOGLE_CLOUD_PROJECT, settings.REGION, settings.PROCESSING_QUEUE_NAME)
        for task in client.list_tasks(parent=parent):
            body = json.loads(task.http_request.body.decode("utf-8"))
            if (body.get("organization_id") == self.org_id) or (body.get("agent_id") == self.agent_id):
                client.delete_task(name=task.name)
                logger.info(f"Deleted test task referencing org/agent: {task.name}")

        self.delete_surrogate_data(f"{self.cloud_run_host}/api/v1/organizations/{self.org_id}/")
