import httpx
import pytest
from tell_me.call_processing.utils.call_processing import CallProcessingPipeline


@pytest.mark.django_db
class TestCallProcessingPipeline:
    @pytest.fixture
    def pipeline(self, mock_deepgram, mock_groq, mock_openai, mock_langfuse, mock_dlp, mock_vertexai, mock_gcs_utils):
        return CallProcessingPipeline()

    def test_cut_into_chunks_single_chunk(self, pipeline, mock_pydub):
        """
        Set the audio length to 300000 ms (5min), which matches CHUNK_SIZE = 5 minutes => exactly 1 chunk.
        """
        # Adjust the mock's length to 5 minutes:
        mock_pydub.return_value.__len__.return_value = 300000
        audio_data = b"fake audio"
        chunks, total_duration = pipeline.cut_into_chunks(audio_data)
        assert len(chunks) == 1
        assert total_duration == 300000

    def test_cut_into_chunks_multiple_chunks(self, pipeline, mock_pydub):
        """
        If the audio length is 600000 ms (10min), we should get 2 chunks (chunk_size=5min).
        """
        audio_data = b"fake audio"
        chunks, total_duration = pipeline.cut_into_chunks(audio_data)
        assert len(chunks) == 2
        assert total_duration == 600000

    def test_transcribe_empty_audio_raises(self, pipeline, mock_deepgram, mock_pydub, mock_langfuse, mock_dlp):
        """
        If the pipeline ends up with no transcript text, it should raise ValueError.
        """
        # Force deepgram mock to return empty paragraphs
        mock_deepgram.listen.rest.v("1").transcribe_file.return_value = {
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "paragraphs": {"transcript": ""}
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
        with pytest.raises(RuntimeError) as exc:
            pipeline(
                file_name="test.wav",
                organization_id=1,
                customer_id="CUST123",
                agent_id=123,
                timestamp="2024-01-01T12:00:00"
            )
        assert "Produced transcript is empty" in str(exc.value)

    def test_transcribe_language_change_warns(self, pipeline, mock_deepgram, mock_pydub, mock_langfuse):
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
            pipeline(
                file_name="test.wav",
                organization_id=1,
                customer_id="CUST123",
                agent_id=123,
                timestamp="2024-01-01T12:00:00"
            )
        assert "Language changed suddenly from" in str(exc.value)

    def test_enrich_recording_structure(self, pipeline, mock_openai, mock_deepgram, mock_pydub, mock_langfuse):
        """
        If the transcript is not empty, we confirm we get back an enriched payload
        with the fields we expect (title, summary, topics, sentiment, etc.).
        """
        result = pipeline(
                file_name="test.wav",
                organization_id=1,
                customer_id="CUST123",
                agent_id=123,
                timestamp="2024-01-01T12:00:00"
        )
        assert "title" in result
        assert "summary" in result
        assert "sentiment" in result
        assert "topics" in result
        assert "transcript" in result
        assert "<agent>:" in result["transcript"] or "<customer>:" in result["transcript"]

    def test_fallback_transcription_if_deepgram_fails(
        self, pipeline, mock_deepgram, mock_groq, mock_openai, mock_langfuse, mock_pydub, mock_dlp, mock_vertexai
    ):
        """
        Ensure that if Deepgram fails on any chunk, the pipeline falls back to Groq
        for ALL chunks, and then applies diarization via OpenAI.
        """

        # Make Deepgram fail on the first chunk call
        def deepgram_failure_side_effect(*args, **kwargs):
            raise httpx.TimeoutException("Simulated Deepgram failure")

        mock_deepgram.listen.rest.v("1").transcribe_file.side_effect = deepgram_failure_side_effect

        # Run the pipeline
        result = pipeline(
            file_name="test_fallback.wav",
            organization_id=1,
            customer_id="CUST123",
            agent_id=123,
            timestamp="2024-01-01T12:00:00"
        )

        # Deepgram was called at least once, but it failed
        assert mock_deepgram.listen.rest.v("1").transcribe_file.called

        # Groq was called (fallback should have triggered)
        assert mock_groq.audio.transcriptions.create.called
        assert mock_groq.audio.transcriptions.create.call_count > 0

        # We expect 2 calls total: 1 for diarization, 1 for enrichment.
        assert mock_openai.chat.completions.create.call_count == 1
        assert mock_vertexai.call_count == 1

        # Basic checks on the final enriched data
        assert "title" in result
        assert "summary" in result
        assert "agent_speaker_labels" in result
        assert "customer_speaker_labels" in result
        assert result["transcript"]

    def test_fallback_fails_groq_raises(
            self, pipeline, mock_deepgram, mock_groq, mock_openai, mock_langfuse, mock_pydub, mock_dlp
    ):
        """
        If Deepgram fails and we attempt to use Groq but Groq also fails,
        we expect the pipeline to raise an exception.
        """
        # Simulate Deepgram and Groq always failing
        mock_deepgram.listen.rest.v("1").transcribe_file.side_effect = ValueError("Deepgram fail")
        mock_groq.audio.transcriptions.create.side_effect = Exception("Groq meltdown")

        with pytest.raises(Exception) as exc:
            pipeline(
                file_name="test_fallback2.wav",
                organization_id=1,
                customer_id="CUST123",
                agent_id=123,
                timestamp="2024-01-01T12:00:00"
            )

        assert "Could not proceed with fallback transcription method" in str(exc.value)

    def test_transcribe_directory_multiple_blobs(
        self, pipeline, mock_deepgram, mock_gcs_utils, mock_pydub
    ):
        """
        If a folder path is passed, and multiple `.wav` files exist,
        the pipeline should download and transcribe each of them.
        """
        _, mock_download, mock_list = mock_gcs_utils

        mock_list.return_value = [
            "folder/part1.wav",
            "folder/part2.wav"
        ]

        result = pipeline(
            file_name="folder/",
            organization_id=1,
            customer_id="C123",
            agent_id=123,
            timestamp="2024-01-01T12:00:00"
        )

        assert mock_download.call_count == 2
        assert "transcript" in result
        assert result["transcript"].strip() != ""

    def test_transcribe_directory_empty_folder(
        self, pipeline, mock_deepgram, mock_gcs_utils, mock_pydub
    ):
        """
        If list_files_in_gcs returns an empty list (no `.wav` files),
        the pipeline should raise a ValueError due to no transcript.
        """
        _, _, mock_list = mock_gcs_utils
        mock_list.return_value = []

        with pytest.raises(RuntimeError) as exc:
            pipeline(
                file_name="empty_folder/",
                organization_id=1,
                customer_id="C123",
                agent_id=123,
                timestamp="2024-01-01T12:00:00"
            )
        assert "Produced transcript is empty" in str(exc.value)

    def test_transcribe_directory_fallback_partial_failure(
        self, pipeline, mock_deepgram, mock_groq, mock_gcs_utils, mock_pydub, mock_openai, mock_vertexai, mock_dlp
    ):
        """
        If Deepgram fails on the first file but not the second,
        the pipeline should fallback to Groq and complete transcription.
        """
        _, mock_download, mock_list = mock_gcs_utils
        mock_list.return_value = ["folder/part1.wav", "folder/part2.wav"]

        def deepgram_side_effect(*args, **kwargs):
            if deepgram_side_effect.call_count == 0:
                deepgram_side_effect.call_count += 1
                raise httpx.TimeoutException("Simulated Deepgram failure")
            return {
                "results": {
                    "channels": [
                        {
                            "alternatives": [{"paragraphs": {"transcript": "Second chunk text"}}],
                            "detected_language": "en"
                        }
                    ]
                },
                "metadata": {"duration": 5.0}
            }

        deepgram_side_effect.call_count = 0
        mock_deepgram.listen.rest.v("1").transcribe_file.side_effect = deepgram_side_effect

        result = pipeline(
            file_name="folder/",
            organization_id=1,
            customer_id="C123",
            agent_id=123,
            timestamp="2024-01-01T12:00:00"
        )

        assert mock_groq.audio.transcriptions.create.called
        assert "transcript" in result
        assert result["transcript"].strip() != ""

    def test_transcription_method_deepgram_used(
        self, pipeline, mock_deepgram, mock_groq, mock_openai, mock_langfuse, mock_dlp, mock_vertexai, mock_pydub
    ):
        """
        Ensure Deepgram is used as the primary transcription method when explicitly specified.
        """
        result = pipeline(
            file_name="test.wav",
            organization_id=1,
            customer_id="CUST123",
            agent_id=123,
            timestamp="2024-01-01T12:00:00",
            transcription_method="deepgram"
        )

        assert mock_deepgram.listen.rest.v("1").transcribe_file.called
        assert not mock_groq.audio.transcriptions.create.called
        assert "transcript" in result

    def test_transcription_method_groq_used(
        self, pipeline, mock_deepgram, mock_groq, mock_openai, mock_langfuse, mock_dlp, mock_vertexai, mock_pydub
    ):
        """
        Ensure Groq is used as the primary transcription method when explicitly specified.
        """
        result = pipeline(
            file_name="test.wav",
            organization_id=1,
            customer_id="CUST123",
            agent_id=123,
            timestamp="2024-01-01T12:00:00",
            transcription_method="groq"
        )

        assert mock_groq.audio.transcriptions.create.called
        assert not mock_deepgram.listen.rest.v("1").transcribe_file.called
        assert "transcript" in result

    def test_invalid_transcription_method_raises(self, pipeline):
        """
        If an invalid transcription method is passed, raise ValueError.
        """
        with pytest.raises(ValueError) as exc:
            pipeline(
                file_name="test.wav",
                organization_id=1,
                customer_id="CUST123",
                agent_id=123,
                timestamp="2024-01-01T12:00:00",
                transcription_method="banana"
            )
        assert "Invalid Transcription Method" in str(exc.value)

    def test_fallback_transcription_if_groq_fails(
        self, pipeline, mock_groq, mock_deepgram, mock_openai, mock_langfuse, mock_pydub, mock_dlp, mock_vertexai
    ):
        """
        If Groq fails, the pipeline should fallback to Deepgram and complete processing.
        """
        mock_groq.audio.transcriptions.create.side_effect = httpx.TimeoutException("Groq timeout")

        result = pipeline(
            file_name="test.wav",
            organization_id=1,
            customer_id="CUST123",
            agent_id=123,
            timestamp="2024-01-01T12:00:00",
            transcription_method="groq"
        )

        assert mock_groq.audio.transcriptions.create.called
        assert mock_deepgram.listen.rest.v("1").transcribe_file.called
        assert "transcript" in result

    def test_fallback_enrichment_if_openai_fails(
            self, pipeline, mock_openai, mock_vertexai, mock_deepgram, mock_pydub, mock_langfuse, mock_dlp
    ):
        """
        When OpenAI enrichment raises a retriable error, the pipeline should retry with Vertex AI and still return a
        structured payload.
        """
        # Force the primary provider (OpenAI) to fail
        mock_openai.chat.completions.create.side_effect = httpx.HTTPError("Simulated OpenAI failure")

        result = pipeline(
            file_name="test.wav",
            organization_id=1,
            customer_id="CUST123",
            agent_id=123,
            timestamp="2024-01-01T12:00:00",
            enrichment_method="openai"
        )

        assert mock_openai.chat.completions.create.called
        assert mock_vertexai.called
        assert mock_vertexai.call_count == 1

        for key in ("title", "summary", "sentiment", "topics"):
            assert key in result
        assert result["transcript"].strip() != ""

    def test_fallback_enrichment_if_vertexai_fails(
        self, pipeline, mock_vertexai, mock_openai, mock_deepgram, mock_pydub, mock_langfuse, mock_dlp
    ):
        """
        When Vertex AI enrichment fails, the pipeline should fall back to OpenAI and succeed.
        """
        mock_vertexai.side_effect = httpx.HTTPError("Simulated Gemini failure")

        result = pipeline(
            file_name="test.wav",
            organization_id=1,
            customer_id="CUST123",
            agent_id=123,
            timestamp="2024-01-01T12:00:00",
            enrichment_method="vertexai"
        )

        assert mock_vertexai.called
        assert mock_openai.chat.completions.create.called
        assert mock_openai.chat.completions.create.call_count == 1

        for key in ("title", "summary", "sentiment", "topics"):
            assert key in result

    def test_fallback_enrichment_both_fail_raises(
        self, pipeline, mock_openai, mock_vertexai, mock_deepgram, mock_pydub, mock_langfuse, mock_dlp
    ):
        """
        If both OpenAI and Vertex AI fail, the pipeline should raise a RuntimeError signalling that enrichment could not be completed.
        """
        mock_openai.chat.completions.create.side_effect = httpx.HTTPError("OpenAI meltdown")
        mock_vertexai.side_effect = httpx.HTTPError("Gemini meltdown")

        with pytest.raises(RuntimeError) as exc:
            pipeline(
                file_name="test.wav",
                organization_id=1,
                customer_id="CUST123",
                agent_id=123,
                timestamp="2024-01-01T12:00:00",
                enrichment_method="openai"      # primary
            )

        assert "Could not proceed with fallback enrichment method" in str(exc.value)

    def test_enrichment_openai_payload_structure(
        self, pipeline, mock_openai, mock_vertexai, mock_deepgram, mock_pydub, mock_langfuse, mock_dlp
    ):
        """
        When `enrichment_method="openai"` the pipeline should call the OpenAI chat completion once and not call VertexAI
        """
        result = pipeline(
            file_name="test.wav",
            organization_id=1,
            customer_id="CUST123",
            agent_id=123,
            timestamp="2024-01-01T12:00:00",
            enrichment_method="openai"
        )

        # Provider usage
        assert mock_openai.chat.completions.create.called
        assert not mock_vertexai.called

        # Basic schema checks
        assert set(result).issuperset(
            {"title", "summary", "sentiment", "topics", "suggested_topics", "new_topics", "transcript"}
        )
        assert isinstance(result["topics"], list)
        assert isinstance(result["suggested_topics"], list)
        assert isinstance(result["new_topics"], list)  # Fixed: should be list, not dict
        assert isinstance(result["sentiment"], (int, float))
        assert "<agent>" in result["transcript"] and "<customer>" in result["transcript"]

    def test_enrichment_vertexai_payload_structure(
        self, pipeline, mock_vertexai, mock_openai, mock_deepgram, mock_pydub, mock_langfuse, mock_dlp
    ):
        """
        Same assertions as above but with `enrichment_method="vertexai"`
        """

        result = pipeline(
            file_name="test.wav",
            organization_id=1,
            customer_id="CUST123",
            agent_id=123,
            timestamp="2024-01-01T12:00:00",
            enrichment_method="vertexai"
        )

        # Provider usage
        assert mock_vertexai.called
        assert not mock_openai.chat.completions.create.called

        # Schema checks
        assert set(result).issuperset(
            {"title", "summary", "sentiment", "topics", "suggested_topics", "new_topics", "transcript"}
        )
        assert isinstance(result["topics"], list)
        assert isinstance(result["suggested_topics"], list)
        assert isinstance(result["new_topics"], list)
        assert isinstance(result["sentiment"], (int, float))

    def test_enrichment_includes_suggested_topics_fields(self, pipeline, mock_openai, mock_deepgram, mock_pydub, mock_langfuse):
        """
        Test that enrichment response includes suggested_topics and new_topics fields.
        """
        result = pipeline(
            file_name="test.wav",
            organization_id=1,
            customer_id="CUST123",
            agent_id=123,
            timestamp="2024-01-01T12:00:00"
        )
        
        # Check all expected fields are present
        assert "suggested_topics" in result
        assert "new_topics" in result
        assert isinstance(result["suggested_topics"], list)
        assert isinstance(result["new_topics"], list)
        
        # Check structure of new_topics
        if result["new_topics"]:
            for topic in result["new_topics"]:
                assert "name" in topic
                assert "description" in topic

    def test_enrichment_new_topics_structure_validation(self, pipeline, mock_openai, mock_deepgram, mock_pydub, mock_langfuse):
        """
        Test that new_topics have the correct structure with name and description.
        """
        result = pipeline(
            file_name="test.wav", 
            organization_id=1,
            customer_id="CUST123",
            agent_id=123,
            timestamp="2024-01-01T12:00:00"
        )
        
        # Verify new_topics structure
        new_topics = result.get("new_topics", [])
        for topic in new_topics:
            assert isinstance(topic, dict)
            assert "name" in topic
            assert "description" in topic
            assert isinstance(topic["name"], str)
            assert isinstance(topic["description"], str)
            assert len(topic["name"]) > 0
            assert len(topic["description"]) > 0

    def test_enrichment_suggested_topics_field_present(self, pipeline, mock_openai, mock_deepgram, mock_pydub, mock_langfuse):
        """
        Test that suggested_topics field is always present in enrichment response.
        """
        result = pipeline(
            file_name="test.wav",
            organization_id=1,
            customer_id="CUST123", 
            agent_id=123,
            timestamp="2024-01-01T12:00:00"
        )
        
        # Verify suggested_topics field
        assert "suggested_topics" in result
        assert isinstance(result["suggested_topics"], list)
        # Should contain string topic names
        for topic_name in result["suggested_topics"]:
            assert isinstance(topic_name, str)

    def test_enrichment_all_new_fields_schema_compliance(self, pipeline, mock_openai, mock_deepgram, mock_pydub, mock_langfuse):
        """
        Test that all enrichment fields comply with expected schema.
        """
        result = pipeline(
            file_name="test.wav",
            organization_id=1,
            customer_id="CUST123",
            agent_id=123,
            timestamp="2024-01-01T12:00:00"
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

    def test_enrichment_with_existing_topics_and_suggested_topics(
        self, pipeline, mock_openai, mock_deepgram, mock_pydub, mock_langfuse, mock_db_handler
    ):
        """
        Test enrichment process when organization has existing topics and suggested topics.
        """
        # Mock the topic retrieval functions to return sample data
        mock_obtain_active_topics, mock_obtain_suggested_topics = mock_db_handler
        mock_obtain_active_topics.return_value = "Billing: Payment issues, Support: Technical help, "
        mock_obtain_suggested_topics.return_value = "Warranty: Product warranty claims, "
        
        result = pipeline(
            file_name="test.wav",
            organization_id=1,
            customer_id="CUST123",
            agent_id=123,
            timestamp="2024-01-01T12:00:00"
        )
        
        # Verify functions were called
        mock_obtain_active_topics.assert_called_once_with(1)
        mock_obtain_suggested_topics.assert_called_once_with(1)
        
        # Result should still contain all expected fields
        assert all(field in result for field in ["topics", "suggested_topics", "new_topics"])
        assert isinstance(result["topics"], list)
        assert isinstance(result["suggested_topics"], list) 
        assert isinstance(result["new_topics"], list)
