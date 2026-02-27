"""Tests for the Genesys AudioHook WebSocket consumer (v2 protocol, RFC 8941 auth)."""

import asyncio
import base64
import json
import uuid

import pytest
from channels.testing import WebsocketCommunicator
from django.test import override_settings
from unittest.mock import patch

from tellme.call_miner.models import Organization, OrganizationAPIKey
from tellme.call_processing.consumers import AudioHookConsumer
from tellme.call_processing.utils.audiohook_utils import build_audiohook_request_headers


WS_PATH = '/ws/audiohook/'
WS_URL = f'ws://testserver{WS_PATH}'

# Fixed secret used for all unit-test signatures; must not match any production value.
TEST_CX_CLIENT_SECRET = base64.b64encode(b'test-hmac-secret-32-bytes-minimum!').decode()
TEST_CX_ORG_UUID = uuid.UUID('aaaabbbb-cccc-4ddd-eeee-ffffffffffff')


@pytest.fixture
def audiohook_org(db):
    return Organization.objects.create(
        name='Audiohook Test Org',
        max_topic_count=10,
        cx_system_org_id=TEST_CX_ORG_UUID,
    )


@pytest.fixture
def audiohook_plain_key(audiohook_org):
    return OrganizationAPIKey.create_key(organization=audiohook_org, name='AudioHook Test Key')


def _make_headers(plain_key: str, org_uuid, session_id: str = None, correlation_id: str = None):
    """
    Build a fresh list of (bytes, bytes) WebSocket upgrade headers, including a valid
    RFC 8941 HMAC-SHA256 signature computed with TEST_CX_CLIENT_SECRET.
    Returns (header_list, session_id).
    """
    s_id = session_id or str(uuid.uuid4())
    c_id = correlation_id or str(uuid.uuid4())
    built = build_audiohook_request_headers(
        url=WS_URL,
        api_key=plain_key,
        client_secret_b64=TEST_CX_CLIENT_SECRET,
        org_id=str(org_uuid),
        session_id=s_id,
        correlation_id=c_id,
    )
    header_list = [(k.lower().encode(), v.encode()) for k, v in built.items()]
    # The consumer reads authority from the Host header; it must match the URL's netloc.
    header_list.append((b'host', b'testserver'))
    return header_list, s_id


def _open_params(org_uuid, session_id: str, agent_id: str = None) -> dict:
    """Build a standard 'open' message payload."""
    custom_config = {'agent_id': agent_id} if agent_id else {}
    return {
        'version': '2',
        'type': 'open',
        'seq': 1,
        'serverseq': 0,
        'id': session_id,
        'position': 'PT0S',
        'parameters': {
            'organizationId': str(org_uuid),
            'conversationId': str(uuid.uuid4()),
            'participant': {
                'id': str(uuid.uuid4()),
                'ani': '+1-555-0100',
                'aniName': 'Test Caller',
                'dnis': '+1-800-0000',
            },
            'media': [{'type': 'audio', 'format': 'PCMU', 'channels': ['external', 'internal'], 'rate': 8000}],
            'language': 'en-US',
            'customConfig': custom_config,
        },
    }


