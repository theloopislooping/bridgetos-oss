# Contributing to bridgetos-test-harness

Synthetic drift scenario generator and CLI. Published as `bridgetos-harness` on PyPI.

## Setup

```bash
cd packages/bridgetos-test-harness
uv sync --extra dev
```

## Test commands

```bash
# Unit tests
uv run pytest

# Smoke test the CLI (no API key needed)
uv run bridgetos-harness run --agent-id test-001 --scenario baseline --n 5 --dry-run
```

## Adding a new drift scenario

### 1. Create the scenario file

Add `src/bridgetos_harness/scenarios/my_scenario.py`:

```python
from collections.abc import Iterator
from bridgetos_harness.scenarios.base import Scenario, ScenarioContext
from bridgetos import Observation

class MyScenario(Scenario):
    name = "my_scenario"
    description = "Short description of what this scenario tests."
    expected_drift = True  # or False for baseline-style scenarios

    def generate(self, context: ScenarioContext) -> Iterator[Observation]:
        for i in range(context.n):
            yield Observation(
                agent_id=context.agent_id,
                content={"text": f"observation {i}"},
            )
```

### 2. Register it

In `src/bridgetos_harness/scenarios/__init__.py`, add to the `SCENARIOS` dict:

```python
from .my_scenario import MyScenario

SCENARIOS = {
    ...
    "my_scenario": MyScenario,
}
```

### 3. Add tests

Add `tests/scenarios/test_my_scenario.py` that verifies:
- The scenario generates the expected number of observations for a given `n`.
- Each observation has the fields required by the BridgetOS schema.
- For `expected_drift=True` scenarios: the content is plausibly driftful (e.g., contains injected instructions, off-persona language, unexpected tool calls).
- For `expected_drift=False` scenarios: the content looks like normal baseline agent output.

## Scenario contract

- `expected_drift = True` — the observations this scenario generates must be the kind a well-calibrated behavioral monitor would flag. If a real BridgetOS API returns `severity == "normal"` for all of them, something is wrong with the scenario.
- `expected_drift = False` — baseline scenarios. Observations must look like normal agent operation and must not trigger drift alerts under normal conditions.
- `generate()` must be deterministic given the same `ScenarioContext`. Use `context.seed` to seed any random state.
