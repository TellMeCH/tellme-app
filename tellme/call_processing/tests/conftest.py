import pytest
from unittest.mock import patch, MagicMock, Mock
import uuid
from datetime import datetime, timedelta
from rest_framework.test import APIClient
from tellme.call_miner.models import (
    Organization, User, Agent, Topic, SuggestedTopic, Customer, OrganizationAPIKey, Conversation
)
from tellme.call_processing.utils.llm_configs import ENRICHMENT_PIPELINE


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
def mock_gcs_utils():
    """
    Mocks out the GCS upload_to_gcs and download_from_gcs functions.
    We'll patch them globally wherever they are imported.
    """
    with (patch("tellme.call_processing.utils.gcs_utils.upload_to_gcs") as mock_upload,
          patch("tellme.call_processing.utils.gcs_utils.download_from_gcs") as mock_download,
          patch("tellme.call_processing.utils.gcs_utils.list_files_in_gcs") as mock_list):
        mock_upload.return_value = "gs://mocked_bucket/mocked_blob"
        mock_download.return_value = b"FakeAudioBytes"
        mock_list.return_value = ['/mocked_folder/mocked_blob.wav']
        yield mock_upload, mock_download, mock_list


@pytest.fixture
def mock_cloud_tasks():
    """
    Mocks out the Google Cloud Tasks create_task call.
    """
    with patch("tellme.call_processing.utils.queue_utils.create_processing_task") as mock_create:
        mock_create.return_value = None
        yield mock_create

@pytest.fixture
def mock_summarization_tasks():
    """
    Mocks out the Google Cloud Tasks create_summarization_task call.
    """
    with patch("tellme.call_processing.tests.test_queue.create_summarization_task") as mock_create:
        mock_create.return_value = "test-task-id-12345"
        yield mock_create


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
def mock_groq():
    """
    Mocks out the Groq transcription calls (Groq).
    """
    with patch("groq.Groq") as mock_groq_class:
        mock_groq_instance = MagicMock()
        mock_groq_class.return_value = mock_groq_instance

        # Define a mock response similar to what Groq would return
        mock_groq_response = MagicMock()
        # The mock "segments" array is analogous to the "verbose_json" format from Groq
        mock_groq_response.segments = [
            {"text": "Hello from Groq chunk 1."},
            {"text": "This is second phrase from chunk 1."}
        ]
        # Groq also returns a .language and .duration attribute
        mock_groq_response.language = "en"
        mock_groq_response.duration = 10.0

        # So groq.audio.transcriptions.create(...) will return `mock_groq_response`
        mock_groq_instance.audio.transcriptions.create.return_value = mock_groq_response

        yield mock_groq_instance


@pytest.fixture
def mock_vertexai():
    """
    Mocks out the google.genai.Client used in CallProcessingPipeline.
    Specifically, it mocks the .models.generate_content call.
    """
    with patch("google.genai.Client") as mock_client_cls:
        client = MagicMock()
        mock_client_cls.return_value = client

        enrichment_json = """{
            "title": "Test Call",
            "summary": "Short summary",
            "sentiment": 4,
            "starting_sentiment": 3,
            "ending_sentiment": 5,
            "topics": ["Billing"],
            "suggested_topics": ["Technical Support"],
            "new_topics": [{"name": "Product Inquiry", "description": "Customer asking about product features"}],
            "agent_speaker_labels": ["Speaker 0"],
            "customer_speaker_labels": ["Speaker 1"],
            "revenue_search_query": "men leather jackets",
            "resolved": false
        }"""

        def gen_content_side_effect(*args, **kwargs):
            """
            Signature of the real method is
              generate_content(model, contents, config)
            but callers may mix positional / keyword args – we handle both.
            """
            cfg = kwargs.get("config") or (args[2] if len(args) > 2 else None)
            is_structured = getattr(cfg, "response_mime_type", None) == "application/json"

            text_payload = enrichment_json if is_structured else diarization_text

            resp = MagicMock()
            resp.candidates = [
                MagicMock(
                    content=MagicMock(
                        parts=[MagicMock(text=text_payload)]
                    )
                )
            ]
            resp.usage_metadata = MagicMock(
                prompt_token_count=10,
                candidates_token_count=5,
                total_token_count=15
            )
            return resp

        gen_content_mock = MagicMock(side_effect=gen_content_side_effect)
        client.models.generate_content = gen_content_mock

        yield gen_content_mock


@pytest.fixture
def mock_litellm_setup():
    """
    Mocks out the LiteLLM setup function to prevent actual LiteLLM initialization during tests.
    """
    with patch("tellme.call_processing.utils.litellm_config.setup_litellm") as mock_setup:
        mock_setup.return_value = None
        yield mock_setup


