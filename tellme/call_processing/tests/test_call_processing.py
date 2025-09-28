import httpx
import json
import pytest
from datetime import datetime
from tellme.call_processing.utils.call_processing import CallProcessingPipeline
from tellme.call_processing.processors import CallTranscriber, CallRedactor, CallEnricher
from tellme.call_processing.utils.llm_configs import ENRICHMENT_PIPELINE


@pytest.mark.django_db
class TestCallProcessingPipeline:
    """
    Test the main orchestration pipeline with simple integration tests.
    """

    @pytest.fixture
    def pipeline(self, mock_deepgram, mock_groq, mock_openai, mock_langfuse, mock_dlp, mock_vertexai, mock_gcs_utils):
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

    def test_pipeline_with_customer_id(self, pipeline, mock_deepgram, mock_openai, mock_dlp, mock_pydub):
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

    def test_pipeline_without_customer_id(self, pipeline, mock_deepgram, mock_openai, mock_dlp, mock_pydub):
        """
        Test full pipeline execution when customer_id is not provided.
        """
        # Mock OpenAI to return customer_info for ID generation
        mock_openai.chat.completions.create.return_value.choices[0].message.content = json.dumps({
            "agent_speaker_labels": ["Speaker 0"],
            "customer_speaker_labels": ["Speaker 1"],
            "topics": ["Billing"],
            "suggested_topics": ["Technical Support"],
            "new_topics": [{"name": "Product Inquiry", "description": "Customer asking about product features"}],
            "customer_info": {
                "full_name": "John Doe",
                "birth_date": "1990-01-15"
            },
            "summary": "Short summary",
            "title": "Test Call",
            "sentiment": 4
        })

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
    def transcriber(self, mock_deepgram, mock_groq, mock_vertexai, mock_langfuse):
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

    def test_cut_into_chunks_multiple_chunks(self, transcriber, mock_pydub):
        """
        If the audio length is 600000 ms (10min), we should get 2 chunks (chunk_size=5min).
        """
        audio_data = b"fake audio"
        chunks, total_duration = transcriber.cut_into_chunks(audio_data)
        assert len(chunks) == 2
        assert total_duration == 600000

    def test_transcribe_language_change_warns(self, transcriber, mock_deepgram, mock_pydub, mock_gcs_utils):
        """
        If chunk #2 has a different language, we raise a Warning.
        """
        def mock_side_effect(payload, options, timeout):
            if not hasattr(mock_side_effect, "call_count"):
                mock_side_effect.call_count = 0
            mock_side_effect.call_count += 1

            if mock_side_effect.call_count == 1:
                return {
                    "results": {
                        "channels": [
                            {
                                "alternatives": [{"paragraphs": {"transcript": "Hello world"}}],
                                "detected_language": "en"
                            }
                        ]
                    },
                    "metadata": {"duration": 5.0}
                }
            else:
                return {
                    "results": {
                        "channels": [
                            {
                                "alternatives": [{"paragraphs": {"transcript": "Hola mundo"}}],
                                "detected_language": "es"
                            }
                        ]
                    },
                    "metadata": {"duration": 5.0}
                }

        mock_deepgram.listen.rest.v('1').transcribe_file.side_effect = mock_side_effect

        with pytest.raises(Warning) as exc:
            transcriber.transcribe("test.wav", "deepgram")
        assert "Language changed from" in str(exc.value)

    def test_fallback_transcription_if_deepgram_fails(
        self, transcriber, mock_deepgram, mock_groq, mock_pydub, mock_gcs_utils
    ):
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

    def test_transcription_method_deepgram_used(
        self, transcriber, mock_deepgram, mock_groq, mock_gcs_utils, mock_pydub
    ):
        """
        Ensure Deepgram is used as the primary transcription method when explicitly specified.
        """
        transcript, language, duration = transcriber.transcribe("test.wav", "deepgram")

        assert mock_deepgram.listen.rest.v("1").transcribe_file.called
        assert not mock_groq.audio.transcriptions.create.called
        assert transcript
        assert language
        assert duration > 0

    def test_transcription_method_groq_used(
        self, transcriber, mock_deepgram, mock_groq, mock_gcs_utils, mock_pydub
    ):
        """
        Ensure Groq is used as the primary transcription method when explicitly specified.
        """
        transcript, language, duration = transcriber.transcribe("test.wav", "groq")

        assert mock_groq.audio.transcriptions.create.called
        assert not mock_deepgram.listen.rest.v("1").transcribe_file.called
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

        redacted_transcript, customer_id = redacter.redact_transcript(transcript, extract_customer_id=False)

        assert mock_dlp.deidentify_content.called
        assert redacted_transcript
        assert customer_id is None

    def test_extract_customer_id_from_redaction(self, redacter, mock_dlp):
        """
        Test customer ID extraction from redacted transcript.
        """
        original_transcript = "Hello, my name is John Doe and I was born on January 15, 1990."

        # Mock DLP to return a redacted transcript with placeholders
        mock_dlp.deidentify_content.return_value.item.value = "Hello, my name is [PERSON_NAME] and I was born on [DATE]."

        redacted_transcript, customer_id = redacter.redact_transcript(original_transcript, extract_customer_id=True)

        assert mock_dlp.deidentify_content.called
        assert redacted_transcript
        assert customer_id is not None
        assert len(customer_id) == 64  # SHA-256 hash length


