"""
Transcript cleaning utilities.

This module provides utilities for cleaning transcripts using regex-based pattern matching
and replacement. Used to correct common transcription errors across all transcripts.
"""

import re


# Configuration for transcript cleaning
# Each entry contains a 'filter' (regex pattern) and 'correction' (replacement text)
TRANSCRIPT_CLEANING = [
    {
        'filter': r'\bGucci\b',
        'correction': 'Gutschein'
    },
    {
        'filter': r'\bBohnen\b',
        'correction': 'Bonus'
    },
    {
        'filter': r'\bVodouas\b',
        'correction': 'Vaudoise'
    },
    {
        'filter': r'\bVadwaz\b',
        'correction': 'Vaudoise'
    },
    {
        'filter': r'\bVoduas\b',
        'correction': 'Vaudoise'
    }
]


def clean_transcript(transcript: str) -> str:
    """
    Clean a transcript by applying regex-based corrections.

    Iterates through TRANSCRIPT_CLEANING patterns and applies replacements
    to fix common transcription errors. All replacements are case-insensitive.

    Args:
        transcript (str): The raw transcript text to clean

    Returns:
        str: The cleaned transcript with corrections applied

    Example:
        >>> clean_transcript("You have a Gucci available")
        "You have a Gutschein available"
    """
    if not transcript:
        return transcript

    cleaned = transcript
    for rule in TRANSCRIPT_CLEANING:
        pattern = rule['filter']
        correction = rule['correction']
        # Use re.IGNORECASE to match any capitalization
        cleaned = re.sub(pattern, correction, cleaned, flags=re.IGNORECASE)

    return cleaned
