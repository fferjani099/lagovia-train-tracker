## 1. Project Structure

- [ ] 1.1 Create the FastAPI application module and expose an app object for Uvicorn and tests
- [ ] 1.2 Create separate modules for iRail HTTP access, departure normalization, station matching, and time-window filtering
- [ ] 1.3 Add configuration constants for iRail base URL, request timeout, language/format parameters, and the 15-minute departure window

## 2. iRail Integration

- [ ] 2.1 Implement station retrieval from the iRail stations endpoint
- [ ] 2.2 Implement case-insensitive substring station matching against iRail station names
- [ ] 2.3 Implement liveboard retrieval for each matching station using station ids when available
- [ ] 2.4 Normalize iRail liveboard rows into train number, destination, scheduled departure time, and delay seconds
- [ ] 2.5 Convert delay seconds to whole delay minutes

## 3. API Behavior

- [ ] 3.1 Implement `GET /departures?q=<query>`
- [ ] 3.2 Return HTTP 400 with the exact `QUERY_TOO_SHORT` error body for missing or shorter-than-3-character queries
- [ ] 3.3 Filter normalized departures to scheduled times from request time through request time plus 15 minutes
- [ ] 3.4 Return successful responses grouped by station with `query`, `windowMinutes`, `generatedAt`, and `stations`
- [ ] 3.5 Include matching station groups with empty `departures` arrays when no departures are inside the window
- [ ] 3.6 Handle iRail request failures with a clear API error and bounded HTTP timeouts

## 4. Tests

- [ ] 4.1 Add endpoint tests for missing `q` and too-short `q` returning the exact HTTP 400 error body
- [ ] 4.2 Add station matching tests for case-insensitive substring matching and no-match behavior
- [ ] 4.3 Add iRail client tests using mocked HTTP responses for stations and liveboard data
- [ ] 4.4 Add time-window filtering tests with a fixed clock for inside, boundary, and outside departures
- [ ] 4.5 Add delay conversion tests from iRail seconds to response minutes
- [ ] 4.6 Add success response tests proving departures are grouped by station and empty station groups are preserved
- [ ] 4.7 Run `pytest` and `ruff` successfully

## 5. Documentation

- [ ] 5.1 Update README with install and local run instructions
- [ ] 5.2 Document the `GET /departures?q=<query>` success response and short-query error response
- [ ] 5.3 Document implementation decisions, trade-offs, known limitations, and rough time spent
- [ ] 5.4 Create or update `AI_USAGE.md` with AI tools used, representative prompts or plans, accepted output, rewritten output, and rejected output
