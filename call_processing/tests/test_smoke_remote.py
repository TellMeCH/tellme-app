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
from google.cloud import secretmanager
from google.cloud import logging_v2, tasks_v2
from django.utils import timezone, crypto
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
    agent_name = "testagent-smoke"
    agent_email = "testagent-smoke@example.com"
    customer_id = "smoke_customer_123"

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
        agent_response = requests.get(
            f"{self.cloud_run_host}/api/v1/agents/",
            headers=self.superuser_headers
        )
        agent_list = agent_response.json()["results"]
        for agent in agent_list:
            if agent['username'] == self.agent_name:
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
                logger.info(f"Deleted test agent {agent['username']}")

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
        self.firebase_api_key = os.getenv("FIREBASE_WEB_API_KEY")
        if not self.firebase_api_key:
            client = secretmanager.SecretManagerServiceClient()
            secret_path = f"projects/{settings.GOOGLE_CLOUD_PROJECT}/secrets/firebase_api_key/versions/latest"
            response = client.access_secret_version(name=secret_path)
            self.firebase_api_key = response.payload.data.decode("UTF-8")

        # Authorization header for setup and teardown
        superuser_id_token = self.user_id_token(f'app.admin.{settings.TELLME_ENV}@tell-me.ch')
        self.superuser_headers = {
            "Authorization": f"Bearer {superuser_id_token}"
        }

        # Before creating an organization, check for existing organizations with the same name
        org_list_resp = requests.get(
            f"{self.cloud_run_host}/api/v1/organizations/",
            headers=self.superuser_headers
        )
        org_list_resp.raise_for_status()
        for org in org_list_resp.json().get("results", []):
            if org["name"] == self.org_name:
                logger.info(f"Found existing organization with URL {org["url"]}. Deleting it.")
                self.delete_surrogate_data(org["url"])

        # Create a new Organization
        org_data = {
            "name": self.org_name,
            "max_user_count": 10,
            "max_topic_count": 20,
        }
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
                "username": self.agent_name,
                "email": self.agent_email,
                "password": crypto.get_random_string(20)
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
        logger.info(f"Created employee (Agent) with Username {employee_json['user']['username']}")

        # Prepare the logging client
        self.logging_client = logging_v2.Client()
        self.unique_log_identifier = f"smoke_test_{int(time.time())}"

        # Load sample recording
        sample_recording_path = os.path.join("./data", "sample_recording.wav")
        with open(sample_recording_path, "rb") as f:
            self.sample_file = BytesIO(f.read())
            self.sample_file.name = "sample_recording.wav"

    def test_smoke_post_with_logs(self):
        """
        Trigger the /queue endpoint, using X-API-KEY
        """
        queue_url = f"{self.cloud_run_host}/processing/v1/queue/"
        trigger_timestamp = timezone.now().isoformat()

        data = {
            "customer_id": self.customer_id,
            "agent_id": self.agent_id,
            "timestamp": trigger_timestamp
        }
        files = {"file": (self.sample_file.name, self.sample_file, "audio/wav")}

        response = requests.post(
            queue_url,
            data=data,
            files=files,
            headers={"Authorization": f"X-API-KEY {self.__api_key_plain}"}
        )
        assert response.status_code == 202, f"Unexpected status code: {response.status_code}"
        response_data = response.json()
        assert "gcs_uri" in response_data, "GCS URI not found in response."
        self.uploaded_gcs_uri = response_data["gcs_uri"]

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
            r"^Execution Time: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
            r"^Created: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}\+00:00$",
            rf"^Organization: {self.org_id}$",
            rf"^File: {self.org_id}/{self.customer_id}_{self.agent_id}_\d{{4}}-\d{{2}}-\d{{2}}T\d{{2}}:\d{{2}}:\d{{2}}\.\d{{6}}\+00:00\.wav$",
            rf"^Creating task in queue with parent projects/{settings.GOOGLE_CLOUD_PROJECT}/locations/{settings.REGION}/queues/{settings.CLOUD_TASKS_QUEUE_NAME}$",
            rf"^Created task in {settings.CLOUD_TASKS_QUEUE_NAME}$",
            rf"^Processing file {self.org_id}/{self.customer_id}_{self.agent_id}_\d{{4}}-\d{{2}}-\d{{2}}T\d{{2}}:\d{{2}}:\d{{2}}\.\d{{6}}\+00:00\.wav, size \d+ bytes\.$",
            rf"^Processed file {self.org_id}/{self.customer_id}_{self.agent_id}_\d{{4}}-\d{{2}}-\d{{2}}T\d{{2}}:\d{{2}}:\d{{2}}\.\d{{6}}\+00:00\.wav, required \d+ seconds$"
        ]
        for pattern in expected_patterns:
            assert any(re.match(pattern, line) for line in text_logs), f"Could not find expected pattern {pattern} in execution logs"

        # Verify conversation creation with a GET call
        resp = requests.get(
            f"{self.cloud_run_host}/api/v1/conversations/",
            headers=self.superuser_headers
        )
        resp.raise_for_status()
        conversations = resp.json()["results"]
        assert len(conversations) == 1, f"Expected 1 conversation, found {len(conversations)}."
        assert conversations[0]['agent_name'] == self.agent_name

        # Check corresponding customer
        resp = requests.get(conversations[0]['customer'], headers=self.superuser_headers)
        resp.raise_for_status()
        customer = resp.json()
        assert customer['external_id'] == self.customer_id

        self.conversation_url = conversations[0]['url']
        logger.info(f"Verified conversation creation: {conversations}")

        # Check Cloud Tasks creation, verifying the payload contains the org_id & agent_id
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(settings.GOOGLE_CLOUD_PROJECT, settings.REGION, settings.CLOUD_TASKS_QUEUE_NAME)
        tasks_list = list(client.list_tasks(parent=parent))

        # Iterate over existing task and identify those that are test-related. Check that none remain
        test_tasks = []
        for task in tasks_list:
            if task.http_request.url == f"{self.cloud_run_host}/processing/v1/process/":
                test_tasks.append(task)
        assert len(test_tasks) == 0, f"Expected 1 task in queue, found {len(test_tasks)}."

    def test_smoke_audiohook_with_logs(self):
        """
        Trigger the /process endpoint, this time using the Audiohook emulator
        """
        audiohook_ws_url = f"{self.cloud_run_host.replace('https://', 'wss://')}/ws/audiohook/"
        trigger_timestamp = timezone.now().isoformat()
        emulator_image = "genesys_audiohook_emulator:latest"
        docker_cmd = [
            "docker", "run", "-i", "--rm",
            "-v", f"{os.getcwd()}/data:/app/data",
            "-e", f"AUDIOHOOK_WS_URL={audiohook_ws_url}",
            "-e", f"WAV_FILE=/app/data/sample_recording.wav",
            "-e", f"API_KEY={self.__api_key_plain}",
            emulator_image
        ]

        logger.info(f"Running AudioHook emulator Docker cmd: {docker_cmd}")
        try:
            subprocess.run(docker_cmd, check=True, capture_output=True, text=True, input="\n")
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
            rf"^Creating task in queue with parent projects/{settings.GOOGLE_CLOUD_PROJECT}/locations/{settings.REGION}/queues/{settings.CLOUD_TASKS_QUEUE_NAME}$",
            rf"^Created task in {settings.CLOUD_TASKS_QUEUE_NAME}$",
            rf"^Processing file {self.org_id}/{self.customer_id}_{self.agent_id}_\d{{4}}-\d{{2}}-\d{{2}}T\d{{2}}:\d{{2}}:\d{{2}}\.\d{{6}}\+00:00\.wav, size \d+ bytes\.$",
            rf"^Processed file {self.org_id}/{self.customer_id}_{self.agent_id}_\d{{4}}-\d{{2}}-\d{{2}}T\d{{2}}:\d{{2}}:\d{{2}}\.\d{{6}}\+00:00\.wav, required \d+ seconds$"
        ]
        for pattern in expected_patterns:
            assert any(re.match(pattern, line) for line in text_logs), f"Could not find expected pattern {pattern} in execution logs"

        # Verify conversation creation with a GET call
        resp = requests.get(
            f"{self.cloud_run_host}/api/v1/conversations/",
            headers=self.superuser_headers
        )
        resp.raise_for_status()
        conversations = resp.json()["results"]
        assert len(conversations) == 1, f"Expected 1 conversation, found {len(conversations)}."
        assert conversations[0]['agent_name'] == self.agent_name

        # Check corresponding customer
        resp = requests.get(conversations[0]['customer'], headers=self.superuser_headers)
        resp.raise_for_status()
        customer = resp.json()
        assert customer['external_id'] == self.customer_id

        self.conversation_url = conversations[0]['url']
        logger.info(f"Verified conversation creation: {conversations}")

        # Check Cloud Tasks creation, verifying the payload contains the org_id & agent_id
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(settings.GOOGLE_CLOUD_PROJECT, settings.REGION, settings.CLOUD_TASKS_QUEUE_NAME)
        tasks_list = list(client.list_tasks(parent=parent))

        # Iterate over existing task and identify those that are test-related. Check that none remain
        test_tasks = []
        for task in tasks_list:
            if task.http_request.url == f"{self.cloud_run_host}/processing/v1/process/":
                test_tasks.append(task)
        assert len(test_tasks) == 0, f"Expected 1 task in queue, found {len(test_tasks)}."

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
        parent = client.queue_path(settings.GOOGLE_CLOUD_PROJECT, settings.REGION, settings.CLOUD_TASKS_QUEUE_NAME)
        for task in client.list_tasks(parent=parent):
            body = json.loads(task.http_request.body.decode("utf-8"))
            if (body.get("organization_id") == self.org_id) or (body.get("agent_id") == self.agent_id):
                client.delete_task(name=task.name)
                logger.info(f"Deleted test task referencing org/agent: {task.name}")

        self.delete_surrogate_data(f"{self.cloud_run_host}/api/v1/organizations/{self.org_id}/")
