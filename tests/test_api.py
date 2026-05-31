from datetime import datetime, timedelta, timezone

import httpx
import pytest

from _runner import run_pytest_for_current_file
from app.irail import IRailError
from app.main import create_app
from app.models import RawDeparture, Station


FIXED_NOW = datetime(2026, 5, 31, 13, 0, tzinfo=timezone.utc)
SHORT_QUERY_ERROR = {
    "error": {
        "code": "QUERY_TOO_SHORT",
        "message": "Query parameter 'q' must contain at least 3 characters.",
        "minLength": 3,
    }
}


class FakeIRailClient:
    def __init__(
        self,
        *,
        stations: list[Station] | None = None,
        liveboards: dict[str, list[RawDeparture]] | None = None,
        fail: bool = False,
    ) -> None:
        self.stations = stations or []
        self.liveboards = liveboards or {}
        self.fail = fail
        self.liveboard_calls: list[str] = []
        self.stations_called = False

    async def get_stations(self) -> list[Station]:
        self.stations_called = True
        if self.fail:
            raise IRailError("iRail unavailable")
        return self.stations

    async def get_liveboard(self, station: Station) -> list[RawDeparture]:
        key = station.id or station.name
        self.liveboard_calls.append(key)
        if self.fail:
            raise IRailError("iRail unavailable")
        return self.liveboards.get(key, [])


async def get_json(path: str, fake_client: FakeIRailClient) -> httpx.Response:
    app = create_app(irail_client=fake_client, now_provider=lambda: FIXED_NOW)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.get(path)


async def get_app_json(path: str, fake_client: FakeIRailClient) -> httpx.Response:
    app = create_app(irail_client=fake_client, now_provider=lambda: FIXED_NOW)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.get(path)


@pytest.mark.asyncio
async def test_missing_query_returns_exact_short_query_error() -> None:
    fake_client = FakeIRailClient()

    response = await get_json("/departures", fake_client)

    assert response.status_code == 400
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    assert response.json() == SHORT_QUERY_ERROR
    assert fake_client.stations_called is False


@pytest.mark.asyncio
async def test_too_short_query_returns_exact_short_query_error() -> None:
    fake_client = FakeIRailClient()

    response = await get_json("/departures?q=Br", fake_client)

    assert response.status_code == 400
    assert response.json() == SHORT_QUERY_ERROR
    assert fake_client.stations_called is False


@pytest.mark.asyncio
async def test_success_response_is_grouped_and_filtered_by_station() -> None:
    brussels = Station(id="BE.NMBS.008813003", name="Brussels-Central")
    bruges = Station(id="BE.NMBS.008891009", name="Bruges")
    outside_window = RawDeparture(
        train_number="IC9999",
        destination="Ghent",
        scheduled_departure_time=FIXED_NOW + timedelta(minutes=16),
        delay_seconds=60,
    )
    inside_window = RawDeparture(
        train_number="IC1234",
        destination="Antwerp-Central",
        scheduled_departure_time=FIXED_NOW + timedelta(minutes=8),
        delay_seconds=240,
    )
    fake_client = FakeIRailClient(
        stations=[brussels, bruges],
        liveboards={
            "BE.NMBS.008813003": [inside_window, outside_window],
            "BE.NMBS.008891009": [],
        },
    )

    response = await get_json("/departures?q=Bru", fake_client)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    assert response.json() == {
        "query": "Bru",
        "windowMinutes": 15,
        "generatedAt": "2026-05-31T13:00:00Z",
        "stations": [
            {
                "id": "BE.NMBS.008813003",
                "name": "Brussels-Central",
                "departures": [
                    {
                        "trainNumber": "IC1234",
                        "destination": "Antwerp-Central",
                        "scheduledDepartureTime": "2026-05-31T13:08:00Z",
                        "delayMinutes": 4,
                    }
                ],
            },
            {
                "id": "BE.NMBS.008891009",
                "name": "Bruges",
                "departures": [],
            },
        ],
    }
    assert fake_client.liveboard_calls == [
        "BE.NMBS.008813003",
        "BE.NMBS.008891009",
    ]


@pytest.mark.asyncio
async def test_no_station_matches_returns_empty_station_list() -> None:
    fake_client = FakeIRailClient(
        stations=[Station(id="BE.NMBS.008892007", name="Ghent-Sint-Pieters")]
    )

    response = await get_json("/departures?q=Bru", fake_client)

    assert response.status_code == 200
    assert response.json()["stations"] == []
    assert fake_client.liveboard_calls == []


@pytest.mark.asyncio
async def test_irail_failure_returns_clear_api_error() -> None:
    fake_client = FakeIRailClient(fail=True)

    response = await get_json("/departures?q=Bru", fake_client)

    assert response.status_code == 502
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    assert response.json() == {
        "error": {
            "code": "IRAIL_UNAVAILABLE",
            "message": "Unable to retrieve departure data from iRail.",
        }
    }


@pytest.mark.asyncio
async def test_openapi_documents_departures_responses_without_default_422() -> None:
    fake_client = FakeIRailClient()

    response = await get_app_json("/openapi.json", fake_client)

    assert response.status_code == 200
    responses = response.json()["paths"]["/departures"]["get"]["responses"]
    media_type = "application/json; charset=utf-8"
    assert responses["200"]["content"][media_type]["schema"]["$ref"].endswith(
        "/DeparturesResponse"
    )
    assert responses["400"]["content"][media_type]["schema"]["$ref"].endswith(
        "/ShortQueryErrorResponse"
    )
    assert responses["502"]["content"][media_type]["schema"]["$ref"].endswith(
        "/UpstreamErrorResponse"
    )
    assert "422" not in responses


if __name__ == "__main__":
    run_pytest_for_current_file(__file__)
