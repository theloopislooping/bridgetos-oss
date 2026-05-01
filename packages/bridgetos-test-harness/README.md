# bridgetos-harness

Drift and failure-mode test harness for behavioral identity monitors of AI agents. Generates labeled synthetic agent behavior under known drift conditions and measures whether your monitor detects them.

Think of it as Promptfoo, but for runtime behavioral identity instead of prompt-time evaluation.

## Why this exists

Behavioral identity monitors claim to detect drift. This harness generates **ground-truth labeled drift** so you can verify those claims with numbers — false-positive rate, detection latency, accuracy across drift types — instead of vibes.

## Install

```bash
pip install bridgetos-harness
```

## Quick start

```bash
export BRIDGETOS_API_KEY=your-key

bridgetos-harness run \
    --agent-id harness-001 \
    --scenario baseline \
    --scenario prompt_injection \
    --scenario semantic_drift \
    --n 30 \
    --output report.json
```

## Programmatic usage

```python
from bridgetos_harness import Runner, scenarios

runner = Runner(agent_id="harness-001")
report = runner.run([
    scenarios.Baseline(n=50),
    scenarios.PromptInjection(n=20, position=0.6),
    scenarios.SemanticDrift(n=30, drift_strength=0.6),
    scenarios.ToolMisuse(n=20, misuse_rate=0.5),
    scenarios.StylisticDrift(n=25, mode="verbose"),
    scenarios.PersonaBreak(n=20, break_rate=0.4),
])

print(report.summary())
print(f"Accuracy: {report.accuracy():.1%}")
print(f"False-positive rate: {report.false_positive_rate():.1%}")
report.save("report.json")
```

## Available scenarios

| Scenario | Expected | Description |
|---|---|---|
| `Baseline` | normal | Stable customer-support agent. No drift. |
| `PromptInjection` | drift | Mid-session adversarial instructions. |
| `SemanticDrift` | drift | Gradual topic drift over time. |
| `ToolMisuse` | drift | Anomalous tool invocations. |
| `StylisticDrift` | drift | Verbosity / formality shifts. |
| `PersonaBreak` | drift | Agent breaks declared role. |

## Adding a custom scenario

```python
from bridgetos_harness.scenarios.base import Scenario, ScenarioContext
from bridgetos import Observation, ObservationContent

class MyScenario(Scenario):
    name = "my_scenario"
    description = "What this scenario tests"
    expected_drift = True

    def generate(self, context):
        for i in range(self.n):
            yield Observation(
                agent_id=context.agent_id,
                content=ObservationContent(text=f"Synthetic output {i}"),
            )
```

## What this harness does NOT do

It does not implement drift detection itself. It generates labeled inputs and submits them to a monitor (e.g., the BridgetOS API). The detection algorithm is the monitor's job — this harness validates whether the monitor catches what it should.

You can point it at any HTTP endpoint that accepts the BridgetOS observation schema, including a self-hosted reference implementation.

## License

Apache 2.0
