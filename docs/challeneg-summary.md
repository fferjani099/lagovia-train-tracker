# Lagovia Train Tracker - Challenge Summary

Build Track A: backend only.

Endpoint:
GET /departures?q=<query>

Requirements:
- If q is missing or shorter than 3 characters, return an explicit error response.
- Search stations whose name contains the query substring.
- Return upcoming departures from every matching station.
- Only include departures scheduled within the next 15 minutes from now.
- For each departure return:
  - train number
  - destination
  - scheduled departure time
  - current delay in minutes
- Return JSON.
- Document response shape.
- README must include install/run instructions, decisions/trade-offs/known limitations, roughly time spent.
- Include AI usage report.

Implementation choice:
- Track A
- Python
- FastAPI
- iRail API