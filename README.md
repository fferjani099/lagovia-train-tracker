# Lagovia Train Tracker

## Project summary

This is a backend-only solution for the Lagovia Train Tracker challenge.

It exposes one API endpoint:

```text
GET /departures?q=<query>
```

The endpoint searches Belgian train stations using iRail and returns upcoming departures grouped by station. It only includes departures scheduled from now through the next 15 minutes.

## Tech stack

- Python
- FastAPI
- HTTPX
- Uvicorn
- pytest
- Ruff
- OpenSpec

## Why I chose Track A

I chose Track A because the challenge can be solved clearly with one backend endpoint.

This allowed me to focus on API design, data mapping, tests, and understanding the code instead of also building a frontend.

## How to install

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## How to run

Start the API locally:

```powershell
uvicorn app.main:app --reload --port 8001
```

Open the API docs in a browser:

```text
http://127.0.0.1:8001/docs
```

If port `8001` is already in use, choose another free port:

```powershell
uvicorn app.main:app --reload --port 8010
```

## Example request

```powershell
curl "http://127.0.0.1:8001/departures?q=Bru"
```

## Example success response

```json
{
  "query": "Bru",
  "windowMinutes": 15,
  "generatedAt": "2026-05-31T18:06:45Z",
  "stations": [
    {
      "id": "BE.NMBS.008813003",
      "name": "Brussels-Central",
      "departures": [
        {
          "trainNumber": "IC 3119",
          "destination": "Antwerp-Central",
          "scheduledDepartureTime": "2026-05-31T18:10:00Z",
          "delayMinutes": 0
        }
      ]
    }
  ]
}
```

The real response depends on live iRail data, so train times and delays will change.

## Example error response

Queries must contain at least 3 characters. A missing or too-short query returns HTTP 400:

```json
{
  "error": {
    "code": "QUERY_TOO_SHORT",
    "message": "Query parameter 'q' must contain at least 3 characters.",
    "minLength": 3
  }
}
```

If iRail cannot be reached, the API returns HTTP 502:

```json
{
  "error": {
    "code": "IRAIL_UNAVAILABLE",
    "message": "Unable to retrieve departure data from iRail."
  }
}
```

## How to run tests

Run the test suite:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Or, if your virtual environment is already active:

```powershell
python -m pytest
```

Run one test file:

```powershell
python -m pytest tests\test_api.py
```

The test files can also be run directly from an activated virtual environment:

```powershell
python tests\test_api.py
```

Run linting:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

Current local result:

- `19 passed`
- `ruff check .` passes

## Decisions and trade-offs

I chose Track A because the challenge can be solved clearly with one backend endpoint. This allowed me to focus on API design, data mapping, tests, and understanding the code.

I chose FastAPI because it is small, readable, and provides automatic API docs.

I used iRail station ids when fetching liveboards because ids are less ambiguous than names.

I did not implement fuzzy search because it was listed as a bonus and I prioritized the required behavior.

For broad queries, the endpoint may be slower because it needs to fetch liveboards for multiple matching stations and iRail has request limits.

I also made HTTPX ignore proxy environment variables by default. This avoids local failures when a machine has a broken `HTTP_PROXY` or `HTTPS_PROXY` value. If a real proxy is needed, start the app with `IRAIL_TRUST_ENV=true`.

## Known limitations

- No fuzzy search.
- No frontend.
- No persistent cache.
- Very broad queries can require several iRail liveboard requests.
- Delay is converted from iRail delay seconds to whole minutes.
- The app depends on live iRail availability.

## Roughly how long I spent

About 6 to 7 hours for reading the challenge, creating the OpenSpec change, implementing the API, writing tests, checking the endpoint manually, and updating documentation.

## AI usage

See [AI_USAGE.md](AI_USAGE.md).
