import httpx
import json
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
from tellme.call_processing.utils.call_processing import CallProcessingPipeline
from tellme.call_processing.processors import CallTranscriber, CallRedactor, CallEnricher, CallValuer
from tellme.call_processing.utils.llm_configs import ENRICHMENT_PIPELINE


@pytest.mark.django_db
class TestCallProcessingPipeline:
    """
    Test the main orchestration pipeline with simple integration tests.
    """

    @pytest.fixture
    def pipeline(self, mock_pydub, mock_db_handler, mock_deepgram, mock_groq, mock_litellm, mock_langfuse,
                 mock_dlp, mock_gcs_utils, mock_call_valuer, mock_litellm_setup):
        return CallProcessingPipeline()

    def test_define_session_id(self, pipeline):
        """
        Test that session ID generation creates a consistent hash.
        """
        file_metadata = {
            "file_name": "test.wav",
            "organization_id": 1,
            "agent_id": 123,
            "timestamp": datetime(2024, 1, 1, 12, 0, 0)
        }

        session_id = pipeline.define_session_id(file_metadata)
        assert isinstance(session_id, str)
        assert len(session_id) == 64  # SHA-256 hash length

        # Same input should produce same session ID
        session_id2 = pipeline.define_session_id(file_metadata)
        # Note: session IDs will be different due to timestamp inclusion

    def test_pipeline_with_customer_id(self, pipeline):
        """
        Test full pipeline execution when customer_id is provided.
        """
        result = pipeline(
            file_name="test.wav",
            organization_id=1,
            customer_id="CUST123",
            agent_id=123,
            timestamp=datetime(2024, 1, 1, 12, 0, 0)
        )

        # Check essential pipeline outputs
        assert "transcript" in result
        assert "language" in result
        assert "duration" in result
        assert "customer_id" in result
        assert result["customer_id"] == "CUST123"
        assert "title" in result
        assert "summary" in result

    def test_pipeline_without_customer_id(self, pipeline, mock_litellm):
        """
        Test full pipeline execution when customer_id is not provided.
        """
        # Mock LiteLLM to return customer_info for ID generation
        def custom_side_effect(*args, **kwargs):
            # Override the default enrichment side effect to include customer_info
            mock_chat_completion = MagicMock()
            mock_chat_completion.choices = [
                MagicMock(message=MagicMock(content=json.dumps({
                    "agent_speaker_labels": ["Speaker 0"],
                    "customer_speaker_labels": ["Speaker 1"],
                    "topics": ["Billing"],
                    "suggested_topics": ["Technical Support"],
                    "new_topics": [{"name": "Product Inquiry", "description": "Customer asking about product features"}],
                    "customer_info": {
                        "full_name": "John Doe",
                        "birth_date": "1990-01-15",
                        "address": "",
                        "phone_number": "",
                        "postcode": "",
                        "loyalty_number": ""
                    },
                    "summary": "Short summary",
                    "title": "Test Call",
                    "sentiment": 4,
                    "starting_sentiment": 3,
                    "ending_sentiment": 5,
                    "revenue_search_query": "",
                    "resolved": False
                })))
            ]
            mock_chat_completion.usage = MagicMock(prompt_tokens=50, completion_tokens=10)
            # Return model name WITHOUT provider prefix (LiteLLM behavior)
            mock_chat_completion.model = "gpt-4o-mini"
            return mock_chat_completion

        mock_litellm.side_effect = custom_side_effect

        result = pipeline(
            file_name="test.wav",
            organization_id=1,
            agent_id=123,
            timestamp=datetime(2024, 1, 1, 12, 0, 0)
        )

        # Check essential pipeline outputs
        assert "transcript" in result
        assert "language" in result
        assert "duration" in result
        assert "customer_id" in result
        assert len(result["customer_id"]) == 64  # Generated SHA-256 hash
        assert "title" in result
        assert "summary" in result


