"""
Utilities for Genesys AudioHook protocol authentication and session management.

Implements:
- RFC 8941 structured field parsing (targeted subset for AudioHook signatures)
- HMAC-SHA256 HTTP Signature verification (RFC 8941 / HTTP Message Signatures)
- Organization lookup from AudioHook WebSocket upgrade headers
- Media format selection
- AudioHook request header building (used by the emulator and tests)

Authentication flow:
  1. Hash the incoming X-API-KEY with HASH_KEY → look up OrganizationAPIKey → get Organization
  2. Verify the HMAC-SHA256 signature using settings.CX_CLIENT_SECRET
  3. Cross-validate audiohook-organization-id against organization.cx_system_org_id
"""

import base64
import hashlib
import hmac
import logging
import re
import secrets
import time
from urllib.parse import urlparse

from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed


MAX_CLOCK_SKEW = 3        # seconds of allowed clock difference between client and server
MAX_SIGNATURE_AGE = 10    # seconds — signatures older than this are rejected
MIN_NONCE_LENGTH = 22     # characters — nonces shorter than this are rejected
FAILURE_DELAY_SECONDS = 0.5  # minimum response time on any auth failure (timing safety)

# All six components that must be covered by the signature
REQUIRED_COMPONENTS = [
    '@request-target',
    '@authority',
    'audiohook-organization-id',
    'audiohook-session-id',
    'audiohook-correlation-id',
    'x-api-key',
]


# RFC 8941 structured field parsing (targeted subset)
# The Genesys AudioHook client sends Signature-Input and Signature headers in
# the RFC 8941 structured fields dictionary format. The subset we need to parse
# is highly regular, so a focused parser is used rather than a full library.
#
# Signature-Input example:
#   sig1=("@request-target" "@authority" "audiohook-organization-id"
#         "audiohook-session-id" "audiohook-correlation-id"
#         "x-api-key");keyid="<key>";created=1234567890;nonce="<nonce>"
#
# Signature example:
#   sig1=:<base64-encoded-hmac>:

def _parse_signature_input(header_value: str) -> tuple[str, list[str], dict, str]:
    """
    Parse a Signature-Input header value.

    Returns:
        label           - the signature label (e.g. "sig1")
        component_names - ordered list of covered component names
        params          - dict of signature parameters (keyid, created, nonce, etc.)
        raw_inner_list  - the raw inner list string used when building the sig base
    Raises:
        ValueError on malformed input.
    """
    # Split on first '=' to get label and the rest
    eq_pos = header_value.index('=')
    label = header_value[:eq_pos].strip()
    rest = header_value[eq_pos + 1:].strip()

    # The rest is an inner list: (...components...);param1=v1;param2=v2
    inner_match = re.match(r'^\(([^)]*)\)(.*)', rest)
    if not inner_match:
        raise ValueError(f'Malformed Signature-Input inner list: {rest!r}')

    components_str = inner_match.group(1)
    params_str = inner_match.group(2)
    raw_inner_list = rest  # kept verbatim for signature base building

    # Extract quoted component names from the inner list
    component_names = re.findall(r'"([^"]+)"', components_str)

    # Parse semicolon-separated parameters: ;key="value" or ;key=integer
    params: dict = {}
    for match in re.finditer(r';(\w+)=(?:"([^"]*)"|([-\d]+))', params_str):
        key = match.group(1)
        value = match.group(2) if match.group(2) is not None else int(match.group(3))
        params[key] = value

    return label, component_names, params, raw_inner_list


def _parse_signature(header_value: str) -> tuple[str, bytes]:
    """
    Parse a Signature header value.

    Returns:
        label     - the signature label (e.g. "sig1")
        sig_bytes - raw HMAC bytes decoded from the RFC 8941 byte sequence (`:base64:`)
    Raises:
        ValueError on malformed input.
    """
    eq_pos = header_value.index('=')
    label = header_value[:eq_pos].strip()
    rest = header_value[eq_pos + 1:].strip()

    # RFC 8941 byte sequence is enclosed in colons: :base64data:
    byte_seq_match = re.match(r'^:([A-Za-z0-9+/=]*):', rest)
    if not byte_seq_match:
        raise ValueError(f'Malformed Signature byte sequence: {rest!r}')

    sig_bytes = base64.b64decode(byte_seq_match.group(1))
    return label, sig_bytes


# Signature base string construction
def _build_signature_base(
    component_names: list[str],
    headers: dict,
    request_target: str,
    authority: str,
    raw_sig_params: str,
) -> str:
    """
    Build the signature base string as defined by RFC 8941 / HTTP Message Signatures.

    Each covered component contributes one line: `"<name>": <value>`
    The final line is always: `"@signature-params": <raw_inner_list>`
    Lines are joined with newlines (no trailing newline).
    """
    lines = []
    for name in component_names:
        if name == '@request-target':
            value = request_target
        elif name == '@authority':
            value = authority
        else:
            # Regular header — look up in the headers dict (already lowercased)
            value = headers.get(name, '')
            if not value:
                raise ValueError(f'Required header {name!r} not present in request')
        lines.append(f'"{name}": {value}')

    lines.append(f'"@signature-params": {raw_sig_params}')
    return '\n'.join(lines)


