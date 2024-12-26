import pytest
from call_processing.utils.call_processing import CallProcessingPipeline


@pytest.mark.django_db
class TestCallProcessingPipeline:
    @pytest.fixture
    def pipeline(self, mock_deepgram, mock_openai, mock_langfuse):
        return CallProcessingPipeline()

    def test_pipeline_missing_metadata_field(self, pipeline):
        """
        Ensure that if a required metadata field is missing, we raise a ValueError.
        """
        valid_metadata = {
            "file_name": "test.wav",
            "organization_id": 0,
            'customer_id': "customer_id",
            'agent_id': 0,
            'timestamp': "2024-01-01T12:00:00"
        }
        for field in valid_metadata.keys():
            current_metadata = valid_metadata.copy()
            del current_metadata[field]
            with pytest.raises(ValueError) as exc:
                pipeline(b"fake audio", current_metadata)
            assert "Missing field" in str(exc.value)

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

    def test_transcribe_empty_audio_raises(self, pipeline, mock_deepgram, mock_pydub):
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
        metadata = {
            "file_name": "test.wav",
            "organization_id": 1,
            "customer_id": "CUST123",
            "agent_id": 123,
            "timestamp": "2024-01-01T12:00:00"
        }
        with pytest.raises(ValueError) as exc:
            pipeline(b"fake audio", metadata)
        assert "Produced transcript is empty" in str(exc.value)

    def test_transcribe_language_change_warns(self, pipeline, mock_deepgram, mock_pydub):
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

        metadata = {
            "file_name": "test.wav",
            "organization_id": 1,
            "customer_id": "CUST123",
            "agent_id": 123,
            "timestamp": "2024-01-01T12:00:00"
        }

        with pytest.raises(Warning) as exc:
            pipeline(b"fake audio", metadata)
        assert "Detected language changed suddenly" in str(exc.value)

    def test_enrich_recording_structure(self, pipeline, mock_openai, mock_deepgram, mock_pydub):
        """
        If the transcript is not empty, we confirm we get back an enriched payload
        with the fields we expect (title, summary, topics, sentiment, etc.).
        """
        metadata = {
            "file_name": "test.wav",
            "organization_id": 1,
            "customer_id": "CUST123",
            "agent_id": 123,
            "timestamp": "2024-01-01T12:00:00"
        }
        result = pipeline(b"fake audio", metadata)
        assert "title" in result
        assert "summary" in result
        assert "sentiment" in result
        assert "topics" in result
        assert "transcript" in result
        assert "<agent>:" in result["transcript"] or "<customer>:" in result["transcript"]