@pytest.mark.django_db
class TestCallTranscriber:
    """
    Test the CallTranscriber processor module.
    """

    @pytest.fixture
    def transcriber(self, mock_gcs_utils, mock_pydub, mock_db_handler, mock_deepgram, mock_groq, mock_langfuse,
                    mock_litellm, mock_litellm_setup):
        return CallTranscriber()

    def test_cut_into_chunks_single_chunk(self, transcriber, mock_pydub):
        """
        Set the audio length to 300000 ms (5min), which matches CHUNK_SIZE = 5 minutes => exactly 1 chunk.
        """
        # Adjust the mock's length to 5 minutes:
        mock_pydub.return_value.__len__.return_value = 300000
        audio_data = b"fake audio"
        chunks, total_duration = transcriber.cut_into_chunks(audio_data)
        assert len(chunks) == 1
        assert total_duration == 300000

    def test_cut_into_chunks_multiple_chunks(self, transcriber):
        """
        If the audio length is 600000 ms (10min), we should get 2 chunks (chunk_size=5min).
        """
        audio_data = b"fake audio"
        chunks, total_duration = transcriber.cut_into_chunks(audio_data)
        assert len(chunks) == 2
        assert total_duration == 600000


    def test_fallback_transcription_if_deepgram_fails(self, transcriber, mock_deepgram, mock_groq):
        """
        Ensure that if Deepgram fails on any chunk, the transcriber falls back to Groq.
        """
        # Make Deepgram fail on the first chunk call
        def deepgram_failure_side_effect(*args, **kwargs):
            raise httpx.TimeoutException("Simulated Deepgram failure")

        mock_deepgram.listen.rest.v("1").transcribe_file.side_effect = deepgram_failure_side_effect

        # Run the transcriber
        transcript, language, duration = transcriber.transcribe("test_fallback.wav", "deepgram")

        # Deepgram was called at least once, but it failed
        assert mock_deepgram.listen.rest.v("1").transcribe_file.called

        # Groq was called (fallback should have triggered)
        assert mock_groq.audio.transcriptions.create.called
        assert mock_groq.audio.transcriptions.create.call_count > 0

        # Basic checks on the final transcript
        assert transcript
        assert language
        assert duration > 0

    def test_transcription_method_deepgram_used(self, transcriber, mock_deepgram, mock_groq, mock_litellm):
        """
        Ensure Deepgram is used as the primary transcription method when explicitly specified.
        """
        transcript, language, duration = transcriber.transcribe("test.wav", "deepgram")

        assert mock_deepgram.listen.rest.v("1").transcribe_file.called
        assert not mock_groq.audio.transcriptions.create.called
        assert not mock_litellm.called
        assert transcript
        assert language
        assert duration > 0

    def test_transcription_method_groq_used(
        self, transcriber, mock_groq, mock_deepgram, mock_litellm, mock_litellm_setup
    ):
        """
        Ensure Groq is used as the primary transcription method when explicitly specified.
        """
        transcript, language, duration = transcriber.transcribe("test.wav", "groq")

        assert mock_groq.audio.transcriptions.create.called
        assert not mock_deepgram.listen.rest.v("1").transcribe_file.called
        assert mock_litellm.called  # Diarization uses litellm.completion
        assert transcript
        assert language
        assert duration > 0

    def test_transcribe_directory_multiple_files(
        self, transcriber, mock_deepgram, mock_gcs_utils, mock_pydub
    ):
        """
        If a folder path is passed, and multiple `.wav` files exist,
        the transcriber should download and transcribe each of them.
        """
        _, mock_download, mock_list = mock_gcs_utils

        mock_list.return_value = [
            "folder/part1.wav",
            "folder/part2.wav"
        ]

        transcript, language, duration = transcriber.transcribe("folder/", "deepgram")

        assert mock_download.call_count == 2
        assert transcript.strip() != ""
        assert language
        assert duration > 0

    def test_transcription_method_mp3_file(
        self, transcriber, mock_deepgram, mock_groq, mock_gcs_utils, mock_pydub
    ):
        """
        Ensure Deepgram is used as the primary transcription method when explicitly specified.
        """
        transcript, language, duration = transcriber.transcribe("test.mp3", "deepgram")

        assert mock_deepgram.listen.rest.v("1").transcribe_file.called
        assert not mock_groq.audio.transcriptions.create.called
        assert transcript
        assert language
        assert duration > 0

    def test_transcribe_directory_multiple_formats(
        self, transcriber, mock_deepgram, mock_gcs_utils, mock_pydub
    ):
        """
        If a folder path is passed, and multiple files of varied formats exist,
        the transcriber should download and transcribe each of them.
        """
        _, mock_download, mock_list = mock_gcs_utils

        mock_list.return_value = [
            "folder/part1.wav",
            "folder/part2.mp3"
        ]

        transcript, language, duration = transcriber.transcribe("folder/", "deepgram")

        assert mock_download.call_count == 2
        assert transcript.strip() != ""
        assert language
        assert duration > 0

    def test_transcript_cleaning_applied(self, transcriber, mock_deepgram, mock_gcs_utils):
        """
        Test that transcript cleaning is applied to convert common transcription errors.
        Verifies that 'Gucci' is converted to 'Gutschein' and 'Bohnen' to 'Bonus'.
        """
        # Override the mock to return a transcript with words that need cleaning
        def deepgram_with_errors(*args, **kwargs):
            return {
                'results': {
                    'channels': [{
                        'alternatives': [{
                            'paragraphs': {
                                'transcript': "Customer has a Gucci available and earned some Bohnen rewards.\n"
                                             "The GUCCI expires soon. More bohnen coming next month."
                            }
                        }],
                        'detected_language': 'de'
                    }]
                },
                'metadata': {
                    'duration': 30.0
                }
            }

        mock_deepgram.listen.rest.v("1").transcribe_file.return_value = deepgram_with_errors()

        transcript, language, duration = transcriber.transcribe("test.wav", "deepgram")

        # Verify that cleaning was applied (case-insensitive)
        assert "Gutschein" in transcript
        assert "Bonus" in transcript
        assert "Gucci" not in transcript  # Original should be replaced
        assert "Bohnen" not in transcript  # Original should be replaced
        # Verify case-insensitive replacement worked
        assert "GUCCI" not in transcript
        assert "bohnen" not in transcript


