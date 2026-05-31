from datetime import datetime, timedelta, timezone

from _runner import run_pytest_for_current_file
from app.departures import (
    delay_seconds_to_minutes,
    departure_to_response,
    filter_by_departure_window,
    isoformat_z,
)
from app.models import RawDeparture


NOW = datetime(2026, 5, 31, 13, 0, tzinfo=timezone.utc)


def test_filter_by_departure_window_includes_start_and_end_boundaries() -> None:
    at_start = RawDeparture("IC1", "Ghent", NOW, 0)
    at_end = RawDeparture("IC2", "Antwerp", NOW + timedelta(minutes=15), 0)
    before_start = RawDeparture("IC3", "Bruges", NOW - timedelta(seconds=1), 0)
    after_end = RawDeparture("IC4", "Liege", NOW + timedelta(minutes=16), 0)

    filtered = filter_by_departure_window(
        [at_start, at_end, before_start, after_end],
        NOW,
        15,
    )

    assert filtered == [at_start, at_end]


def test_delay_seconds_to_minutes_returns_whole_minutes() -> None:
    assert delay_seconds_to_minutes(240) == 4


def test_departure_to_response_formats_public_shape() -> None:
    departure = RawDeparture(
        train_number="IC1234",
        destination="Antwerp-Central",
        scheduled_departure_time=NOW + timedelta(minutes=8),
        delay_seconds=240,
    )

    assert departure_to_response(departure) == {
        "trainNumber": "IC1234",
        "destination": "Antwerp-Central",
        "scheduledDepartureTime": "2026-05-31T13:08:00Z",
        "delayMinutes": 4,
    }


def test_isoformat_z_normalizes_to_utc() -> None:
    value = datetime(2026, 5, 31, 15, 0, tzinfo=timezone(timedelta(hours=2)))

    assert isoformat_z(value) == "2026-05-31T13:00:00Z"


if __name__ == "__main__":
    run_pytest_for_current_file(__file__)
