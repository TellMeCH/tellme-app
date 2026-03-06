# Build:
#   docker remove genesys_audiohook_emulator
#   docker build -t genesys_audiohook_emulator ./emulators/genesys_audiohook
#
# Run (local):
#   docker run --rm -it --network=tell_me_app-network \
#     -v "<path-to-wav>:/app/data" \
#     -e AUDIOHOOK_WS_URL=ws://django:8080/ws/audiohook/ \
#     -e WAV_FILE=/app/data/sample_recording.wav \
#     -e API_KEY=<plain_org_api_key> \
#     -e CX_CLIENT_SECRET=<base64_hmac_secret> \
#     -e CX_ORG_ID=<genesys_org_uuid> \
#     -e AGENT_ID=<optional_agent_uuid> \
#     genesys_audiohook_emulator

FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade websockets

COPY main.py .

CMD ["python", "main.py"]