@pytest.mark.django_db
class TestCallRedactor:
    """
    Test the CallRedactor processor module.
    """

    @pytest.fixture
    def redacter(self, mock_dlp):
        return CallRedactor()

    def test_redact_transcript_basic(self, redacter, mock_dlp):
        """
        Test basic transcript redaction functionality.
        """
        transcript = "Hello, my name is John Doe and my phone is 555-1234."

        redacted_transcript, customer_id, first_name, last_name, birth_date = redacter.redact_transcript(transcript, extract_customer_id=False)

        assert mock_dlp.deidentify_content.called
        assert redacted_transcript
        assert customer_id is None
        assert first_name is None
        assert last_name is None
        assert birth_date is None

    def test_extract_customer_id_from_redaction(self, redacter, mock_dlp):
        """
        Test customer ID extraction from redacted transcript.
        """
        original_transcript = "Hello, my name is John Doe and I was born on January 15, 1990."

        # Mock DLP to return a redacted transcript with placeholders
        mock_dlp.deidentify_content.return_value.item.value = "Hello, my name is [PERSON_NAME] and I was born on [DATE]."

        redacted_transcript, customer_id, first_name, last_name, birth_date = redacter.redact_transcript(original_transcript, extract_customer_id=True)

        assert mock_dlp.deidentify_content.called
        assert redacted_transcript
        assert customer_id is not None
        assert len(customer_id) == 64  # SHA-256 hash length
        assert first_name == 'John'
        assert last_name == 'Doe'
        assert birth_date == '1990-01-15'


