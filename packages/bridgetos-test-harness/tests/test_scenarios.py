"""Tests for the test harness scenarios."""

from datetime import datetime, timezone

from bridgetos_harness import scenarios
from bridgetos_harness.runner import Runner
from bridgetos_harness.scenarios.base import ScenarioContext


def _ctx() -> ScenarioContext:
    return ScenarioContext(
        agent_id="t",
        session_id="s",
        seed=42,
        start_time=datetime(2026, 5, 1, tzinfo=timezone.utc),
    )


def test_baseline_yields_n_observations():
    s = scenarios.Baseline(n=10)
    out = list(s.generate(_ctx()))
    assert len(out) == 10
    assert all(o.agent_id == "t" for o in out)


def test_prompt_injection_has_injected_tag_in_back_half():
    s = scenarios.PromptInjection(n=20, position=0.5)
    out = list(s.generate(_ctx()))
    front = out[:10]
    back = out[10:]
    assert all("pre_injection" in (o.context.tags if o.context else []) for o in front)
    assert all("injected" in (o.context.tags if o.context else []) for o in back)


def test_semantic_drift_progresses():
    s = scenarios.SemanticDrift(n=30, drift_strength=1.0)
    out = list(s.generate(_ctx()))
    assert len(out) == 30


def test_dry_run_runner_does_not_call_api():
    runner = Runner(agent_id="t", dry_run=True)
    report = runner.run([scenarios.Baseline(n=5), scenarios.PromptInjection(n=5)])
    assert len(report.outcomes) == 2
    assert report.outcomes[0].n_observations == 5
    assert all(s is None for s in report.outcomes[0].drift_scores)


def test_all_scenarios_have_expected_drift_set():
    for name in ["baseline", "prompt_injection", "semantic_drift", "tool_misuse", "stylistic_drift", "persona_break"]:
        cls = getattr(scenarios, "".join(p.capitalize() for p in name.split("_")))
        instance = cls(n=2)
        assert hasattr(instance, "expected_drift")
        assert isinstance(instance.expected_drift, bool)
