"""Date and time utilities — always timezone-aware (UTC)."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Optional


UTC = timezone.utc


def utcnow() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(UTC)


def today_utc() -> date:
    """Return today's date in UTC."""
    return datetime.now(UTC).date()


def to_utc(dt: datetime) -> datetime:
    """Convert a naive datetime to UTC-aware, or convert existing tz to UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def start_of_day(d: date) -> datetime:
    """Return midnight UTC for the given date."""
    return datetime.combine(d, time.min, tzinfo=UTC)


def end_of_day(d: date) -> datetime:
    """Return 23:59:59.999999 UTC for the given date."""
    return datetime.combine(d, time.max, tzinfo=UTC)


def start_of_month(year: int, month: int) -> date:
    """Return the first day of a given month."""
    return date(year, month, 1)


def end_of_month(year: int, month: int) -> date:
    """Return the last day of a given month."""
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, last_day)


def parse_date(value: str) -> date:
    """Parse an ISO date string (YYYY-MM-DD)."""
    return date.fromisoformat(value)


def is_past_deadline(deadline_time: time, reference_date: Optional[date] = None) -> bool:
    """Return True if the current UTC time is past the given time-of-day deadline."""
    ref_date = reference_date or today_utc()
    deadline_dt = datetime.combine(ref_date, deadline_time, tzinfo=UTC)
    return utcnow() >= deadline_dt


def is_same_day(dt: datetime, d: date) -> bool:
    """Return True if the datetime falls on the given date (UTC)."""
    return to_utc(dt).date() == d


def format_date(d: date) -> str:
    """Format a date as YYYY-MM-DD."""
    return d.strftime("%Y-%m-%d")


def format_datetime(dt: datetime) -> str:
    """Format a datetime as ISO 8601 string."""
    return to_utc(dt).isoformat()


def date_range(start: date, end: date):
    """Yield each date from start to end inclusive."""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def days_in_month(year: int, month: int) -> int:
    """Return the number of days in a month."""
    import calendar
    return calendar.monthrange(year, month)[1]


def get_week_bounds(d: date) -> tuple[date, date]:
    """Return (Monday, Sunday) of the week containing the given date."""
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def get_month_bounds(d: date) -> tuple[date, date]:
    """Return (first, last) day of the month containing the given date."""
    first = d.replace(day=1)
    last = end_of_month(d.year, d.month)
    return first, last


def get_year_bounds(year: int) -> tuple[date, date]:
    """Return (Jan 1, Dec 31) of the given year."""
    return date(year, 1, 1), date(year, 12, 31)
