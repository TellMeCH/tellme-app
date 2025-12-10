"""
CHUNK_SIZE : float
    Length of each audio chunk, in minutes.
MINIMUM_CALLER_AGE: int
    Minimum expected age of the caller, to identify birth dates vs relative dates.
MINIMUM_EXPECTED_PRICE: float
    Minimum expected price for revenue-related queries.
MAXIMUM_EXPECTED_PRICE: float
    Maximum expected price for revenue-related queries.
"""
CHUNK_SIZE: float = 5
MINIMUM_CALLER_AGE: int = 16
MINIMUM_EXPECTED_PRICE: float = 1.0
MAXIMUM_EXPECTED_PRICE: float = 10000.0