# Core HMAC-SHA256 signature verification
async def verify_audiohook_signature(
    headers: dict,
    request_target: str,
    authority: str,
) -> tuple[bool, str]:
    """
    Verify the HMAC-SHA256 HTTP Signature sent by the Genesys AudioHook client.

    Always waits at least FAILURE_DELAY_SECONDS before returning on any failure
    to prevent timing side-channel attacks.

    Args:
        headers:        Lowercase header dict from the WebSocket scope.
        request_target: The HTTP request path+query (e.g. "/ws/audiohook/").
        authority:      The HTTP Host header value (e.g. "app.tell-me.ch").

    Returns:
        (True,  "")      on success
        (False, reason)  on any failure
    """
    import asyncio
    start = asyncio.get_event_loop().time()
    ok, reason = _verify_signature_sync(headers, request_target, authority)
    if not ok:
        elapsed = asyncio.get_event_loop().time() - start
        delay = FAILURE_DELAY_SECONDS - elapsed
        if delay > 0:
            await asyncio.sleep(delay)
    return ok, reason


def _verify_signature_sync(
    headers: dict,
    request_target: str,
    authority: str,
) -> tuple[bool, str]:
    """Synchronous inner implementation of signature verification."""

    # Check client secret is configured
    client_secret_b64 = settings.CX_CLIENT_SECRET
    if not client_secret_b64:
        return False, 'CX_CLIENT_SECRET is not configured'
    try:
        client_secret = base64.b64decode(client_secret_b64)
    except Exception:
        return False, 'CX_CLIENT_SECRET is not valid base64'

    # Extract and validate X-API-KEY
    api_key = headers.get('x-api-key', '')
    if not api_key:
        return False, 'Missing X-API-KEY header'

    # Parse Signature-Input
    sig_input_raw = headers.get('signature-input', '')
    if not sig_input_raw:
        return False, 'Missing Signature-Input header'
    try:
        label, component_names, sig_params, raw_inner_list = _parse_signature_input(sig_input_raw)
    except (ValueError, Exception) as e:
        return False, f'Malformed Signature-Input: {e}'

    # Parse Signature
    sig_raw = headers.get('signature', '')
    if not sig_raw:
        return False, 'Missing Signature header'
    try:
        sig_label, sig_bytes = _parse_signature(sig_raw)
    except (ValueError, Exception) as e:
        return False, f'Malformed Signature: {e}'

    if sig_label != label:
        return False, f'Signature label {sig_label!r} does not match Signature-Input label {label!r}'

    # Validate keyid matches X-API-KEY
    keyid = sig_params.get('keyid', '')
    if keyid != api_key:
        return False, 'Signature keyid does not match X-API-KEY header'

    # Validate nonce
    nonce = sig_params.get('nonce', '')
    if not nonce:
        return False, 'Missing nonce in signature parameters'
    if len(str(nonce)) < MIN_NONCE_LENGTH:
        return False, f'Nonce must be at least {MIN_NONCE_LENGTH} characters'

    # Validate timestamp
    created = sig_params.get('created')
    if created is None:
        return False, 'Missing created in signature parameters'
    now = int(time.time())
    if created > now + MAX_CLOCK_SKEW:
        return False, 'Signature created timestamp is in the future'
    if created + MAX_SIGNATURE_AGE < now - MAX_CLOCK_SKEW:
        return False, 'Signature has expired'

    # Validate required components are all covered
    missing = [c for c in REQUIRED_COMPONENTS if c not in component_names]
    if missing:
        return False, f'Signature does not cover required components: {missing}'

    # Build signature base string
    # Decode header values from bytes if needed (WebSocket scope stores bytes)
    str_headers = {
        k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v
        for k, v in headers.items()
    }
    try:
        sig_base = _build_signature_base(
            component_names, str_headers, request_target, authority, raw_inner_list
        )
    except ValueError as e:
        return False, f'Cannot build signature base: {e}'

    # HMAC-SHA256 timing-safe comparison
    computed = hmac.new(client_secret, sig_base.encode('utf-8'), hashlib.sha256).digest()
    if not hmac.compare_digest(computed, sig_bytes):
        return False, 'Signature does not match'

    return True, ''


