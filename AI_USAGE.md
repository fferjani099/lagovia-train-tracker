# AI Usage Report

## Tools used

- ChatGPT: planning, choosing track/tooling, and understanding the challenge.
- Codex in VS Code: generating and editing code, tests, README, and AI_USAGE.md.
- OpenSpec: structuring the implementation with proposal, spec, design, and tasks.

## Representative prompts

1. "Create an OpenSpec change for Track A using FastAPI..."
2. "Implement GET /departures?q=... using iRail..."
3. "Add tests for short query validation, 15-minute filtering, and delay conversion..."
4. "Write a README with install/run instructions and trade-offs..."

## What I accepted as-is

- Some FastAPI boilerplate.
- Basic Pydantic response models.
- Some test structure.

## What I rewrote or adjusted

- The API response shape.
- The error response shape.
- README wording.
- Some service logic to make sure I understood the filtering.
- iRail HTTP client settings after local testing showed proxy environment variables could break requests.

## What I rejected

- Frontend/React implementation.
- Fuzzy search.
- Extra features outside the requirements.

## Verification

- Ran the app locally with Uvicorn.
- Tested the endpoint manually with curl and FastAPI docs.
- Ran pytest.
- Ran Ruff.
- Reviewed generated code before committing.
