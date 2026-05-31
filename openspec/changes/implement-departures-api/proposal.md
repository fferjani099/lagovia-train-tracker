## Why

Lagovia needs a backend-only Track A API that lets callers search Belgian stations by partial name and see imminent train departures. Defining the contract first keeps the challenge implementation focused on the required endpoint, response shape, external iRail behavior, and submission documentation.

## What Changes

- Add a Python FastAPI backend endpoint: `GET /departures?q=<query>`.
- Return an explicit HTTP 400 error when `q` is missing or shorter than 3 characters.
- Search iRail stations by case-insensitive substring match on station names.
- Fetch live departures from matching stations using iRail liveboard data, using station ids where possible.
- Return only departures whose scheduled departure time is within the next 15 minutes.
- Convert iRail delay values to whole minutes in the API response.
- Group successful responses by station.
- Add documentation tasks for API shape, install/run instructions, trade-offs, known limitations, rough time spent, and AI usage.

## Capabilities

### New Capabilities

- `departures-api`: Backend API behavior for station search, iRail liveboard aggregation, validation errors, departure filtering, and grouped JSON responses.

### Modified Capabilities

- None.

## Impact

- New FastAPI application code and supporting modules for iRail access, station matching, response shaping, and time filtering.
- New tests for request validation, station matching, iRail client behavior, delay conversion, time-window filtering, grouped responses, and error paths.
- Updated README documentation and a new or updated `AI_USAGE.md`.
- Runtime dependencies remain aligned with the existing Python stack: FastAPI, Uvicorn, HTTPX, pytest, pytest-asyncio, and Ruff.
