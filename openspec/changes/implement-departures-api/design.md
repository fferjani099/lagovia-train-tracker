## Context

The repository is a small Python backend challenge for Track A. The application will expose a single FastAPI endpoint backed by iRail, using the stations endpoint to resolve station matches and the liveboard endpoint to load departures for each matching station.

The API must be simple enough to explain in a walkthrough, test without network access, and document clearly in the README. The existing dependency set already supports this approach with FastAPI, Uvicorn, HTTPX, pytest, pytest-asyncio, and Ruff.

## Goals / Non-Goals

**Goals:**

- Implement `GET /departures?q=<query>` with the exact short-query error contract.
- Query iRail stations, match station names by case-insensitive substring, and request liveboard data using station ids when available.
- Return a stable JSON response grouped by station.
- Filter departures by scheduled departure time within now plus 15 minutes.
- Convert iRail delay values from seconds to whole minutes.
- Keep iRail access isolated behind a small client so endpoint tests can mock external data.
- Document installation, running, response shape, trade-offs, limitations, time spent, and AI usage.

**Non-Goals:**

- Build a frontend or Track B experience.
- Implement fuzzy station search.
- Persist iRail data or introduce a database.
- Add authentication, rate limiting, or production deployment infrastructure.
- Guarantee live data availability when iRail is unavailable.

## Decisions

- Use FastAPI with an async HTTPX iRail client.
  - Rationale: FastAPI matches the requested stack and async HTTP calls keep multiple liveboard requests straightforward.
  - Alternative considered: synchronous requests. Rejected because it adds blocking behavior without simplifying the endpoint enough to matter.

- Model iRail as a separate client module.
  - Rationale: Station fetching, liveboard fetching, delay conversion, and response normalization are external-data concerns and should be testable without calling iRail.
  - Alternative considered: put HTTP calls directly in the route. Rejected because it would make endpoint tests brittle and harder to read.

- Use iRail station ids for liveboard requests when an id exists.
  - Rationale: Station ids are more stable than names and avoid ambiguity in liveboard lookups.
  - Alternative considered: request liveboard by station name. This can remain a fallback only if id data is missing.

- Return a grouped success envelope.
  - Shape:

```json
{
  "query": "Bru",
  "windowMinutes": 15,
  "generatedAt": "2026-05-31T13:00:00Z",
  "stations": [
    {
      "id": "BE.NMBS.008813003",
      "name": "Brussels-Central",
      "departures": [
        {
          "trainNumber": "IC 1234",
          "destination": "Antwerpen-Centraal",
          "scheduledDepartureTime": "2026-05-31T13:08:00Z",
          "delayMinutes": 4
        }
      ]
    }
  ]
}
```

  - Matching stations with no departures in the 15-minute window remain in the response with `departures: []`.
  - Alternative considered: a flat departure list with station fields repeated. Rejected because the requirement asks for grouping by station.

- Filter against scheduled departure time, not delayed departure time.
  - Rationale: The challenge explicitly says scheduled departure time within now plus 15 minutes.
  - Alternative considered: include delayed actual time in the window. Rejected because it changes the contract and may hide trains that are scheduled soon but delayed.

- Treat short or missing `q` as the same validation error.
  - Rationale: The user-facing contract says `q` must contain at least 3 characters, and missing input violates that rule.

## Risks / Trade-offs

- iRail response shapes may vary or fields may be missing -> Normalize defensively and skip malformed departure rows that cannot provide a scheduled time.
- Many station matches can cause many liveboard calls -> Keep the first implementation simple, then document this as a limitation and consider a cap or caching only if needed.
- Time-based filtering can make tests flaky -> Inject or isolate the clock in filtering logic so tests use a fixed `now`.
- iRail downtime or slow responses can make the API fail -> Configure HTTP timeouts and return a clear upstream error rather than hanging.
- Time zones can be confusing -> Normalize response timestamps to ISO 8601 and document the chosen timezone behavior.
