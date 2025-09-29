"""
CHUNK_SIZE : float
    Length of each audio chunk, in minutes.
TRANSCRIPTION_MODEL_NAME_DEEPGRAM : str
    Model used when transcribing with Deepgram.
TRANSCRIPTION_MODEL_NAME_GROQ : str
    Model used when transcribing with Groq.
API_MAX_RETRIES : int
    Max retry attempts for any network call in the pipeline.
API_BASE_DELAY : float
    Initial back-off delay (seconds) for retry logic.
API_BACKOFF_FACTOR : int
    Multiplier for exponential back-off.
MINIMUM_CALLER_AGE: int
    Minimum expected age of the caller, to identify birth dates vs relative dates.
"""
CHUNK_SIZE: float = 5
TRANSCRIPTION_MODEL_NAME_DEEPGRAM: str = 'whisper-medium'
TRANSCRIPTION_MODEL_NAME_GROQ: str = 'whisper-large-v3'
API_MAX_RETRIES: int = 5
API_BASE_DELAY: float = 5.0
API_BACKOFF_FACTOR: int = 2
MINIMUM_CALLER_AGE: int = 16
MINIMUM_EXPECTED_PRICE: float = 1.0
MAXIMUM_EXPECTED_PRICE: float = 10000.0
