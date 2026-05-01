"""bridgetos-harness — drift and failure-mode test harness for AI agents.

A Promptfoo-style evaluation harness that generates synthetic agent
behavior under known drift conditions and measures whether a behavioral
identity monitor (e.g., BridgetOS) detects them.

Use it to:
- Validate that your monitoring catches prompt injection
- Stress-test calibration windows
- Benchmark detection latency across drift types
- Generate ground-truth labeled drift scenarios for academic papers

Quick start:

    from bridgetos_harness import Runner, scenarios

    runner = Runner(agent_id="harness-test-001")
    report = runner.run([
        scenarios.Baseline(n=50),
        scenarios.PromptInjection(n=10, position=0.7),
        scenarios.SemanticDrift(n=30, drift_strength=0.5),
    ])
    print(report.summary())
"""

from bridgetos_harness import scenarios
from bridgetos_harness.runner import Runner
from bridgetos_harness.report import Report, ScenarioOutcome

__version__ = "0.1.0"
__all__ = ["Runner", "Report", "ScenarioOutcome", "scenarios"]
