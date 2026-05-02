# Contributing to bridgetos-langchain

LangChain `BaseCallbackHandler` adapter. Published as `bridgetos-langchain` on PyPI.

## Setup

```bash
cd packages/bridgetos-langchain
uv sync --extra dev
```

## Test commands

```bash
uv run pytest
uv run pytest --cov --cov-report=term-missing
```

## Callback architecture

`BridgetOSCallback` follows a two-phase accumulate-then-flush pattern:

1. **Accumulate** — `on_tool_end` and `on_tool_error` append to `_pending_tool_calls`.
2. **Flush** — `on_llm_end` bundles the pending tool calls with the LLM output text into a single `Observation` and submits it via `Client.observe()`.

This produces **one `Observation` per LLM completion**, not one per tool call. Keep this invariant when adding new event hooks — tool-level events should accumulate; LLM-level events should flush.

If `observe()` returns `governance_state == "locked"`, the callback raises `GovernanceLockedError`. Callers must propagate this to halt agent execution.

## Adding new event hooks

1. Identify where in the LangChain callback lifecycle your event fires.
2. If the event is a tool-level event: accumulate into `_pending_tool_calls` or a similar buffer.
3. If the event is an LLM-completion event: flush the buffer and call `Client.observe()`.
4. Add a test that verifies the resulting `Observation` contains the expected content.

## Testing against a real LangChain agent

Set credentials and point at a local or staging API:

```bash
export BRIDGETOS_API_KEY=your-key
export BRIDGETOS_BASE_URL=https://api.bridgetos.com
```

Then run a short LangChain chain with `BridgetOSCallback` in the `callbacks` list and verify observations appear in the API.

For unit tests, construct the client with `dry_run=True` (or patch `Client.observe`) so no real HTTP calls are made.
