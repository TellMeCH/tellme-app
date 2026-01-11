# Summary settings constants for default summarization behavior.
DEFAULT_SUMMARY_SETTINGS = {
    'topic': {
        'period': 'quarter',
        'rolling': True
    },
    'customer': {
        'period': 'eternity',
        'rolling': False
    },
    'agent': {
        'period': 'month',
        'rolling': False
    }
}


def get_default_summary_settings():
    """
    Get default summary period and rolling window settings.

    Returns:
        dict: Default settings for each object type
    """
    return DEFAULT_SUMMARY_SETTINGS.copy()