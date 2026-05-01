# bridgetos-python

Python SDK for the BridgetOS API.

## Install

```bash
pip install bridgetos
```

## Usage

```python
from bridgetos import Client, Observation, ObservationContent, ObservationContext

client = Client(api_key="your-key")

obs = Observation(
    agent_id="support-bot-001",
    content=ObservationContent(text="I can help with that refund request."),
    context=ObservationContext(
        task_type="customer_support",
        model="claude-opus-4-7",
        framework="langchain",
    ),
)

result = client.observe(obs)
print(f"drift={result.drift_score:.3f} severity={result.severity}")
if result.governance_state == "locked":
    raise RuntimeError("Agent identity revoked — halt execution")
```

### Async

```python
from bridgetos import AsyncClient, Observation, ObservationContent

async with AsyncClient() as client:
    result = await client.observe(
        Observation(
            agent_id="support-bot-001",
            content=ObservationContent(text="..."),
        )
    )
```

### Environment variables

- `BRIDGETOS_API_KEY` — API key (alternative to passing `api_key=`)
- `BRIDGETOS_BASE_URL` — Override the API base URL (for self-hosted deployments)

## What this package does

- Validates observations against the BridgetOS schema before sending
- Handles authentication, retries, and error mapping
- Returns drift scores, severity, governance state, and signed receipts

## What this package does NOT do

- Compute drift scores locally — those are computed by the BridgetOS API
- Implement the measurement architecture (vectors, horizons, governance state machine) — those are proprietary

## License

MIT