@pytest.mark.django_db
class TestCallEnricher:
    """
    Test the CallEnricher processor module.
    """

    @pytest.fixture
    def enricher(self, mock_db_handler, mock_litellm, mock_langfuse, mock_litellm_setup):
        return CallEnricher()

    def test_enrich_recording_with_customer_id(self, enricher, mock_db_handler):
        """
        Test enrichment process when customer_id is provided (via enrichment).
        """
        # Mock the topic retrieval functions
        _, mock_obtain_active_topics, mock_obtain_suggested_topics, mock_retrieve_organization_language = mock_db_handler
        mock_obtain_active_topics.return_value = "Billing: Payment issues, Support: Technical help, "
        mock_obtain_suggested_topics.return_value = "Warranty: Product warranty claims, "
        mock_retrieve_organization_language.return_value = "German"

        # The mock will automatically return appropriate responses based on step metadata

        transcript = "Agent: Hello. Customer: Hi, I need help."
        redacted_transcript = "Agent: Hello. Customer: Hi, I need help."

        result, input_tokens, output_tokens = enricher.enrich_recording(
            transcript, redacted_transcript, "openai", 1
        )

        # Check that customer_info was processed into customer_id
        assert "customer_id" in result
        assert len(result["customer_id"]) == 64  # SHA-256 hash
        assert "customer_info" not in result  # Should be removed after processing

        # Check other fields
        assert "title" in result
        assert "summary" in result
        assert "sentiment" in result
        assert "topics" in result
        assert isinstance(input_tokens, int)
        assert isinstance(output_tokens, int)

    def test_enrich_recording_structure_compliance(self, enricher, mock_db_handler):
        """
        Test that enrichment response includes all expected fields with correct types.
        """
        _, mock_obtain_active_topics, mock_obtain_suggested_topics, mock_retrieve_organization_language = mock_db_handler
        mock_obtain_active_topics.return_value = "Billing: Payment issues, "
        mock_obtain_suggested_topics.return_value = "Technical Support: Hardware troubleshooting, "
        mock_retrieve_organization_language.return_value = "German"

        transcript = "Agent: Hello. Customer: Hi, I need help."
        redacted_transcript = "Agent: Hello. Customer: Hi, I need help."

        result, input_tokens, output_tokens = enricher.enrich_recording(
            transcript, redacted_transcript, "openai", 1
        )

        # Test all required fields exist
        required_fields = [
            "agent_speaker_labels", "customer_speaker_labels",
            "topics", "suggested_topics", "new_topics",
            "summary", "title", "sentiment", "resolved"
        ]
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

        # Test field types
        assert isinstance(result["agent_speaker_labels"], list)
        assert isinstance(result["customer_speaker_labels"], list)
        assert isinstance(result["topics"], list)
        assert isinstance(result["suggested_topics"], list)
        assert isinstance(result["new_topics"], list)
        assert isinstance(result["summary"], str)
        assert isinstance(result["title"], str)
        assert isinstance(result["sentiment"], (int, float))
        assert isinstance(result["resolved"], bool)

        # Test sentiment range
        assert 1 <= result["sentiment"] <= 5

    def test_enrichment_pipeline_steps(self, enricher, mock_litellm, mock_db_handler):
        """
        Test that enrichment follows the ENRICHMENT_PIPELINE configuration.
        """
        _, mock_obtain_active_topics, mock_obtain_suggested_topics, mock_retrieve_organization_language = mock_db_handler
        mock_obtain_active_topics.return_value = "Billing: Payment issues, "
        mock_obtain_suggested_topics.return_value = "Technical Support: Hardware troubleshooting, "
        mock_retrieve_organization_language.return_value = "German"

        transcript = "Agent: Hello. Customer: Hi, I need help."
        redacted_transcript = "Agent: Hello. Customer: Hi, I need help."

        # The mock will automatically handle pipeline steps based on metadata

        result, input_tokens, output_tokens = enricher.enrich_recording(
            transcript, redacted_transcript, "openai", 1
        )

        # Verify that LiteLLM was called for each step in the pipeline
        expected_steps = len(ENRICHMENT_PIPELINE)
        assert mock_litellm.call_count == expected_steps

        # Verify the enrichment result structure
        assert "title" in result
        assert "summary" in result
        assert "sentiment" in result
        assert "topics" in result

    def test_fallback_enrichment_if_primary_fails(self, enricher, mock_db_handler):
        """
        Test that LiteLLM model preference ordering works correctly for fallbacks.
        """
        _, mock_obtain_active_topics, mock_obtain_suggested_topics, mock_retrieve_organization_language = mock_db_handler
        mock_obtain_active_topics.return_value = "Billing: Payment issues, "
        mock_obtain_suggested_topics.return_value = "Technical Support: Hardware troubleshooting, "
        mock_retrieve_organization_language.return_value = "German"

        models_used = []

        def track_model_side_effect(*args, **kwargs):
            # Check which model is being attempted first
            model_config = kwargs.get("model", [])
            models_used.append(model_config)

            # Return success response
            mock_completion = MagicMock()
            mock_completion.choices = [MagicMock(message=MagicMock(
                content=json.dumps({
                    "title": "Test Call",
                    "summary": "Short summary",
                    "sentiment": 4,
                    "starting_sentiment": 3,
                    "ending_sentiment": 5,
                    "topics": ["Billing"],
                    "suggested_topics": ["Technical Support"],
                    "new_topics": [],
                    "revenue_search_query": "",
                    "resolved": False,
                    "agent_speaker_labels": ["Speaker 0"],
                    "customer_speaker_labels": ["Speaker 1"],
                    "customer_info": {
                        "full_name": "",
                        "address": "",
                        "birth_date": "",
                        "phone_number": "",
                        "postcode": "",
                        "loyalty_number": ""
                    }
                })
            ))]
            mock_completion.usage = MagicMock(prompt_tokens=50, completion_tokens=10)
            mock_completion.model = model_config if model_config else "unknown"
            return mock_completion

        with patch("litellm.completion", side_effect=track_model_side_effect):
            transcript = "Agent: Hello. Customer: Hi, I need help."
            redacted_transcript = "Agent: Hello. Customer: Hi, I need help."

            # Test OpenAI preference
            result, input_tokens, output_tokens = enricher.enrich_recording(
                transcript, redacted_transcript, "openai", 1
            )

            # Verify OpenAI models were attempted first for each step
            openai_first_calls = [model for model in models_used if model.startswith("openai/")]
            assert len(openai_first_calls) == len(ENRICHMENT_PIPELINE), "OpenAI should be first choice for each enrichment step"

            models_used.clear()

            # Test VertexAI preference
            result, input_tokens, output_tokens = enricher.enrich_recording(
                transcript, redacted_transcript, "vertexai", 1
            )

            # Verify VertexAI models were attempted first for each step
            vertexai_first_calls = [model for model in models_used if model.startswith("vertex_ai/")]
            assert len(vertexai_first_calls) == len(ENRICHMENT_PIPELINE), "VertexAI should be first choice for each enrichment step"

            # Verify result structure
            for key in ("title", "summary", "sentiment", "topics"):
                assert key in result

    def test_enrich_recording_extracts_customer_data_from_redaction(self, enricher, mock_litellm, mock_db_handler):
        """
        Test that enrichment properly extracts and processes customer data when customer_info is provided via enrichment.

        This test verifies that the create_customer_id function is called and returns the expected
        customer demographic data (first name, last name, birth date) along with the hashed ID.
        """
        # Mock the topic retrieval functions
        _, mock_obtain_active_topics, mock_obtain_suggested_topics, mock_retrieve_organization_language = mock_db_handler
        mock_obtain_active_topics.return_value = "Billing: Payment issues, Support: Technical help"
        mock_obtain_suggested_topics.return_value = "Warranty: Product warranty claims"
        mock_retrieve_organization_language.return_value = "English"

        # Mock LiteLLM to return customer_info that will be processed
        def custom_side_effect(*args, **kwargs):
            # Detect enrichment step by checking the response_format schema
            step_name = "unknown"
            if "response_format" in kwargs:
                response_format = kwargs.get("response_format", {})
                json_schema = response_format.get("json_schema", {})
                schema = json_schema.get("schema", {})
                properties = schema.get("properties", {})

                # speaker_identification step has agent_speaker_labels and customer_speaker_labels
                if "agent_speaker_labels" in properties and "customer_speaker_labels" in properties:
                    step_name = "speaker_identification"

            mock_chat_completion = MagicMock()
            if step_name == "speaker_identification":
                content = json.dumps({
                    "agent_speaker_labels": ["Agent"],
                    "customer_speaker_labels": ["Customer"],
                    "customer_info": {
                        "full_name": "Jane Smith",
                        "birth_date": "March 22, 1985",
                        "address": "",
                        "phone_number": "",
                        "postcode": "",
                        "loyalty_number": ""
                    }
                })
            else:
                content = json.dumps({
                    "topics": ["Billing"],
                    "suggested_topics": ["Technical Support"],
                    "new_topics": [{"name": "Account Management", "description": "Customer account related inquiries"}],
                    "summary": "Customer called regarding billing inquiry",
                    "title": "Billing Support Call",
                    "sentiment": 4,
                    "starting_sentiment": 3,
                    "ending_sentiment": 5,
                    "revenue_search_query": "",
                    "resolved": True
                })

            mock_chat_completion.choices = [MagicMock(message=MagicMock(content=content, refusal=None))]
            mock_chat_completion.usage = MagicMock(prompt_tokens=50, completion_tokens=10, total_tokens=60)
            # Return model name WITHOUT provider prefix (LiteLLM behavior)
            mock_chat_completion.model = "gpt-4o-mini"
            return mock_chat_completion

        mock_litellm.side_effect = custom_side_effect

        transcript = "Agent: Hello. Customer: Hi, I'm Jane Smith, born March 22, 1985."
        redacted_transcript = "Agent: Hello. Customer: Hi, I'm [PERSON_NAME], born [DATE]."

        result, input_tokens, output_tokens = enricher.enrich_recording(
            transcript, redacted_transcript, "openai", 1
        )

        # Verify that customer_info was processed into individual customer fields
        assert "customer_id" in result
        assert len(result["customer_id"]) == 64  # SHA-256 hash length
        assert "customer_first_name" in result
        assert result["customer_first_name"] == "Jane"
        assert "customer_last_name" in result
        assert result["customer_last_name"] == "Smith"
        assert "customer_birth_date" in result
        assert result["customer_birth_date"] == "1985-03-22"  # Django formatted date

        # Verify that customer_info was removed after processing
        assert "customer_info" not in result

        # Verify other enrichment results
        assert "title" in result
        assert "summary" in result
        assert "sentiment" in result
        assert result["sentiment"] == 4
        assert "resolved" in result
        assert result["resolved"] is True