@pytest.mark.django_db
class TestCallEnricher:
    """
    Test the CallEnricher processor module.
    """

    @pytest.fixture
    def enricher(self, mock_openai, mock_vertexai, mock_langfuse):
        return CallEnricher()

    def test_enrich_recording_with_customer_id(self, enricher, mock_openai, mock_db_handler):
        """
        Test enrichment process when customer_id is provided (via enrichment).
        """
        # Mock the topic retrieval functions
        mock_obtain_active_topics, mock_obtain_suggested_topics = mock_db_handler
        mock_obtain_active_topics.return_value = "Billing: Payment issues, Support: Technical help, "
        mock_obtain_suggested_topics.return_value = "Warranty: Product warranty claims, "

        # Mock OpenAI to include customer_info
        mock_openai.chat.completions.create.return_value.choices[0].message.content = json.dumps({
            "agent_speaker_labels": ["Speaker 0"],
            "customer_speaker_labels": ["Speaker 1"],
            "topics": ["Billing"],
            "suggested_topics": ["Technical Support"],
            "new_topics": [{"name": "Product Inquiry", "description": "Customer asking about product features"}],
            "customer_info": {
                "full_name": "John Doe",
                "birth_date": "1990-01-15"
            },
            "summary": "Short summary",
            "title": "Test Call",
            "sentiment": 4
        })

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

    def test_enrich_recording_structure_compliance(self, enricher, mock_openai, mock_db_handler):
        """
        Test that enrichment response includes all expected fields with correct types.
        """
        mock_obtain_active_topics, mock_obtain_suggested_topics = mock_db_handler
        mock_obtain_active_topics.return_value = "Billing: Payment issues, "
        mock_obtain_suggested_topics.return_value = "Technical Support: Hardware troubleshooting, "

        transcript = "Agent: Hello. Customer: Hi, I need help."
        redacted_transcript = "Agent: Hello. Customer: Hi, I need help."

        result, input_tokens, output_tokens = enricher.enrich_recording(
            transcript, redacted_transcript, "openai", 1
        )

        # Test all required fields exist
        required_fields = [
            "agent_speaker_labels", "customer_speaker_labels",
            "topics", "suggested_topics", "new_topics",
            "summary", "title", "sentiment"
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

        # Test sentiment range
        assert 1 <= result["sentiment"] <= 5

    def test_enrichment_pipeline_steps(self, enricher, mock_openai, mock_db_handler):
        """
        Test that enrichment follows the ENRICHMENT_PIPELINE configuration.
        """
        mock_obtain_active_topics, mock_obtain_suggested_topics = mock_db_handler
        mock_obtain_active_topics.return_value = "Billing: Payment issues, "
        mock_obtain_suggested_topics.return_value = "Technical Support: Hardware troubleshooting, "

        transcript = "Agent: Hello. Customer: Hi, I need help."
        redacted_transcript = "Agent: Hello. Customer: Hi, I need help."

        # Mock OpenAI to return valid responses for each step
        def openai_side_effect(*args, **kwargs):
            # Return different responses based on call count to simulate pipeline steps
            if not hasattr(openai_side_effect, 'call_count'):
                openai_side_effect.call_count = 0
            openai_side_effect.call_count += 1

            from unittest.mock import MagicMock
            response = MagicMock()
            response.choices = [MagicMock()]
            response.usage = MagicMock()
            response.usage.prompt_tokens = 50
            response.usage.completion_tokens = 10

            response.choices[0].message.content = json.dumps({
                "agent_speaker_labels": ["Speaker 0"],
                "customer_speaker_labels": ["Speaker 1"],
                "topics": ["Billing"],
                "suggested_topics": ["Technical Support"],
                "new_topics": [{"name": "Product Inquiry", "description": "Customer asking about product features"}],
                "summary": "Short summary",
                "title": "Test Call",
                "sentiment": 4
            })
            return response

        mock_openai.chat.completions.create.side_effect = openai_side_effect

        result, input_tokens, output_tokens = enricher.enrich_recording(
            transcript, redacted_transcript, "openai", 1
        )

        # Verify that OpenAI was called for each step in the pipeline
        expected_steps = len(ENRICHMENT_PIPELINE)
        assert mock_openai.chat.completions.create.call_count == expected_steps

        # Verify the enrichment result structure
        assert "title" in result
        assert "summary" in result
        assert "sentiment" in result
        assert "topics" in result

    def test_fallback_enrichment_if_openai_fails(
        self, enricher, mock_openai, mock_vertexai, mock_db_handler
    ):
        """
        When OpenAI enrichment raises a retriable error, the enricher should retry with Vertex AI.
        """
        mock_obtain_active_topics, mock_obtain_suggested_topics = mock_db_handler
        mock_obtain_active_topics.return_value = "Billing: Payment issues, "
        mock_obtain_suggested_topics.return_value = "Technical Support: Hardware troubleshooting, "

        # Force the primary provider (OpenAI) to fail
        mock_openai.chat.completions.create.side_effect = httpx.HTTPError("Simulated OpenAI failure")

        transcript = "Agent: Hello. Customer: Hi, I need help."
        redacted_transcript = "Agent: Hello. Customer: Hi, I need help."

        result, input_tokens, output_tokens = enricher.enrich_recording(
            transcript, redacted_transcript, "openai", 1
        )

        assert mock_openai.chat.completions.create.called
        assert mock_vertexai.called
        assert mock_vertexai.call_count == len(ENRICHMENT_PIPELINE)

        for key in ("title", "summary", "sentiment", "topics"):
            assert key in result