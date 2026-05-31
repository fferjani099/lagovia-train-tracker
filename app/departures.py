from datetime import datetime, timedelta, timezone
from typing import Any

from app.models import RawDeparture


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def isoformat_z(value: datetime) -> str:
    normalized = to_utc(value).replace(microsecond=0)
    return normalized.isoformat().replace("+00:00", "Z")


def delay_seconds_to_minutes(delay_seconds: int) -> int:
    return int(delay_seconds) // 60


def filter_by_departure_window(
    departures: list[RawDeparture],
    now: datetime,
    window_minutes: int,
) -> list[RawDeparture]:
    window_start = to_utc(now)
    window_end = window_start + timedelta(minutes=window_minutes)

    return [
        departure
        for departure in departures
        if window_start
        <= to_utc(departure.scheduled_departure_time)
        <= window_end
    ]


def departure_to_response(departure: RawDeparture) -> dict[str, Any]:
    return {
        "trainNumber": departure.train_number,
        "destination": departure.destination,
        "scheduledDepartureTime": isoformat_z(departure.scheduled_departure_time),
        "delayMinutes": delay_seconds_to_minutes(departure.delay_seconds),
    }

