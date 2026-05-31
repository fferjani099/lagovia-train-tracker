## ADDED Requirements

### Requirement: Departures endpoint
The system SHALL expose `GET /departures?q=<query>` as the Track A backend API endpoint.

#### Scenario: Caller requests departures
- **WHEN** a caller sends `GET /departures?q=Bru`
- **THEN** the system responds with JSON for station groups matching the query

### Requirement: Query length validation
The system MUST reject a missing query or a query containing fewer than 3 non-whitespace characters with HTTP 400 and the exact documented error shape.

#### Scenario: Query is missing
- **WHEN** a caller sends `GET /departures` without `q`
- **THEN** the system responds with HTTP 400 and body `{"error":{"code":"QUERY_TOO_SHORT","message":"Query parameter 'q' must contain at least 3 characters.","minLength":3}}`

#### Scenario: Query is too short
- **WHEN** a caller sends `GET /departures?q=Br`
- **THEN** the system responds with HTTP 400 and body `{"error":{"code":"QUERY_TOO_SHORT","message":"Query parameter 'q' must contain at least 3 characters.","minLength":3}}`

### Requirement: Station search
The system SHALL retrieve all stations from the iRail stations endpoint and match stations whose names contain the query as a case-insensitive substring.

#### Scenario: Query matches station names by substring
- **WHEN** the iRail station list contains `Brussels-Central` and the caller queries `bru`
- **THEN** the station is included in the set of station groups to process

#### Scenario: Query has no station matches
- **WHEN** no iRail station name contains the query substring
- **THEN** the system responds with HTTP 200 and an empty `stations` array

### Requirement: Liveboard lookup
The system SHALL fetch departures for every matching station from the iRail liveboard endpoint and MUST use the iRail station id for liveboard lookup when one is available.

#### Scenario: Matching station has an id
- **WHEN** a matching station has id `BE.NMBS.008813003`
- **THEN** the system requests liveboard data for that station using the id

### Requirement: Departure time window
The system SHALL include only departures whose scheduled departure time is greater than or equal to the request time and less than or equal to 15 minutes after the request time.

#### Scenario: Departure is inside the window
- **WHEN** the request time is `2026-05-31T13:00:00Z` and a scheduled departure time is `2026-05-31T13:15:00Z`
- **THEN** the departure is included in the station group's `departures`

#### Scenario: Departure is outside the window
- **WHEN** the request time is `2026-05-31T13:00:00Z` and a scheduled departure time is `2026-05-31T13:16:00Z`
- **THEN** the departure is excluded from the station group's `departures`

### Requirement: Delay conversion
The system SHALL convert iRail departure delay values from seconds to whole minutes in the response.

#### Scenario: iRail delay is converted to minutes
- **WHEN** iRail returns a departure delay of `240` seconds
- **THEN** the API departure contains `"delayMinutes": 4`

### Requirement: Grouped success response
The system SHALL return successful responses grouped by station with the response fields `query`, `windowMinutes`, `generatedAt`, and `stations`.

#### Scenario: Matching station has upcoming departures
- **WHEN** a matching station has a departure in the 15-minute window
- **THEN** the station group contains `id`, `name`, and `departures`
- **AND** each departure contains `trainNumber`, `destination`, `scheduledDepartureTime`, and `delayMinutes`

#### Scenario: Matching station has no upcoming departures
- **WHEN** a station matches the query but has no departures in the 15-minute window
- **THEN** the station remains in the `stations` array with an empty `departures` array

### Requirement: Submission documentation
The project documentation MUST describe how to install and run the API, the response shapes, decisions, trade-offs, known limitations, rough time spent, and AI usage.

#### Scenario: Reader opens project documentation
- **WHEN** a reader opens the README and AI usage documentation
- **THEN** they can find local install and run instructions, API examples, documented trade-offs and limitations, rough time spent, AI tools used, representative prompts or plans, and notes about accepted, rewritten, and rejected AI output
