from _runner import run_pytest_for_current_file
from app.models import Station
from app.stations import match_stations


def test_match_stations_uses_case_insensitive_substring() -> None:
    stations = [
        Station(id="1", name="Brussels-Central"),
        Station(id="2", name="Ghent-Sint-Pieters"),
    ]

    assert match_stations(stations, "bru") == [stations[0]]


def test_match_stations_returns_empty_list_when_no_station_matches() -> None:
    stations = [Station(id="1", name="Brussels-Central")]

    assert match_stations(stations, "aac") == []


def test_match_stations_checks_standard_name_too() -> None:
    stations = [
        Station(
            id="BE.NMBS.008813003",
            name="Brussels-Central",
            standard_name="Brussel-Centraal",
        )
    ]

    assert match_stations(stations, "centraal") == stations


if __name__ == "__main__":
    run_pytest_for_current_file(__file__)
