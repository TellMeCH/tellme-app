import datetime
from django.db import models
from tellme.call_miner.models import PeriodSummary


def check_if_refresh_needed(
        summary: PeriodSummary, conversations: models.query.QuerySet, rolling: bool, window_start: datetime,
        deviation_threshold: int = 10
) -> bool:
    """
    Decide whether the summary should be recalculated based on conversation volume changes.

    In period based mode, if the conversation count has changed significantly, a refresh is triggered
    In rolling mode, if enough new conversations have been added or the previous summary is too old,
    a refresh is triggered.

    Parameters:
        summary : PeriodSummary, The existing summary object to compare against.
        conversations : QuerySet, All conversations within the target time window.
        rolling : bool, Whether the summary is for a rolling window (uses new conversations after last_call_at).
        window_start: datetime, Date bound of the time window used to obtain relevant conversations
        deviation_threshold : int, The number of new conversations to consider when refreshing summaries

    Returns:
    (needs_refresh, current_count) : tuple[bool, int]
        - True if a summary refresh is needed, False otherwise.
        - The current number of relevant conversations.
    """
    current = conversations.count()
    previous = summary.call_count
    if previous == 0:
        return current > 0, current
    if not rolling:
        deviation = abs(current - previous) * 100 / previous
    else:
        old_latest_call = summary.last_call_at
        if window_start > old_latest_call:
            deviation = deviation_threshold + 1
        else:
            new_call_count = conversations.filter(date__gt=old_latest_call).count()
            deviation = new_call_count * 100 / previous
    return deviation > deviation_threshold, current