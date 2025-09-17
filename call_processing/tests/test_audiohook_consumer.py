import json
import pytest
from channels.testing import WebsocketCommunicator
from call_processing.consumers import AudioHookConsumer


@pytest.mark.django_db(transaction=True)
class TestAudioHookConsumer:
    @pytest.mark.asyncio
    async def test_stream_success(
        self,
        mock_gcs_utils,
        mock_cloud_tasks,
        setup_db,
    ):
        """
        1) Connect with a valid API key.
        2) Send an 'open' message with seq=1, expect 'opened'.
        3) Send some dummy audio frames (bytes).
        4) Send a 'close' with seq=2, expect 'closed' and finalize_recording.
        5) Ensure GCS upload and Cloud Task creation happened.
        """

        valid_api_key = setup_db[5]
        communicator = WebsocketCommunicator(
            AudioHookConsumer.as_asgi(),
            "/testws/",
            headers=[(b"x-api-key", valid_api_key.encode("utf-8"))]
        )
        connected, subprotocol = await communicator.connect()
        assert connected is True

        # Send an 'open' message with seq=1
        open_msg = {
            "version": "2",
            "type": "open",
            "seq": 1,
            "id": "test-session",
            "parameters": {
                "agent": {"id": "Agent123"},
                "participant": {"id": "CustomerABC"},
                "media": [
                    {
                        "type": "audio",
                        "format": "PCMU",
                        "channels": ["external", "internal"],
                        "rate": 8000,
                    },
                    {
                        "type": "audio",
                        "format": "PCMU",
                        "channels": ["external"],
                        "rate": 8000,
                    }
                ]
            }
        }
        await communicator.send_json_to(open_msg)

        # Expect an 'opened' message back
        response_raw = await communicator.receive_from()
        response = json.loads(response_raw)
        assert response["type"] == "opened"
        assert response["seq"] == 1
        assert response['clientseq'] == 1
        assert len(response['parameters']['media'][0]['channels']) == 2

        # Send a few audio frames (mu-law bytes). Here we just send random bytes as a placeholder.
        await communicator.send_to(bytes_data=b"\x01\x02\x03\x04")
        await communicator.send_to(bytes_data=b"\x05\x06\x07\x08")

        # Send a 'close' message with seq=2
        close_msg = {
            "version": "2",
            "type": "close",
            "seq": 2,
            "id": "test-session",
            "parameters": {
                "reason": "end"
            }
        }
        await communicator.send_json_to(close_msg)

        # Expect a 'closed' message back
        closed_raw = await communicator.receive_from()
        closed_response = json.loads(closed_raw)
        assert closed_response["type"] == "closed"
        assert closed_response["seq"] == 2

        await communicator.disconnect()

        # Check that GCS upload_to_gcs was called
        upload_mock = mock_gcs_utils[0]
        assert upload_mock.called, "Expected the consumer to upload final WAV data to GCS"

        # Check that a Cloud Task was created
        mock_create_task = mock_cloud_tasks
        assert mock_create_task.called, "Expected the consumer to create a Cloud Task after finalize_recording."

    @pytest.mark.asyncio
    async def test_unauthenticated(self):
        """
        Connect with NO api key or an invalid key.
        The consumer should respond with a 'disconnect' error message
        and eventually refuse any further messages (or close).
        """

        communicator = WebsocketCommunicator(AudioHookConsumer.as_asgi(), "/testws/")
        connected, _ = await communicator.connect()
        assert connected is True, "WebSocket is accepted initially per consumer.connect()"

        # The consumer calls self.send_error('unauthorized', ...) in connect().
        msg_raw = await communicator.receive_from()
        msg = json.loads(msg_raw)
        assert msg["type"] == "disconnect"
        assert msg['parameters']['reason'] == 'unauthorized'

        # Let's send a few 'ping' messages to see it respond with 'disconnect' again
        for i in range(2):
            ping_msg = {
                "version": "2",
                "type": "ping",
                "seq": i + 1,
                "id": "test-session"
            }
            await communicator.send_json_to(ping_msg)

            msg2_raw = await communicator.receive_from()
            msg2 = json.loads(msg2_raw)
            assert msg2["type"] == "disconnect"
            assert msg2['parameters']['reason'] == 'error'

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_out_of_order_seq(self, setup_db):
        """
        Connect properly, send an 'open' with seq=1, then skip to seq=3 to simulate out-of-order.
        The consumer should respond with 'disconnect' and close.
        """

        valid_api_key = setup_db[5]
        communicator = WebsocketCommunicator(
            AudioHookConsumer.as_asgi(),
            "/testws/",
            headers=[(b"x-api-key", valid_api_key.encode("utf-8"))]
        )
        connected, _ = await communicator.connect()
        assert connected is True

        # Send open with seq=1
        open_msg = {
            "version": "2",
            "type": "open",
            "seq": 1,
            "id": "test-session",
            "parameters": {
                "participant": {"id": "Cust123"},
                "agent": {"id": "AgentABC"},
            }
        }
        await communicator.send_json_to(open_msg)
        opened_raw = await communicator.receive_from()
        opened_resp = json.loads(opened_raw)
        assert opened_resp["type"] == "opened"

        # Now skip seq=2 and send seq=3
        ping_msg = {
            "version": "2",
            "type": "ping",
            "seq": 3,
            "id": "test-session"
        }
        await communicator.send_json_to(ping_msg)

        # We expect a "disconnect" response
        error_raw = await communicator.receive_from()
        error_resp = json.loads(error_raw)
        assert error_resp["type"] == "disconnect"
        assert error_resp["parameters"]["reason"] == "error"
        assert "Out-of-order seq" in error_resp["parameters"]["info"]

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_no_close_after_disconnect(self, setup_db):
        """
        If the consumer has sent 'disconnect', it expects a 'close'.
        If we keep sending anything else (e.g. 'ping'), it will eventually
        finalize recording and close after MAXIMUM_ERROR_RETRIES times.
        """
        valid_api_key = setup_db[5]
        communicator = WebsocketCommunicator(
            AudioHookConsumer.as_asgi(),
            "/testws/",
            headers=[(b"x-api-key", valid_api_key.encode("utf-8"))]
        )
        connected, _ = await communicator.connect()
        assert connected is True

        # Out-of-order seq right away:
        bad_msg = {
            "version": "2",
            "type": "open",
            "seq": 99,
            "id": "test-session",
        }
        await communicator.send_json_to(bad_msg)
        error_raw = await communicator.receive_from()
        error_resp = json.loads(error_raw)
        assert error_resp["type"] == "disconnect"
        assert "Out-of-order seq" in error_resp["parameters"]["info"]

        # Consumer re-sends "disconnect" up to 5 times, then forcibly closes.
        for i in range(5):
            await communicator.send_json_to({
                "version": "2",
                "type": "ping",
                "seq": 100 + i,
                "id": "test-session",
            })
            next_resp_raw = await communicator.receive_from()
            next_resp = json.loads(next_resp_raw)
            assert next_resp["type"] == "disconnect"

        assert await communicator.receive_nothing()
        await communicator.disconnect()
