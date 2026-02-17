from __future__ import annotations

import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")


def is_valid_day(day: int) -> bool:
    return 1 <= day <= 7


def is_valid_lesson_number(lesson_number: int) -> bool:
    return 1 <= lesson_number <= 10


def is_valid_time(value: str) -> bool:
    return bool(TIME_RE.fullmatch(value))


def parse_time_to_datetime(base: datetime, hhmm: str, tz: ZoneInfo) -> datetime:
    hours, minutes = map(int, hhmm.split(":"))
    return base.replace(hour=hours, minute=minutes, second=0, microsecond=0, tzinfo=tz)


def now_in_timezone(tz: ZoneInfo) -> datetime:
    return datetime.now(tz)


def day_of_week_monday_first(dt: datetime) -> int:
    return dt.isoweekday()


def tomorrow(dt: datetime) -> datetime:
    return dt + timedelta(days=1)
