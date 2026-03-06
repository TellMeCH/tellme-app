"""
Genesys AudioHook reference implementation test runner entrypoint.

Writes testconfig.cfg from environment variables and runs the npm test suite
(audiohook-reference-implementation-main). Organisation setup and teardown are
handled externally by the pytest smoke-test framework.

Environment variables:
  AUDIOHOOK_WS_URL    WebSocket URL of the server (wss:// or ws://)
  API_KEY             Plain OrganizationAPIKey value
  CLIENT_SECRET       Base64-encoded HMAC client secret
  ORG_UUID            Genesys organisation UUID (organization.cx_system_org_id)
  AGENT_ID            (Optional) TellMe agent ID; embedded in customConfig

Test configuration written to testconfig.cfg:
  [Features]
    singleChannel=false        -- single-channel tests skipped
    doubleChannel=true         -- double-channel open/close/media tests run
    transcriptionConnector=false -- transcript-connector tests skipped

Tests that run (not skipped):
  - Open Message: double-channel variants (3 tests)
  - Audiohook Monitor: Ping/Pong, Update, Discard, Error, Pause+Resume (6 tests)
  - Close Message (1 test)

Tests that are skipped:
  - Open Message: single-channel variants
  - Transcript Connector suite
  - Empty CDK Stack (always test.skip in the reference implementation)
"""

import json
import os
import subprocess
import sys

AUDIOHOOK_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "audiohook-reference-implementation-main",
)

AUDIOHOOK_WS_URL = os.environ.get("AUDIOHOOK_WS_URL")
API_KEY = os.environ.get("API_KEY")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
ORG_UUID = os.environ.get("ORG_UUID")
AGENT_ID = os.environ.get("AGENT_ID")

for _var, _name in [
    (AUDIOHOOK_WS_URL, "AUDIOHOOK_WS_URL"),
    (API_KEY, "API_KEY"),
    (CLIENT_SECRET, "CLIENT_SECRET"),
    (ORG_UUID, "ORG_UUID"),
]:
    if not _var:
        print(f"ERROR: Required environment variable {_name} is not set", file=sys.stderr)
        sys.exit(1)

# Build and write testconfig.cfg
custom_config = json.dumps({"agent_id": AGENT_ID}) if AGENT_ID else "{}"
testconfig_content = f"""[EndPoint]
url={AUDIOHOOK_WS_URL}

[Authentication]
apiKey={API_KEY}
clientSecret={CLIENT_SECRET}

[OpenParameters]
organizationId={ORG_UUID}
customConfig={custom_config}
language=en-US

[Features]
singleChannel=false
doubleChannel=true
transcriptionConnector=false
"""

testconfig_path = os.path.join(AUDIOHOOK_DIR, "testconfig.cfg")
with open(testconfig_path, "w") as f:
    f.write(testconfig_content)
print(f"Written testconfig.cfg at {testconfig_path}")

# Run the reference implementation test suite
print("Running npm run test...")
result = subprocess.run(
    ["npm", "run", "test"],
    cwd=AUDIOHOOK_DIR,
    timeout=300,
)
sys.exit(result.returncode)