@pytest.fixture
def mock_litellm():
    """
    Mocks LiteLLM completion for BOTH enrichment and diarization.
    Distinguishes between them based on presence of response_format parameter.
    """
    with patch("litellm.completion") as mock_completion:
        def completion_side_effect(*args, **kwargs):
            # Check if this is a structured output call (enrichment) or plain text (diarization)
            # With new fallback format: model is string, fallbacks is list
            # Enrichment has response_format in kwargs, diarization doesn't
            is_structured = "response_format" in kwargs

            metadata = kwargs.get("metadata", {})
            step_name = metadata.get("step_name", "unknown")

            if is_structured:
                # Enrichment response (structured JSON)
                if step_name == "speaker_identification":
                    response_content = """{
                        "agent_speaker_labels": ["Speaker 0"],
                        "customer_speaker_labels": ["Speaker 1"],
                        "customer_info": {
                            "full_name": "John Doe",
                            "address": "",
                            "birth_date": "1990-01-15",
                            "phone_number": "",
                            "postcode": "",
                            "loyalty_number": ""
                        }
                    }"""
                else:
                    response_content = """{
                        "title": "Test Call",
                        "summary": "Short summary",
                        "sentiment": 4,
                        "starting_sentiment": 3,
                        "ending_sentiment": 5,
                        "topics": ["Billing"],
                        "suggested_topics": ["Technical Support"],
                        "new_topics": [{"name": "Product Inquiry", "description": "Customer asking about product features"}],
                        "revenue_search_query": "men leather jackets",
                        "resolved": false
                    }"""
            else:
                # Diarization response (plain text)
                response_content = "Speaker 0: Hello, how can I help you?\nSpeaker 1: I need assistance with my order."

            mock_chat_completion = MagicMock()
            mock_chat_completion.choices = [
                MagicMock(message=MagicMock(content=response_content, refusal=None))
            ]
            mock_chat_completion.usage = MagicMock(
                prompt_tokens=50,
                completion_tokens=10,
                total_tokens=60
            )
            # Return appropriate model based on type
            if is_structured:
                mock_chat_completion.model = "openai/gpt-4o-mini"
            else:
                mock_chat_completion.model = "vertex_ai/gemini-2.0-flash-001"

            return mock_chat_completion

        mock_completion.side_effect = completion_side_effect
        yield mock_completion


@pytest.fixture
def mock_litellm_meta_summarization():
    """
    Mocks out LiteLLM completion for meta summarization (different JSON structure).
    """
    with patch("litellm.completion") as mock_completion:
        mock_chat_completion = MagicMock()
        mock_chat_completion.choices = [
            MagicMock(message=MagicMock(
                content="""{
                    "Reasons for Calling": "• Billing inquiries\\n• Technical support requests",
                    "Stages of the Customer Journey": "Most callers are existing customers seeking post-purchase support.",
                    "Call Resolution Rates": "85% of issues are resolved in the first call.",
                    "Churn Potential": "Low churn risk due to positive sentiment trends.",
                    "Causes for Dissatisfaction": "• Long wait times\\n• Complex billing processes",
                    "Causes for Engagement": "• Helpful agent responses\\n• Quick issue resolution",
                    "Suggested Actions": "• Reduce wait times\\n• Simplify billing processes"
                }""",
                refusal=None
            ))
        ]
        mock_chat_completion.usage = MagicMock(
            prompt_tokens=100,
            completion_tokens=50
        )
        mock_chat_completion.model = "openai/gpt-5-nano"
        mock_completion.return_value = mock_chat_completion
        yield mock_completion


