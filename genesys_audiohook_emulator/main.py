import asyncio
import websockets
import json
import uuid
import time
import os
import wave
import audioop

ORGANIZATION_ID = str(uuid.uuid4())
CONVERSATION_ID = str(uuid.uuid4())
PARTICIPANT_ID = str(uuid.uuid4())
ANI = "+1-555-555-1234"
ANI_NAME = "John Doe"
DNIS = "+1-800-555-6789"
PING_INTERVAL = 5.0  # How often to send pings (seconds)
SAMPLE_RATE = 8000

WEBSOCKET_URL = os.environ.get("AUDIOHOOK_WS_URL")
WAV_FILE = os.environ.get("WAV_FILE")
API_KEY = os.environ.get('API_KEY')


def read_and_convert_lin_to_mulaw(file_path, chunk_ms=100):
    """
    Generator that reads a standard PCM .wav file, resamples it to 8 kHz,
    and outputs TWO-CHANNEL G.711 mu-law in interleaved format:
        [L0, R0, L1, R1, L2, R2, ...]

    Steps:
    1. Open WAV (N channels, 8/16-bit, any sample rate).
    2. Resample to 8 kHz with audioop.ratecv (keeping original #channels if <=2, else only first 2).
    3. If input channels < 2, replicate to form 2 channels.
    4. Convert each channel's samples from linear PCM to mu-law separately.
    5. Interleave mu-law bytes, yield ~chunk_ms worth at a time.

    => The final chunk length in bytes = 2 * (#samples) because we have 2 channels,
       each sample is 1 mu-law byte.
    """

    with wave.open(file_path, 'rb') as wf:
        in_channels = wf.getnchannels()
        in_rate = wf.getframerate()
        in_width = wf.getsampwidth()  # e.g. 2 for 16-bit
        out_rate = SAMPLE_RATE

        # We'll read ~chunk_ms from the input WAV each iteration
        chunk_frames_in = int(in_rate * (chunk_ms / 1000.0))

        # State for audioop.ratecv
        ratecv_state = None

        while True:
            frames = wf.readframes(chunk_frames_in)
            if not frames:
                break

            # Resample from in_rate -> out_rate (keeping in_channels for now).
            converted, ratecv_state = audioop.ratecv(frames, in_width, in_channels, in_rate, out_rate, ratecv_state)

            # Restrict to first 2 channels if the input was multi-channel.
            # audioop.ratecv will produce 'out_rate' frames, but still arranged in
            # (in_channels * out_width) bytes per frame. We'll do manual slicing below.
            # If in_channels=1, we treat it as mono, then replicate for "2 channels".
            # If in_channels>=2, we only keep the first 2 channels.

            # At this point, 'converted' is (N * out_width) bytes per frame,
            # with N = in_channels, not necessarily 2.

            # For convenience, let's define a small helper to split out each channel:
            channel_data = split_channels(converted, in_width, in_channels)

            if in_channels == 1:
                # Replicate the single channel => 2 channels
                left_pcm = channel_data[0]
                right_pcm = channel_data[0]
            else:
                # Use only the first 2 channels
                left_pcm = channel_data[0]
                right_pcm = channel_data[1]

            # Now convert each channel from linear PCM => mu-law
            # audioop.lin2ulaw wants (mono) data in linear PCM with a known width.
            left_mulaw = audioop.lin2ulaw(left_pcm, in_width)
            right_mulaw = audioop.lin2ulaw(right_pcm, in_width)

            # Interleave the mu-law bytes: L0, R0, L1, R1, ...
            interleaved = interleave_two_channels(left_mulaw, right_mulaw)

            yield interleaved


def split_channels(raw_data, sample_width, in_channels):
    """
    Returns a list of bytearrays, each corresponding to one channel’s PCM samples.
    For example, if in_channels=2 (stereo) and sample_width=2, then for each frame
    of 4 bytes [L0_lo, L0_hi, R0_lo, R0_hi], we append [L0_lo, L0_hi] to channel 0
    and [R0_lo, R0_hi] to channel 1.

    This is a manual approach because audioop doesn’t provide a direct “split channels” API.
    """
    # Each frame = in_channels * sample_width bytes
    # raw_data length = num_frames * in_channels * sample_width
    channel_buffers = [bytearray() for _ in range(in_channels)]
    frame_size = in_channels * sample_width

    for i in range(0, len(raw_data), frame_size):
        frame = raw_data[i:i+frame_size]
        # slice out each channel
        for ch in range(in_channels):
            start = ch * sample_width
            end = start + sample_width
            channel_buffers[ch].extend(frame[start:end])

    return channel_buffers


