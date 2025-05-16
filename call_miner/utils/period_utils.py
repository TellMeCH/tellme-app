import datetime
import zoneinfo
from dateutil.relativedelta import relativedelta

UTC = zoneinfo.ZoneInfo("UTC")


def period_bounds(period: str, ref: datetime.datetime | None = None, tz: zoneinfo.ZoneInfo = UTC) \
        -> tuple[datetime.datetime, datetime.datetime, str]:
    """Return (start, end, label) for the period that contains *ref*."""
    ref = (ref or datetime.datetime.now(UTC)).astimezone(tz)

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
