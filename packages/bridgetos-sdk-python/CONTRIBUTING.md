# Contributing to bridgetos-sdk-python

Published as the `bridgetos` package on PyPI.

## Setup

```bash
cd packages/bridgetos-sdk-python
uv sync --extra dev
```

## Test commands

```bash
# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/test_schema.py::test_observation_minimum_fields

# With coverage
uv run pytest --cov --cov-report=term-missing
```

## Lint and format

```bash
uv run ruff check src/
uv run ruff format src/
```

CI runs both as `--check` (no auto-fix). Fix locally before pushing.

## Public API surface

The public API is everything exported from `src/bridgetos/__init__.py`. Changes to this surface follow semantic versioning.

**Breaking changes — require a major version bump:**
- Removing or renaming any exported symbol (`Client`, `AsyncClient`, `Observation`, `ObservationResult`, etc.)
- Changing the type or removing any required constructor parameter
- Removing or renaming any field on `ObservationResult` (callers destructure these)
- Changing the HTTP method or path of any endpoint (`POST /v1/agents/{agent_id}/observe`, etc.)
- Changing how `governance_state == "locked"` is surfaced (callers gate on this)

**Non-breaking — patch or minor version:**
- Adding a new optional constructor parameter with a default
- Adding a new method to `Client` or `AsyncClient`
- Adding a new optional field to any Pydantic model
- Internal refactoring with no observable behavior change

## Architecture note

All Pydantic models use `extra="forbid"` — unknown fields raise on construction. `ObservationResult` uses `extra="ignore"` intentionally (the API may add fields the SDK doesn't know about yet). Keep this asymmetry intact.