def interleave_two_channels(left_bytes, right_bytes):
    """
    Interleave L0, R0, L1, R1, ...
    If left_bytes and right_bytes differ in length, we stop at the smaller length.
    """
    interleaved = bytearray()
    length = min(len(left_bytes), len(right_bytes))
    for i in range(length):
        interleaved.append(left_bytes[i])
        interleaved.append(right_bytes[i])
    return bytes(interleaved)


class AudioHookEmulator:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.client_seq = 0  # Client seq counter
        self.last_server_seq_rx = 0
        self.close_reason = None

        # Track total samples "processed" or "sent" to generate the position in PTxxS.
        self.position_samples = 0

        # For waiting on "opened":
        self.opened_event = asyncio.Event()
        self.opened_received = False

        # For waiting on "closed":
        self.closed_event = asyncio.Event()
        self.closed_received = False

        # Ping/pong & RTT
        self.last_ping_time = None
        self.rtt = None

    def next_client_seq(self):
        """
        Increment and return the next client seq.
        """
        self.client_seq += 1
        return self.client_seq

    async def send_json_message(self, ws, msg_type, parameters=None):
        if parameters is None:
            parameters = {}

        # Convert the sample count into an ISO8601 duration string (PTxx.xxxS).
        seq = self.next_client_seq()
        seconds = self.position_samples / float(SAMPLE_RATE)
        position_str = f"PT{seconds:.6f}S".rstrip('0').rstrip('.')

        msg_id = str(uuid.uuid4())

        msg = {
            "version": "2",
            "type": msg_type,
            "seq": seq,
            "serverseq": self.last_server_seq_rx,  # last server message fully processed
            "id": msg_id,
            "position": position_str,
            "parameters": parameters
        }
        await ws.send(json.dumps(msg))
        print(f">>> [seq={seq}] Sent '{msg_type}': {msg}")

    async def send_open(self, ws):
        params = {
            "organizationId": ORGANIZATION_ID,
            "conversationId": CONVERSATION_ID,
            "participant": {
                "id": PARTICIPANT_ID,
                "ani": ANI,
                "aniName": ANI_NAME,
                "dnis": DNIS
            },
            "media": [
                {
                    "type": "audio",
                    "format": "PCMU",  # mu-law
                    "channels": ["external", "internal"],
                    "rate": SAMPLE_RATE
                }
            ],
            "language": "en-US"
        }
        # Force position 0 for the open message
        self.position_samples = 0
        await self.send_json_message(ws, "open", params)

    async def send_close(self, ws, reason="end"):
        params = {
            "reason": reason
        }
        await self.send_json_message(ws, "close", params)

    async def send_ping(self, ws):
        """
        Periodically send a ping. If we have a known RTT from
        the previous cycle, include it in parameters.
        """
        params = {}
        if self.rtt is not None:
            params["rtt"] = f"PT{self.rtt:.4f}S"
        self.last_ping_time = time.perf_counter()
        await self.send_json_message(ws, "ping", params)

    async def handle_server_message(self, msg_str):
        try:
            parsed = json.loads(msg_str)
        except json.JSONDecodeError:
            print("<<< Received invalid JSON from server.")
            self.close_reason = 'error'
            return

        msg_type = parsed.get("type", "<unknown>")
        server_seq = parsed.get("seq", 0)

        # Basic check for server seq
        if server_seq != self.last_server_seq_rx + 1 and self.last_server_seq_rx != 0:
            print(f"<<< Out-of-order seq from server! got={server_seq}, expected={self.last_server_seq_rx + 1}")
            self.close_reason = 'error'
            return
        self.last_server_seq_rx = server_seq

        if msg_type == "opened":
            print(f"<<< Received 'opened': {parsed}")
            self.opened_received = True
            self.opened_event.set()

        elif msg_type == "pong":
            print(f"<<< Received 'pong': {parsed}")
            if self.last_ping_time is not None:
                now = time.perf_counter()
                self.rtt = now - self.last_ping_time
                print(f"    (RTT measured: {self.rtt:.4f}s)")

        elif msg_type == "closed":
            print(f"<<< Received 'closed': {parsed}")
            self.closed_received = True
            self.closed_event.set()

        elif msg_type == "error":
            print(f"<<< Received 'error': {parsed}")
            self.close_reason = 'error'

        elif msg_type == "disconnect":
            print(f"<<< Received 'disconnect': {parsed}")
            self.close_reason = 'disconnect'

        else:
            print(f"<<< Received other/unhandled '{msg_type}': {parsed}")

    async def reader_loop(self, ws):
        """
        Continuously read messages from the server until connection is closed or we hit a fatal error.
        """
        try:
            async for msg in ws:
                await self.handle_server_message(msg)
                if self.close_reason:
                    print("Aborting read due to fatal_error.")
                    break
        except websockets.ConnectionClosed:
            print("Server closed connection (reader_loop).")

    async def ping_loop(self, ws):
        """
        Periodically send 'ping' to the server.
        """
        try:
            while not self.close_reason:
                await asyncio.sleep(PING_INTERVAL)
                if self.close_reason:
                    break
                await self.send_ping(ws)
        except asyncio.CancelledError:
            pass

    async def stream_audio(self, ws):
        """
        We read the input WAV (any #channels, sample rate) and produce
        2ch mu-law. Each chunk has (2 * n) bytes => n 2-channel samples.
        We'll increment position_samples by n for each chunk, i.e. chunk_len/2.
        """
        for mulaw_chunk in read_and_convert_lin_to_mulaw(WAV_FILE, chunk_ms=100):
            # Each chunk has length = 2 * (num_samples_in_chunk).
            # So the # of time samples = len(chunk)/2.
            num_samples = len(mulaw_chunk) // 2
            self.position_samples += num_samples

            await ws.send(mulaw_chunk)
            await asyncio.sleep(0.1)
            print(f">>> Sent chunk of size {len(mulaw_chunk)}")

    async def run_session(self):
        """
        1) Connect
        2) send open, wait for 'opened'
        3) stream audio
        4) send close, wait
        5) done
        """
        async with websockets.connect(self.ws_url, additional_headers={'X-API-KEY': API_KEY}) as ws:
            # Create tasks: read messages & ping
            reader_task = asyncio.create_task(self.reader_loop(ws))
            pinger_task = asyncio.create_task(self.ping_loop(ws))

            # 1) Send open
            await self.send_open(ws)

            # 2) Actually wait for 'opened' up to 5 seconds
            try:
                await asyncio.wait_for(self.opened_event.wait(), timeout=5.0)
                if not self.opened_received:
                    print("Timed out waiting for 'opened'!")
                    self.close_reason = 'error'
            except asyncio.TimeoutError:
                print("No 'opened' in 5 seconds.")
                self.close_reason = 'error'

            if self.close_reason:
                print("Fatal error before streaming audio. Ending.")
                # Typically you'd send a 'close' or just exit.
                pinger_task.cancel()
                reader_task.cancel()
                return

            # 3) Stream audio
            await self.stream_audio(ws)
            if self.close_reason:
                print(f"Closing connection due to {self.close_reason}")
                pinger_task.cancel()
                reader_task.cancel()
                return

            # 4) Send close
            await self.send_close(ws, reason="end")

            # 5) Wait for 'closed'
            try:
                await asyncio.wait_for(self.closed_event.wait(), timeout=10.0)
                if not self.closed_received:
                    print("Timed out waiting for 'closed'!")
                    self.close_reason = 'error'
            except asyncio.TimeoutError:
                print("No 'closed' in 5 seconds.")
                self.close_reason = 'error'

            # Cancel tasks
            pinger_task.cancel()
            reader_task.cancel()

            print("Session complete.")


def main():
    """
    Simple loop that waits for user input. Press ENTER to start streaming or 'q' to quit.
    """
    print("Genesys AudioHook Emulator")
    print("Press ENTER to start streaming or 'q' + ENTER to quit.")

    loop = asyncio.get_event_loop()

    while True:
        user_input = input("> ")
        if user_input.strip().lower() == 'q':
            print("Quitting.")
            break

        emulator = AudioHookEmulator(WEBSOCKET_URL)
        loop.run_until_complete(emulator.run_session())
        if emulator.close_reason:
            print("Session ended with a fatal error. (You can try again.)")

    loop.close()


if __name__ == "__main__":
    main()
