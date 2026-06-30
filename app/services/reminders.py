"""Reminder date calculation.

The next reminder date is derived from an activity date plus an interval expressed
in days, months, or years. Month/year math is the classic footgun (e.g. Jan 31 +
1 month), so adding it here once — and clamping to the end of the target month —
keeps the rest of the app free of date edge cases.

Implemented with the standard library only to avoid an extra dependency.
"""

from __future__ import annotations

import calendar
from datetime import date

VALID_UNITS = ("days", "months", "years")


def add_interval(start: date, interval: int, unit: str) -> date:
    """Return ``start`` advanced by ``interval`` units.

    For 'months' and 'years', if the resulting day would overflow the target
    month (e.g. adding a month to Jan 31), it is clamped to that month's last day.
    """
    if unit == "days":
        from datetime import timedelta

        return start + timedelta(days=interval)

    if unit == "months":
        total_months = (start.year * 12 + (start.month - 1)) + interval
        year, month = divmod(total_months, 12)
        month += 1
    elif unit == "years":
        year, month = start.year + interval, start.month
    else:
        raise ValueError(f"Unknown reminder unit: {unit!r}")

    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(start.day, last_day))


def compute_next_reminder_date(
    activity_date: date, interval: int | None, unit: str | None
) -> date | None:
    """Compute the next reminder date, or ``None`` when no reminder is set.

    A reminder exists only when both a positive interval and a valid unit are
    provided.
    """
    if not interval or interval <= 0 or unit not in VALID_UNITS:
        return None
    return add_interval(activity_date, interval, unit)
