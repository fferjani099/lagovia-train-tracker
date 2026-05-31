from datetime import datetime, timezone

import httpx
import pytest

from _runner import run_pytest_for_current_file
from app.irail import IRailClient, IRailError, normalize_liveboard_departures
from app.models import Station


def test_irail_client_defaults_to_versioned_api_and_ignores_proxy_env() -> None:
    client = IRailClient()

    assert client.base_url == "https://api.irail.be/v1"
    assert client.follow_redirects is True
    assert client.trust_env is False


@pytest.mark.asyncio
async def test_get_stations_fetches_and_normalizes_irail_stations() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/stations/"
        assert request.url.params["format"] == "json"
        assert request.url.params["lang"] == "en"
        return httpx.Response(
            200,
            json={
                "station": [
                    {
                        "id": "BE.NMBS.008813003",
                        "name": "Brussels-Central",
                        "standardname": "Brussel-Centraal",
                    }
                ]
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = IRailClient(http_client=http_client)

        stations = await client.get_stations()

    assert stations == [
        Station(
            id="BE.NMBS.008813003",
            name="Brussels-Central",
            standard_name="Brussel-Centraal",
        )
    ]


@pytest.mark.asyncio
async def test_get_liveboard_uses_station_id_and_normalizes_departures() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/liveboard/"
        assert request.url.params["id"] == "BE.NMBS.008813003"
        assert "station" not in request.url.params
        assert request.url.params["arrdep"] == "departure"
        assert request.url.params["alerts"] == "false"
        return httpx.Response(
            200,
            json={
                "departures": {
                    "number": 1,
                    "departure": [
                        {
                            "delay": 240,
                            "station": "Antwerp-Central",
                            "time": 1780232880,
                            "vehicle": "BE.NMBS.IC1234",
                            "vehicleinfo": {"shortname": "IC1234"},
                        }
                    ],
                }
            },
        )

    station = Station(id="BE.NMBS.008813003", name="Brussels-Central")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = IRailClient(http_client=http_client)

        departures = await client.get_liveboard(station)

    assert len(departures) == 1
    assert departures[0].train_number == "IC1234"
    assert departures[0].destination == "Antwerp-Central"
    assert departures[0].scheduled_departure_time == datetime(
        2026,
        5,
        31,
        13,
        8,
        tzinfo=timezone.utc,
    )
    assert departures[0].delay_seconds == 240


@pytest.mark.asyncio
async def test_get_liveboard_falls_back_to_station_name_when_id_is_missing() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["station"] == "Brussels-Central"
        assert "id" not in request.url.params
        return httpx.Response(200, json={"departures": {"number": 0}})

    station = Station(id=None, name="Brussels-Central")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = IRailClient(http_client=http_client)

        departures = await client.get_liveboard(station)

    assert departures == []


@pytest.mark.asyncio
async def test_irail_http_failure_raises_irail_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "unavailable"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = IRailClient(http_client=http_client)

        with pytest.raises(IRailError):
            await client.get_stations()


def test_normalize_liveboard_departures_skips_unusable_rows() -> None:
    data = {
        "departures": {
            "departure": [
                {"delay": 0, "station": "Antwerp-Central", "vehicle": "IC1234"},
                {
                    "delay": "60",
                    "stationinfo": {"name": "Ghent"},
                    "time": "1780232880",
                    "vehicle": "BE.NMBS.IC4321",
                },
            ]
        }
    }

    departures = normalize_liveboard_departures(data)

    assert len(departures) == 1
    assert departures[0].train_number == "IC4321"
    assert departures[0].destination == "Ghent"


if __name__ == "__main__":
    run_pytest_for_current_file(__file__)
