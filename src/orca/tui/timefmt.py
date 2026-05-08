"""Format ISO-8601 timestamps as short relative ages: 5s, 3m, 2h, 14d."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

STALE_AFTER = timedelta(hours=24)


def parse_iso(iso_ts: str | None) -> datetime | None:
    """Parse an ISO-8601 string, returning a UTC-aware datetime or None.

    Tolerates the trailing-Z form and naive timestamps (assumes UTC).
    """
    if not iso_ts:
        return None
    try:
        ts = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts


def format_age(iso_ts: str | None, *, now: datetime | None = None) -> str:
    """Return short relative age. '-' for None or invalid input."""
    ts = parse_iso(iso_ts)
    if ts is None:
        return "-"
    cur = now or datetime.now(timezone.utc)
    sec = max(0, int((cur - ts).total_seconds()))
    if sec < 60:
        return f"{sec}s"
    if sec < 3600:
        return f"{sec // 60}m"
    if sec < 86400:
        return f"{sec // 3600}h"
    return f"{sec // 86400}d"
