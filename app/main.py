import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi

from app.config import DEPARTURE_WINDOW_MINUTES, QUERY_MIN_LENGTH
from app.departures import (
    departure_to_response,
    filter_by_departure_window,
    isoformat_z,
    utc_now,
)
from app.irail import IRailClient, IRailError
from app.responses import UTF8JSONResponse
from app.schemas import (
    DeparturesResponse,
    ShortQueryErrorResponse,
    UpstreamErrorResponse,
)
from app.stations import match_stations


logger = logging.getLogger(__name__)


SHORT_QUERY_ERROR = {
    "error": {
        "code": "QUERY_TOO_SHORT",
        "message": "Query parameter 'q' must contain at least 3 characters.",
        "minLength": QUERY_MIN_LENGTH,
    }
}

IRAIL_UNAVAILABLE_ERROR = {
    "error": {
        "code": "IRAIL_UNAVAILABLE",
        "message": "Unable to retrieve departure data from iRail.",
    }
}


def create_app(
    *,
    irail_client: IRailClient | None = None,
    now_provider: Callable[[], datetime] | None = None,
) -> FastAPI:
    app = FastAPI(
        title="Lagovia Train Tracker",
        default_response_class=UTF8JSONResponse,
    )
    app.state.irail_client = irail_client or IRailClient()
    app.state.now_provider = now_provider or utc_now

    @app.get(
        "/departures",
        response_model=DeparturesResponse,
        response_class=UTF8JSONResponse,
        responses={
            400: {
                "model": ShortQueryErrorResponse,
                "description": "Query is missing or shorter than 3 characters.",
            },
            502: {
                "model": UpstreamErrorResponse,
                "description": "Unable to retrieve departure data from iRail.",
            },
        },
    )
    async def get_departures(
        request: Request,
        q: str | None = None,
    ) -> dict[str, Any] | UTF8JSONResponse:
        query = (q or "").strip()
        if len(query) < QUERY_MIN_LENGTH:
            return UTF8JSONResponse(status_code=400, content=SHORT_QUERY_ERROR)

        generated_at = request.app.state.now_provider()
        client: IRailClient = request.app.state.irail_client

        try:
            stations = await client.get_stations()
            matching_stations = match_stations(stations, query)
            station_groups = []

            for station in matching_stations:
                departures = await client.get_liveboard(station)
                upcoming_departures = filter_by_departure_window(
                    departures,
                    generated_at,
                    DEPARTURE_WINDOW_MINUTES,
                )
                station_groups.append(
                    {
                        "id": station.id,
                        "name": station.name,
                        "departures": [
                            departure_to_response(departure)
                            for departure in upcoming_departures
                        ],
                    }
                )
        except IRailError:
            logger.exception("Unable to retrieve departure data from iRail")
            return UTF8JSONResponse(status_code=502, content=IRAIL_UNAVAILABLE_ERROR)

        return {
            "query": query,
            "windowMinutes": DEPARTURE_WINDOW_MINUTES,
            "generatedAt": isoformat_z(generated_at),
            "stations": station_groups,
        }

    app.openapi = lambda: _custom_openapi(app)
    return app


def _custom_openapi(app: FastAPI) -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    schema["paths"]["/departures"]["get"]["responses"].pop("422", None)
    app.openapi_schema = schema
    return app.openapi_schema


app = create_app()