@pytest.mark.django_db
class TestRevenueCalculation:
    """
    Test the CallValuer revenue calculation functionality.
    """

    @pytest.fixture
    def call_valuer(self, setup_db, mock_call_valuer, mock_db_handler):
        """Create a CallValuer instance with mocked dependencies."""
        return CallValuer()

    def test_call_valuer_with_search_query(self, call_valuer, setup_db, mock_call_valuer):
        """
        Test that CallValuer calculates revenue when a valid search query is provided.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Test with a search query
        revenue, product_url, failure_reason = call_valuer.infer_revenue("men leather jackets", org.id)

        # Check that revenue is calculated
        assert revenue is not None
        assert isinstance(revenue, float)
        assert product_url is not None
        assert isinstance(product_url, str)
        assert product_url == 'https://teststore.ch/de/men-leather-jackets-premium'
        assert failure_reason is None  # Should be None on success

        # With our mock setup, it should calculate the average of prices: (299.90 + 199.50 + 149.99 + 250.00) / 4
        expected_revenue = (299.90 + 199.50 + 149.99 + 250.00) / 4
        assert abs(revenue - expected_revenue) < 1.0  # Allow small floating point differences

        # Verify that the CallValuer used Google Custom Search API and made HTTP request
        mock_build, mock_get = mock_call_valuer
        assert mock_build.called  # Google Custom Search API was initialized
        assert mock_get.called  # HTTP request to product page was made

    def test_call_valuer_with_empty_search_query(self, call_valuer, setup_db):
        """
        Test that CallValuer returns None when no search query is provided.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Test with empty search query
        revenue, product_url, failure_reason = call_valuer.infer_revenue("", org.id)

        # Check that both revenue and product_url are None when no search query
        assert revenue is None
        assert product_url is None
        assert failure_reason == "Missing query"

    def test_call_valuer_with_whitespace_search_query(self, call_valuer, setup_db):
        """
        Test that CallValuer returns None when search query is only whitespace.
        """
        org, agent, topic, suggested_topic, customer, plain_key, conversation = setup_db

        # Test with whitespace-only search query
        revenue, product_url, failure_reason = call_valuer.infer_revenue("   ", org.id)

        # Check that both revenue and product_url are None when search query is whitespace
        assert revenue is None
        assert product_url is None
        assert failure_reason == "Missing query"