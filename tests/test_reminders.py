from datetime import date

import pytest

from app.services.reminders import add_interval, compute_next_reminder_date


def test_add_days():
    assert add_interval(date(2026, 1, 10), 5, "days") == date(2026, 1, 15)


def test_add_months_simple():
    assert add_interval(date(2026, 1, 15), 3, "months") == date(2026, 4, 15)


def test_add_months_rolls_over_year():
    assert add_interval(date(2026, 11, 10), 3, "months") == date(2027, 2, 10)


def test_add_months_clamps_end_of_month():
    # Jan 31 + 1 month -> Feb 28 (2026 is not a leap year).
    assert add_interval(date(2026, 1, 31), 1, "months") == date(2026, 2, 28)


def test_add_years_leap_day_clamps():
    # Feb 29 (leap) + 1 year -> Feb 28.
    assert add_interval(date(2024, 2, 29), 1, "years") == date(2025, 2, 28)


def test_unknown_unit_raises():
    with pytest.raises(ValueError):
        add_interval(date(2026, 1, 1), 1, "weeks")


@pytest.mark.parametrize(
    "interval,unit",
    [(None, "months"), (0, "months"), (-1, "days"), (3, "weeks"), (3, None)],
)
def test_no_reminder_returns_none(interval, unit):
    assert compute_next_reminder_date(date(2026, 1, 1), interval, unit) is None


def test_reminder_computed():
    assert compute_next_reminder_date(date(2026, 1, 1), 6, "months") == date(
        2026, 7, 1
    )