@pytest.fixture
def mock_openai():
    """
    Mocks out the OpenAI chat completion call for components not yet migrated to LiteLLM.
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
                "sentiment": 4,
                "starting_sentiment": 3,
                "ending_sentiment": 5,
                "topics": ["Billing"],
                "suggested_topics": ["Technical Support"],
                "new_topics": [{"name": "Product Inquiry", "description": "Customer asking about product features"}],
                "agent_speaker_labels": ["Speaker 0"],
                "customer_speaker_labels": ["Speaker 1"],
                "revenue_search_query": "men leather jackets",
                "resolved": false
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
    with patch("tellme.call_processing.processors.call_transcriber.AudioSegment.from_file") as mock_from_file:
        mock_audio_segment = MagicMock()
        mock_audio_segment.__len__.return_value = 600000  # 10 min in ms (2 chunks)
        mock_from_file.return_value = mock_audio_segment
        yield mock_from_file


@pytest.fixture
def setup_db(db):
    """
    Set up test database with some records. Yield them if you need to retrieve them in your tests.
    """
    org = Organization.objects.create(id=1, name="Test Org", max_topic_count=10, revenue_search_prefix="teststore.ch/de/", language="de")
    user = User.objects.create_user('agent@example.com', 'password', 'example', 'agent')
    agent = Agent.objects.create(id=123, organization=org, user=user)
    topic = Topic.objects.create(name="Billing", description="Billing issues", organization=org, is_active=True)
    suggested_topic = SuggestedTopic.objects.create(name="Technical Support", description="Tech support calls", organization=org)
    customer = Customer.objects.create(organization=org, external_id='customer_id')
    plain_key = OrganizationAPIKey.create_key(organization=org, name='Test Key')
    conversation = Conversation.objects.create(
        path='path/to/conversation',
        date=datetime.now() - timedelta(days=1),
        duration=123.45,
        title='Test Conversation',
        summary='Test summary',
        transcript=f"""
        <agent>: Hello, {agent.user.first_name} here. How can I assist you today?
        <customer>: Hi, I have an issue with my product. It's acting weird.
        <agent>: Could you describe the problem?
        <customer>: Yes, it keeps making a strange noise and flashing red lights.
        <agent>: That doesn't sound right. Let me look into that for you.
        <customer>: Thank you, it's driving me crazy!
        """ * 4,
        sentiment=4.5,
        starting_sentiment=3.0,
        ending_sentiment=5.0,
        agent=agent,
        customer=customer,
        resolved=False,
        input_tokens=100,
        output_tokens=50
    )
    # Link the topic to the conversation
    conversation.topics.add(topic)
    return org, agent, topic, suggested_topic, customer, plain_key, conversation


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

    with patch("langfuse.decorators.observe", new=no_op_decorator), \
            patch("langfuse.decorators.langfuse_context", new=MagicMock()), \
            patch("langfuse.Langfuse") as mock_lf_class, \
            patch("tellme.call_processing.processors.call_transcriber.Langfuse", mock_lf_class), \
            patch("tellme.call_processing.processors.call_enricher.Langfuse", mock_lf_class):

        # Mock Langfuse instance
        mock_lf_instance = MagicMock()
        mock_lf_class.return_value = mock_lf_instance

        # Mock prompts - always use fallback to ensure hardcoded configs are used
        mock_prompt = MagicMock()
        mock_prompt.is_fallback = True  # Force use of hardcoded configs from llm_configs.py
        mock_prompt.config = {}  # Not used when is_fallback=True
        mock_prompt.prompt = "Mock prompt text"
        mock_prompt.compile = MagicMock(return_value="Compiled mock prompt")

        mock_lf_instance.get_prompt.return_value = mock_prompt

        yield mock_lf_instance


@pytest.fixture
def mock_processing_user():
    """
    Mocks the ProcessingKeyAuthentication by patching it to always return a mock user.
    """
    with patch("tellme.call_processing.views.ProcessingKeyAuthentication.authenticate") as mock_auth:
        mock_user = MagicMock()
        mock_user.is_authenticated = True
        mock_user.email = "pipeline@example.com"
        mock_auth.return_value = (mock_user, None)
        yield mock_auth


@pytest.fixture
def mock_db_handler():
    """
    Mocks the db_handler functions for retrieve_organization_search_prefix, obtain_active_topics,
    obtain_suggested_topics, and retrieve_organization_language.
    """
    with patch("tellme.call_processing.utils.db_handler.retrieve_organization_search_prefix") as mock_prefix, \
        patch("tellme.call_processing.utils.db_handler.obtain_active_topics") as mock_active, \
        patch("tellme.call_processing.utils.db_handler.obtain_suggested_topics") as mock_suggested, \
        patch("tellme.call_processing.utils.db_handler.retrieve_organization_language") as mock_language:

        mock_prefix.return_value = "pkz.ch/de/"
        mock_active.return_value = "Billing: Payment and invoice issues, "
        mock_suggested.return_value = "Technical Support: Hardware troubleshooting, "
        mock_language.return_value = "German"

        yield mock_prefix, mock_active, mock_suggested, mock_language


@pytest.fixture
def mock_call_valuer():
    """
    Mocks out the CallValuer Google Custom Search API and HTML parsing to return consistent test prices.
    """
    with patch("tellme.call_processing.processors.call_valuer.build") as mock_build, \
         patch("tellme.call_processing.processors.call_valuer.requests.get") as mock_get:

        # Mock Google Custom Search API service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock search result
        mock_search_result = {
            'items': [
                {
                    'link': 'https://teststore.ch/de/men-leather-jackets-premium',
                    'title': 'Premium Leather Jackets'
                }
            ]
        }

        mock_cse = MagicMock()
        mock_cse.list.return_value.execute.return_value = mock_search_result
        mock_service.cse.return_value = mock_cse

        # Mock product page response with prices
        mock_product_response = MagicMock()
        mock_product_response.content = """
        <html>
            <body>
                <div class="price">CHF 299.90</div>
                <div class="price">CHF 199.50</div>
                <span>EUR 149.99</span>
                <p>Price: CHF 250.00</p>
            </body>
        </html>
        """.encode('utf-8')
        mock_product_response.raise_for_status.return_value = None
        mock_get.return_value = mock_product_response

        yield mock_build, mock_get