@pytest.mark.django_db(transaction=True)
class TestAudioHookConsumer:

    @pytest.mark.asyncio
    @override_settings(CX_CLIENT_SECRET=TEST_CX_CLIENT_SECRET)
    async def test_stream_success(self, audiohook_plain_key, audiohook_org):
        """Full happy-path: connect → open → audio frames → close → processing pipeline triggered."""
        header_list, session_id = _make_headers(audiohook_plain_key, TEST_CX_ORG_UUID)

        # Patch at the boundary the consumer actually crosses: it calls
        # processing_utils.upload_file_and_create_processing_task(...) directly.
        # Mocking that function avoids all cross-module import-path ambiguity that makes
        # lower-level mocks (gcs_utils.upload_to_gcs, create_processing_task) unreliable
        # in the thread-pool executor context.  The processing pipeline internals are
        # covered by test_queue.py.
        with patch('tellme.call_processing.consumers.audio_utils.decode_mulaw_file_to_wav', return_value=b'WAV'), \
             patch('tellme.call_processing.consumers.processing_utils.upload_file_and_create_processing_task',
                   return_value=({'message': 'queued'}, 202)) as mock_process:
            communicator = WebsocketCommunicator(AudioHookConsumer.as_asgi(), WS_PATH, headers=header_list)
            connected, _ = await communicator.connect()
            assert connected is True

            await communicator.send_json_to(_open_params(TEST_CX_ORG_UUID, session_id))
            opened = json.loads(await communicator.receive_from())
            assert opened['type'] == 'opened'
            assert opened['seq'] == 1
            assert opened['clientseq'] == 1
            assert len(opened['parameters']['media'][0]['channels']) == 2

            await communicator.send_to(bytes_data=b'\x7f' * 160)
            await communicator.send_to(bytes_data=b'\x7f' * 160)

            await communicator.send_json_to({
                'version': '2', 'type': 'close', 'seq': 2,
                'serverseq': 1, 'id': session_id, 'position': 'PT0.02S',
                'parameters': {'reason': 'end'},
            })
            closed = json.loads(await communicator.receive_from())
            assert closed['type'] == 'closed'
            assert closed['seq'] == 2

            # Allow the thread-pool executor (_finalize_recording_sync) to complete.
            await asyncio.sleep(0.2)
            await communicator.disconnect()

            # Assert inside the with-block: patches are still active, no race with __exit__.
            mock_process.assert_called_once()

    @pytest.mark.asyncio
    @override_settings(CX_CLIENT_SECRET=TEST_CX_CLIENT_SECRET)
    async def test_unauthenticated_no_headers(self):
        """No auth headers → disconnect with reason='unauthorized'; subsequent pings are silently ignored."""
        communicator = WebsocketCommunicator(AudioHookConsumer.as_asgi(), WS_PATH)
        connected, _ = await communicator.connect()
        assert connected is True

        msg = json.loads(await communicator.receive_from())
        assert msg['type'] == 'disconnect'
        assert msg['parameters']['reason'] == 'unauthorized'

        # Non-close messages after disconnect are silently ignored (no response)
        await communicator.send_json_to({
            'version': '2', 'type': 'ping', 'seq': 1,
            'serverseq': 1, 'id': 'x', 'position': 'PT0S', 'parameters': {},
        })
        assert await communicator.receive_nothing()

        await communicator.disconnect()

    @pytest.mark.asyncio
    @override_settings(CX_CLIENT_SECRET=TEST_CX_CLIENT_SECRET)
    async def test_invalid_signature(self, audiohook_plain_key, audiohook_org):
        """Valid headers but wrong HMAC value → disconnect with reason='unauthorized'."""
        header_list, _ = _make_headers(audiohook_plain_key, TEST_CX_ORG_UUID)
        # Replace the Signature header with a correctly formatted but wrong HMAC
        bad_sig_b64 = base64.b64encode(b'a' * 32).decode()
        bad_sig_value = f'sig1=:{bad_sig_b64}:'.encode()
        corrupted = [(k, bad_sig_value if k == b'signature' else v) for k, v in header_list]

        communicator = WebsocketCommunicator(AudioHookConsumer.as_asgi(), WS_PATH, headers=corrupted)
        connected, _ = await communicator.connect()
        assert connected is True

        msg = json.loads(await communicator.receive_from())
        assert msg['type'] == 'disconnect'
        assert msg['parameters']['reason'] == 'unauthorized'

        await communicator.disconnect()

    @pytest.mark.asyncio
    @override_settings(CX_CLIENT_SECRET=TEST_CX_CLIENT_SECRET)
    async def test_unknown_org(self):
        """Valid HMAC signature but API key not in DB → disconnect with reason='unauthorized'."""
        # Build signed headers for a key that does not exist in the database
        unknown_key = 'not-a-real-api-key'
        header_list, _ = _make_headers(unknown_key, TEST_CX_ORG_UUID)

        communicator = WebsocketCommunicator(AudioHookConsumer.as_asgi(), WS_PATH, headers=header_list)
        connected, _ = await communicator.connect()
        assert connected is True

        msg = json.loads(await communicator.receive_from())
        assert msg['type'] == 'disconnect'
        assert msg['parameters']['reason'] == 'unauthorized'

        await communicator.disconnect()

    @pytest.mark.asyncio
    @override_settings(CX_CLIENT_SECRET=TEST_CX_CLIENT_SECRET)
    async def test_org_id_mismatch_in_open(self, audiohook_plain_key, audiohook_org):
        """Auth succeeds but organizationId in open body differs from org.cx_system_org_id → disconnect."""
        header_list, session_id = _make_headers(audiohook_plain_key, TEST_CX_ORG_UUID)
        communicator = WebsocketCommunicator(AudioHookConsumer.as_asgi(), WS_PATH, headers=header_list)
        connected, _ = await communicator.connect()
        assert connected is True

        open_msg = _open_params(TEST_CX_ORG_UUID, session_id)
        open_msg['parameters']['organizationId'] = str(uuid.uuid4())  # wrong UUID
        await communicator.send_json_to(open_msg)

        msg = json.loads(await communicator.receive_from())
        assert msg['type'] == 'disconnect'
        assert msg['parameters']['reason'] == 'unauthorized'

        await communicator.disconnect()

    @pytest.mark.asyncio
    @override_settings(CX_CLIENT_SECRET=TEST_CX_CLIENT_SECRET)
    async def test_out_of_order_seq(self, audiohook_plain_key, audiohook_org):
        """After open, a non-sequential seq → disconnect with reason='error'."""
        header_list, session_id = _make_headers(audiohook_plain_key, TEST_CX_ORG_UUID)
        communicator = WebsocketCommunicator(AudioHookConsumer.as_asgi(), WS_PATH, headers=header_list)
        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_json_to(_open_params(TEST_CX_ORG_UUID, session_id))
        assert json.loads(await communicator.receive_from())['type'] == 'opened'

        # Skip seq=2, jump to seq=3
        await communicator.send_json_to({
            'version': '2', 'type': 'ping', 'seq': 3,
            'serverseq': 1, 'id': session_id, 'position': 'PT0S', 'parameters': {},
        })
        msg = json.loads(await communicator.receive_from())
        assert msg['type'] == 'disconnect'
        assert msg['parameters']['reason'] == 'error'
        assert 'Out-of-order seq' in msg['parameters']['info']

        await communicator.disconnect()

    @pytest.mark.asyncio
    @override_settings(CX_CLIENT_SECRET=TEST_CX_CLIENT_SECRET)
    async def test_post_disconnect_messages_silently_ignored(self, audiohook_plain_key, audiohook_org):
        """After a disconnect is sent, non-close messages produce no response."""
        header_list, session_id = _make_headers(audiohook_plain_key, TEST_CX_ORG_UUID)
        communicator = WebsocketCommunicator(AudioHookConsumer.as_asgi(), WS_PATH, headers=header_list)
        connected, _ = await communicator.connect()
        assert connected is True

        # Trigger a disconnect via out-of-order seq (seq=99 instead of expected seq=1)
        await communicator.send_json_to({
            'version': '2', 'type': 'open', 'seq': 99,
            'serverseq': 0, 'id': session_id, 'position': 'PT0S', 'parameters': {},
        })
        assert json.loads(await communicator.receive_from())['type'] == 'disconnect'

        # Pings with consecutive seqs starting from 1 are silently ignored
        await communicator.send_json_to({
            'version': '2', 'type': 'ping', 'seq': 1,
            'serverseq': 1, 'id': session_id, 'position': 'PT0S', 'parameters': {},
        })
        assert await communicator.receive_nothing()

        await communicator.disconnect()

    @pytest.mark.asyncio
    @override_settings(CX_CLIENT_SECRET=TEST_CX_CLIENT_SECRET)
    async def test_update_message(self, audiohook_plain_key, audiohook_org):
        """'update' message → server replies with 'updated'."""
        header_list, session_id = _make_headers(audiohook_plain_key, TEST_CX_ORG_UUID)
        communicator = WebsocketCommunicator(AudioHookConsumer.as_asgi(), WS_PATH, headers=header_list)
        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_json_to(_open_params(TEST_CX_ORG_UUID, session_id))
        assert json.loads(await communicator.receive_from())['type'] == 'opened'

        await communicator.send_json_to({
            'version': '2', 'type': 'update', 'seq': 2,
            'serverseq': 1, 'id': session_id, 'position': 'PT0S',
            'parameters': {'language': 'fr-FR'},
        })
        msg = json.loads(await communicator.receive_from())
        assert msg['type'] == 'updated'
        assert msg['clientseq'] == 2

        await communicator.disconnect()

    @pytest.mark.asyncio
    @override_settings(CX_CLIENT_SECRET=TEST_CX_CLIENT_SECRET)
    async def test_discarded_message(self, audiohook_plain_key, audiohook_org):
        """'discarded' message → no response, no crash."""
        header_list, session_id = _make_headers(audiohook_plain_key, TEST_CX_ORG_UUID)
        communicator = WebsocketCommunicator(AudioHookConsumer.as_asgi(), WS_PATH, headers=header_list)
        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_json_to(_open_params(TEST_CX_ORG_UUID, session_id))
        assert json.loads(await communicator.receive_from())['type'] == 'opened'

        await communicator.send_json_to({
            'version': '2', 'type': 'discarded', 'seq': 2,
            'serverseq': 1, 'id': session_id, 'position': 'PT0.1S',
            'parameters': {'start': 'PT0S', 'discarded': 'PT0.1S'},
        })
        assert await communicator.receive_nothing()

        await communicator.disconnect()

    @pytest.mark.asyncio
    @override_settings(CX_CLIENT_SECRET=TEST_CX_CLIENT_SECRET)
    async def test_error_message(self, audiohook_plain_key, audiohook_org):
        """'error' message → no response, no crash."""
        header_list, session_id = _make_headers(audiohook_plain_key, TEST_CX_ORG_UUID)
        communicator = WebsocketCommunicator(AudioHookConsumer.as_asgi(), WS_PATH, headers=header_list)
        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_json_to(_open_params(TEST_CX_ORG_UUID, session_id))
        assert json.loads(await communicator.receive_from())['type'] == 'opened'

        await communicator.send_json_to({
            'version': '2', 'type': 'error', 'seq': 2,
            'serverseq': 1, 'id': session_id, 'position': 'PT0S',
            'parameters': {'code': 500, 'message': 'Network problem'},
        })
        assert await communicator.receive_nothing()

        await communicator.disconnect()

    @pytest.mark.asyncio
    @override_settings(CX_CLIENT_SECRET=TEST_CX_CLIENT_SECRET)
    async def test_custom_config_agent_id(self, audiohook_plain_key, audiohook_org):
        """agent_id in customConfig is accepted and session closes cleanly."""
        header_list, session_id = _make_headers(audiohook_plain_key, TEST_CX_ORG_UUID)
        communicator = WebsocketCommunicator(AudioHookConsumer.as_asgi(), WS_PATH, headers=header_list)
        connected, _ = await communicator.connect()
        assert connected is True

        agent_uuid = str(uuid.uuid4())
        await communicator.send_json_to(_open_params(TEST_CX_ORG_UUID, session_id, agent_id=agent_uuid))
        assert json.loads(await communicator.receive_from())['type'] == 'opened'

        await communicator.send_json_to({
            'version': '2', 'type': 'close', 'seq': 2,
            'serverseq': 1, 'id': session_id, 'position': 'PT0S',
            'parameters': {'reason': 'end'},
        })
        msg = json.loads(await communicator.receive_from())
        assert msg['type'] == 'closed'

        await communicator.disconnect()
