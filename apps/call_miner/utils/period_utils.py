import datetime
import zoneinfo
from dateutil.relativedelta import relativedelta

UTC = zoneinfo.ZoneInfo("UTC")
DAYS_DIFF = {'week': 7, 'month': 30, 'quarter': 90}


def period_bounds(period: str, rolling: bool = False, tz: zoneinfo.ZoneInfo = UTC) \
        -> tuple[datetime.datetime, datetime.datetime, str]:
    """
    Returns the start, end, and label for a given period.

    Parameters:
        period : "week" | "month" | "quarter", Type of time period.
        rolling : bool, default False. If True, returns a rolling window ending yesterday.
        tz : zoneinfo.ZoneInfo, default UTC. Timezone for the result.

    Returns:
        (start, end, label) : tuple
        Start and end datetimes (tz-aware, [start, end)), and a label string.
    """
    ref = datetime.datetime.now(UTC).astimezone(tz)

    if rolling:
        if period not in DAYS_DIFF.keys():
            raise ValueError(f"period must be {', '.join(DAYS_DIFF.keys())}")
        start = (ref - datetime.timedelta(days=DAYS_DIFF[period])).replace(hour=0, minute=0, second=0, microsecond=0)
        end = (ref + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        label = f'Rolling{DAYS_DIFF[period]}D'
        return start, end, label
    else:
        if period == "week":
            start = ref - datetime.timedelta(days=ref.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + datetime.timedelta(weeks=1)
            label = start.strftime("%G-W%V")
        elif period == "month":
            start = ref.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start + relativedelta(months=1)
            label = start.strftime("%Y-%m")
        elif period == "quarter":
            q_idx = (ref.month - 1) // 3
            start = ref.replace(month=q_idx * 3 + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start + relativedelta(months=3)
            label = f"{start.year}-Q{q_idx + 1}"
        else:
            raise ValueError("period must be 'week', 'month', or 'quarter'")
        return start, end, label
