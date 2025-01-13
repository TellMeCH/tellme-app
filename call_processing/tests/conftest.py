import pytest
from unittest.mock import patch, MagicMock, Mock
import uuid
from rest_framework.test import APIClient
from call_miner.models import Organization, User, Agent, Topic, Customer


@pytest.fixture(autouse=True)
def mock_firebase_auth():
    """Mock firebase_admin.auth methods to prevent real Firebase interactions during tests."""
    with patch('firebase_admin.auth.create_user') as mock_create_user, \
            patch('firebase_admin.auth.delete_user') as mock_delete_user:
        # Define a side effect function that generates a unique UID each time create_user is called
        def create_user_side_effect(*args, **kwargs):
            mock_user = Mock()
            mock_user.uid = str(uuid.uuid4())  # Generate a unique UID
            return mock_user

        mock_create_user.side_effect = create_user_side_effect

        # Mock the delete_user method to do nothing
        mock_delete_user.return_value = None

        yield


@pytest.fixture
def api_client():
    """
    Returns a DRF APIClient instance for making requests to the Django app in tests.
    """
    return APIClient()


@pytest.fixture
def mock_gcs_upload_download():
    """
    Mocks out the GCS upload_to_gcs and download_from_gcs functions.
    We'll patch them globally wherever they are imported.
    """
    with (patch("call_processing.views.upload_to_gcs") as mock_upload,
          patch("call_processing.views.download_from_gcs") as mock_download):
        mock_upload.return_value = "gs://mocked_bucket/mocked_blob"
        mock_download.return_value = b"FakeAudioBytes"
        yield mock_upload, mock_download


@pytest.fixture
def mock_cloud_tasks():
    """
    Mocks out the Google Cloud Tasks create_task call.
    """
    with patch("google.cloud.tasks_v2.CloudTasksClient") as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        mock_client_instance.create_task.return_value = {
            "name": "projects/TEST/locations/TEST/queues/TEST/tasks/TEST"
        }
        yield mock_client_instance


@pytest.fixture
def mock_dlp():
    """
    Mocks out the Google Cloud DLP API calls.
    """
    with patch("google.cloud.dlp_v2.DlpServiceClient") as mock_dlp_class:
        mock_dlp_instance = MagicMock()
        mock_dlp_class.return_value = mock_dlp_instance

        # Create a mock response with a redacted value
        mock_response = MagicMock()
        mock_response.item.value = """
            Speaker 0: My name is [PERSON_NAME] and this is outrageous!
            Speaker 1: What? My phone number is [PHONE_NUMBER]
        """
        mock_dlp_instance.deidentify_content.return_value = mock_response

        yield mock_dlp_instance


@pytest.fixture
def mock_deepgram():
    """
    Mocks out the Deepgram transcription calls (DeepgramClient)
    and the PrerecordedOptions class.
    """
    with patch("deepgram.DeepgramClient") as mock_deepgram_client_class:
        # Mock the DeepgramClient instance
        mock_deepgram_instance = MagicMock()
        mock_deepgram_client_class.return_value = mock_deepgram_instance

        # Mock the response from transcribe_file so we get a standard transcript
        mock_response = {
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "paragraphs": {
                                    "transcript": """
                                        Speaker 0: My name is Sefano Giorgio and this is outrageous!
                                        Speaker 1: What? My phone number is +34 634 333 222
                                    """
                                }
                            }
                        ],
                        "detected_language": "en"
                    }
                ]
            },
            "metadata": {
                "duration": 10.0
            }
        }

        listen_mock = MagicMock()
        listen_mock.rest.v("1").transcribe_file.return_value = mock_response
        mock_deepgram_instance.listen = listen_mock

        yield mock_deepgram_instance


@pytest.fixture
def mock_openai():
    """
    Mocks out the OpenAI chat completion call.
    """
    with patch("langfuse.openai.OpenAI") as mock_openai_class:
        mock_openai_instance = MagicMock()
        mock_openai_class.return_value = mock_openai_instance

        # The structure of the response from openai.chat.completions.create
        mock_chat_completion = MagicMock()
        # Mock JSON content from the OpenAI completion
        mock_chat_completion.choices = [
            MagicMock(message=MagicMock(
                content="""{
                "title": "Test Call",
                "summary": "Short summary",
                "sentiment": 0.9, 
                "topics": ["Sales"],
                "agent_speaker_labels": ["Speaker 0:"],
                "customer_speaker_labels": ["Speaker 1:"]
                }"""
            ))
        ]
        # Usage data
        mock_chat_completion.usage = MagicMock(
            prompt_tokens=50,
            completion_tokens=10
        )
        # Return value from create
        mock_openai_instance.chat.completions.create.return_value = mock_chat_completion

        yield mock_openai_instance


@pytest.fixture
def mock_pydub():
    """
    Mocks pydub's AudioSegment.from_file so we can control the length (ms) of the audio.
    This helps us test single vs multiple chunks in the pipeline.
    """
    with patch("call_processing.utils.call_processing.AudioSegment.from_file") as mock_from_file:
        mock_audio_segment = MagicMock()
        mock_audio_segment.__len__.return_value = 600000  # 10 min in ms (2 chunks)
        mock_from_file.return_value = mock_audio_segment
        yield mock_from_file


@pytest.fixture
def setup_db(db):
    """
    Set up test database with some records. Yield them if you need to retrieve them in your tests.
    """
    org = Organization.objects.create(id=1, name="Test Org")
    user = User.objects.create_user('agent', 'agent@example.com', 'password')
    agent = Agent.objects.create(id=123, organization=org, user=user)
    topic = Topic.objects.create(name="Sales", description="Sales topic", organization=org, is_active=True)
    customer = Customer.objects.create(organization=org, external_id='customer_id')
    return org, agent, topic, customer


@pytest.fixture(autouse=True)
def mock_langfuse():
    """
    Mocks out all Langfuse-related functionality:
      - The @observe decorator becomes a no-op
      - langfuse_context becomes a MagicMock
      - Langfuse() constructor becomes a MagicMock
    This prevents any real tracing from happening in your tests.
    """

    def no_op_decorator(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    with patch("call_processing.utils.call_processing.observe", new=no_op_decorator), \
            patch("call_processing.utils.call_processing.langfuse_context", new=MagicMock()), \
            patch("call_processing.utils.call_processing.Langfuse") as mock_lf_class:
        # The Langfuse constructor will return a MagicMock
        mock_lf_instance = MagicMock()
        mock_lf_class.return_value = mock_lf_instance

        mock_prompt = MagicMock()
        mock_prompt.is_fallback = False
        mock_lf_instance.get_prompt.return_value = mock_prompt

        yield mock_lf_instance


@pytest.fixture
def mock_processing_user():
    """
    Mocks the ProcessingKeyAuthentication by patching it to always return a mock user.
    """
    with patch("call_processing.views.ProcessingKeyAuthentication.authenticate") as mock_auth:
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.email = "pipeline@example.com"
        mock_auth.return_value = (mock_user, None)
        yield mock_auth
