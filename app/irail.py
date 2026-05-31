from datetime import datetime, timezone
from typing import Any

import httpx

from app.config import (
    IRAIL_BASE_URL,
    IRAIL_FOLLOW_REDIRECTS,
    IRAIL_FORMAT,
    IRAIL_LANGUAGE,
    IRAIL_TIMEOUT_SECONDS,
    IRAIL_TRUST_ENV,
    IRAIL_USER_AGENT,
)
from app.models import RawDeparture, Station


class IRailError(Exception):
    """Raised when iRail cannot provide usable data."""


class IRailClient:
    def __init__(
        self,
        *,
        base_url: str = IRAIL_BASE_URL,
        timeout_seconds: float = IRAIL_TIMEOUT_SECONDS,
        language: str = IRAIL_LANGUAGE,
        response_format: str = IRAIL_FORMAT,
        follow_redirects: bool = IRAIL_FOLLOW_REDIRECTS,
        trust_env: bool = IRAIL_TRUST_ENV,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.language = language
        self.response_format = response_format
        self.follow_redirects = follow_redirects
        self.trust_env = trust_env
        self.http_client = http_client

    async def get_stations(self) -> list[Station]:
        data = await self._get(
            "/stations/",
            params={"format": self.response_format, "lang": self.language},
        )
        return [
            station
            for station in (_normalize_station(item) for item in _as_list(data.get("station")))
            if station is not None
        ]

    async def get_liveboard(self, station: Station) -> list[RawDeparture]:
        params = {
            "format": self.response_format,
            "lang": self.language,
            "arrdep": "departure",
            "alerts": "false",
        }

        if station.id:
            params["id"] = station.id
        else:
            params["station"] = station.name

        data = await self._get("/liveboard/", params=params)
        return normalize_liveboard_departures(data)

    async def _get(self, path: str, params: dict[str, str]) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = {"Accept": "application/json", "User-Agent": IRAIL_USER_AGENT}

        try:
            if self.http_client is not None:
                response = await self.http_client.get(
                    url,
                    params=params,
                    headers=headers,
                    follow_redirects=self.follow_redirects,
                )
            else:
                async with httpx.AsyncClient(
                    timeout=self.timeout_seconds,
                    follow_redirects=self.follow_redirects,
                    trust_env=self.trust_env,
                ) as client:
                    response = await client.get(url, params=params, headers=headers)

            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise IRailError("Unable to retrieve data from iRail.") from exc

        if not isinstance(data, dict):
            raise IRailError("iRail returned an unexpected response shape.")

        return data


def normalize_liveboard_departures(data: dict[str, Any]) -> list[RawDeparture]:
    departures_block = data.get("departures", {})
    if not isinstance(departures_block, dict):
        return []

    normalized: list[RawDeparture] = []
    for item in _as_list(departures_block.get("departure")):
        if not isinstance(item, dict):
            continue

        departure = _normalize_departure(item)
        if departure is not None:
            normalized.append(departure)

    return normalized


def _normalize_station(item: Any) -> Station | None:
    if not isinstance(item, dict):
        return None

    name = _string_or_none(item.get("name")) or _string_or_none(item.get("standardname"))
    if name is None:
        return None

    return Station(
        id=_string_or_none(item.get("id")),
        name=name,
        standard_name=_string_or_none(item.get("standardname")),
    )


def _normalize_departure(item: dict[str, Any]) -> RawDeparture | None:
    scheduled_departure_time = _parse_time(item.get("time"))
    train_number = _extract_train_number(item)
    destination = _extract_destination(item)

    if scheduled_departure_time is None or train_number is None or destination is None:
        return None

    return RawDeparture(
        train_number=train_number,
        destination=destination,
        scheduled_departure_time=scheduled_departure_time,
        delay_seconds=_int_or_zero(item.get("delay")),
    )


def _extract_train_number(item: dict[str, Any]) -> str | None:
    vehicle_info = item.get("vehicleinfo")
    if isinstance(vehicle_info, dict):
        short_name = _string_or_none(vehicle_info.get("shortname"))
        if short_name is not None:
            return short_name

        name = _string_or_none(vehicle_info.get("name"))
        if name is not None:
            return _strip_vehicle_prefix(name)

    vehicle = _string_or_none(item.get("vehicle"))
    if vehicle is None:
        return None

    return _strip_vehicle_prefix(vehicle)


def _extract_destination(item: dict[str, Any]) -> str | None:
    station = item.get("station")
    if isinstance(station, dict):
        name = _string_or_none(station.get("name"))
        if name is not None:
            return name
        standard_name = _string_or_none(station.get("standardname"))
        if standard_name is not None:
            return standard_name

    if isinstance(station, str) and station.strip():
        return station.strip()

    station_info = item.get("stationinfo")
    if isinstance(station_info, dict):
        return _string_or_none(station_info.get("name")) or _string_or_none(
            station_info.get("standardname")
        )

    return None


def _parse_time(value: Any) -> datetime | None:
    if isinstance(value, dict):
        value = value.get("time") or value.get("#text") or value.get("formatted")

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None

        if stripped.isdigit():
            return datetime.fromtimestamp(int(stripped), tz=timezone.utc)

        try:
            parsed = datetime.fromisoformat(stripped.replace("Z", "+00:00"))
        except ValueError:
            return None

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    return None


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _string_or_none(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def _int_or_zero(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _strip_vehicle_prefix(value: str) -> str:
    return value.removeprefix("BE.NMBS.").strip()
