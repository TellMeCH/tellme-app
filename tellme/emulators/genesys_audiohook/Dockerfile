# docker remove genesys_audiohook_emulator; docker build -t genesys_audiohook_emulator ./genesys_audiohook_emulator;
# docker run --rm -it --network=tell_me_app-network -v "":/app/data -e AUDIOHOOK_WS_URL=ws://django:8080/ws/audiohook/ -e WAV_FILE=/app/data/sample_chde_call.wav -e SESSION_TOKEN= -e AGENT_ID= genesys_audiohook_emulator

# Start from any recent Python image
FROM python:3.12-slim

# Create app directory
WORKDIR /app

# Install websockets
RUN pip install --upgrade websockets

# Copy in the emulator code
COPY main.py .

# By default, run our emulator script
CMD ["python", "main.py"]