# Organization lookup
@sync_to_async
def get_org_from_audiohook_headers(headers: dict):
    """
    Resolve the TellMe Organization from AudioHook WebSocket upgrade headers.

    Primary lookup: hash X-API-KEY with HASH_KEY → OrganizationAPIKey → Organization.
    Secondary validation: audiohook-organization-id == organization.cx_system_org_id.

    Args:
        headers: Raw headers dict from the WebSocket scope (may have bytes keys/values).

    Returns:
        Organization instance.

    Raises:
        AuthenticationFailed with a descriptive reason on any failure.
    """
    from tellme.call_miner.models import OrganizationAPIKey

    def _decode(v):
        return v.decode('utf-8') if isinstance(v, bytes) else v

    plain_key = _decode(headers.get(b'x-api-key') or headers.get('x-api-key') or '')
    if not plain_key:
        raise AuthenticationFailed('Missing X-API-KEY header')

    hashed = hashlib.sha256(
        (settings.HASH_KEY + plain_key + settings.HASH_KEY).encode('utf-8')
    ).hexdigest()

    try:
        api_key_obj = OrganizationAPIKey.objects.select_related('organization').get(hashed_api_key=hashed)
    except OrganizationAPIKey.DoesNotExist:
        raise AuthenticationFailed('Unknown API key')

    if api_key_obj.expires < timezone.now():
        raise AuthenticationFailed('API key has expired')

    org = api_key_obj.organization

    cx_org_id = _decode(headers.get(b'audiohook-organization-id') or headers.get('audiohook-organization-id') or '')
    if not cx_org_id:
        raise AuthenticationFailed('Missing Audiohook-Organization-Id header')

    if not org.cx_system_org_id or str(org.cx_system_org_id) != cx_org_id:
        raise AuthenticationFailed('Audiohook-Organization-Id does not match organization')

    return org


# Media format selection
def select_media(offered: list) -> dict | None:
    """
    Select the best media format from the list offered by the CX system in the open message.

    Preference order:
      1. Two-channel PCMU at 8000 Hz  (preferred — matches existing decode logic)
      2. Any two-channel format at 8000 Hz
      3. First offered format (fallback)

    Returns exactly one unmodified item from the offered list, or None if the list is empty.
    """
    if not offered:
        return None

    two_ch_pcmu = [
        m for m in offered
        if m.get('format') == 'PCMU'
        and len(m.get('channels', [])) == 2
        and m.get('rate') == 8000
    ]
    if two_ch_pcmu:
        return two_ch_pcmu[0]

    two_ch = [m for m in offered if len(m.get('channels', [])) == 2]
    if two_ch:
        return two_ch[0]

    return offered[0]


# Request header builder (used by emulator and unit tests)
def build_audiohook_request_headers(
    url: str,
    api_key: str,
    client_secret_b64: str,
    org_id: str,
    session_id: str,
    correlation_id: str,
) -> dict:
    """
    Build the complete set of WebSocket upgrade headers for a Genesys AudioHook client.

    Computes an RFC 8941-compatible HMAC-SHA256 signature covering the six required
    components and returns a dict ready to pass as `additional_headers` to `websockets.connect`.

    Args:
        url:               Full WebSocket URL (ws:// or wss://).
        api_key:           Plain OrganizationAPIKey value.
        client_secret_b64: Base64-encoded HMAC client secret (settings.CX_CLIENT_SECRET).
        org_id:            CX system organization UUID string (organization.cx_system_org_id).
        session_id:        UUID string for this session.
        correlation_id:    UUID string for correlation.

    Returns:
        Dict of header name → value, including Signature-Input and Signature.
    """
    parsed = urlparse(url)
    request_target = parsed.path + (f'?{parsed.query}' if parsed.query else '')
    authority = parsed.netloc

    now = int(time.time())
    nonce = secrets.token_urlsafe(22)  # >= 22 chars as required

    # Build the Signature-Input inner list string
    component_list = ' '.join(f'"{c}"' for c in REQUIRED_COMPONENTS)
    raw_inner_list = (
        f'({component_list})'
        f';keyid="{api_key}"'
        f';created={now}'
        f';nonce="{nonce}"'
    )

    # Build the signature base string
    header_values = {
        'audiohook-organization-id': org_id,
        'audiohook-session-id': session_id,
        'audiohook-correlation-id': correlation_id,
        'x-api-key': api_key,
    }
    lines = []
    for name in REQUIRED_COMPONENTS:
        if name == '@request-target':
            value = request_target
        elif name == '@authority':
            value = authority
        else:
            value = header_values[name]
        lines.append(f'"{name}": {value}')
    lines.append(f'"@signature-params": {raw_inner_list}')
    sig_base = '\n'.join(lines)

    # Compute HMAC-SHA256
    client_secret = base64.b64decode(client_secret_b64)
    signature = hmac.new(client_secret, sig_base.encode('utf-8'), hashlib.sha256).digest()
    sig_b64 = base64.b64encode(signature).decode('ascii')

    return {
        'X-API-KEY': api_key,
        'Audiohook-Organization-Id': org_id,
        'Audiohook-Session-Id': session_id,
        'Audiohook-Correlation-Id': correlation_id,
        'Signature-Input': f'sig1={raw_inner_list}',
        'Signature': f'sig1=:{sig_b64}:',
    }
