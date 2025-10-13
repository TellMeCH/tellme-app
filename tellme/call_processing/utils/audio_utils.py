"""
Audio format conversion utilities for call processing.

This module provides functions for converting between different audio formats,
specifically for handling mu-law encoded audio files commonly used in telephony.
"""

import wave
import audioop
import io


def decode_mulaw_file_to_wav(in_path: str, channels=2, sample_rate=8000):
    """
    Convert a raw mu-law audio file to WAV format.

    Reads raw mu-law data (2-channel interleaved) from the specified path,
    decodes it to 16-bit PCM, then writes it as a proper WAV file
    into memory and returns the WAV bytes.

    Args:
        in_path (str): Path to the input mu-law file
        channels (int): Number of audio channels (default: 2)
        sample_rate (int): Audio sample rate in Hz (default: 8000)

    Returns:
        io.BytesIO: BytesIO object containing the WAV file data
    """
    # Read raw mu-law bytes from disk
    with open(in_path, 'rb') as f:
        mulaw_bytes = f.read()

    # Split L, R mu-law bytes
    left_mulaw, right_mulaw = split_interleaved_stereo_mulaw(mulaw_bytes)

    # Decode from mu-law to linear PCM (16-bit/width of 2 bytes)
    left_pcm = audioop.ulaw2lin(left_mulaw, 2)
    right_pcm = audioop.ulaw2lin(right_mulaw, 2)

    # Re-interleave the PCM bytes into stereo
    pcm_interleaved = interleave_two_channels(left_pcm, right_pcm, sample_width=2)

    # Write the result to an in-memory WAV (BytesIO)
    output_buffer = io.BytesIO()
    with wave.open(output_buffer, 'wb') as w:
        w.setnchannels(channels)
        w.setsampwidth(2)  # 16-bit
        w.setframerate(sample_rate)
        w.writeframes(pcm_interleaved)

    # Return the WAV bytes
    return output_buffer


def split_interleaved_stereo_mulaw(mulaw_stereo: bytes):
    """
    Split interleaved stereo mu-law data into separate left and right channels.

    Args:
        mulaw_stereo (bytes): Interleaved stereo mu-law data [L0, R0, L1, R1, ...]

    Returns:
        tuple[bytes, bytes]: Left channel bytes and right channel bytes
    """
    left = bytearray()
    right = bytearray()
    for i in range(0, len(mulaw_stereo), 2):
        left.append(mulaw_stereo[i])
        right.append(mulaw_stereo[i + 1])
    return bytes(left), bytes(right)


def interleave_two_channels(left_pcm, right_pcm, sample_width=2):
    """
    Interleave left and right channel PCM data into stereo format.

    Args:
        left_pcm (bytes): Left channel PCM data
        right_pcm (bytes): Right channel PCM data
        sample_width (int): Width of each sample in bytes (default: 2 for 16-bit)

    Returns:
        bytes: Interleaved stereo PCM data [L0, R0, L1, R1, ...]
    """
    interleaved = bytearray()
    length = min(len(left_pcm), len(right_pcm))
    for i in range(0, length, sample_width):
        interleaved.extend(left_pcm[i: i + sample_width])
        interleaved.extend(right_pcm[i: i + sample_width])
    return bytes(interleaved)