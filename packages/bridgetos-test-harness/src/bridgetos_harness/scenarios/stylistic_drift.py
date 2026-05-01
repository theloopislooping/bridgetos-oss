"""Stylistic drift scenario: writing style shifts (verbosity, formality)."""

from __future__ import annotations

from typing import Iterator

from bridgetos import Observation, ObservationContent, ObservationContext, ObservationTelemetry

from bridgetos_harness.scenarios.base import Scenario, ScenarioContext


SHORT_TERSE = [
    "Sure.",
    "Done.",
    "Got it.",
    "K.",
    "Refunded.",
    "Updated.",
]

LONG_VERBOSE = [
    "Absolutely, I would be more than delighted to assist you with this particular inquiry today, "
    "and I do want to take a moment to thank you for reaching out to our customer support team — "
    "we genuinely value the opportunity to make this right for you, and I'll do everything in my "
    "power to ensure that the resolution we arrive at is fully satisfactory and exceeds your "
    "expectations in every reasonable way.",
    "I deeply appreciate the patience you have demonstrated throughout this process, and rest "
    "assured that the matter you have raised will be given the absolute highest priority on my "
    "end, with full attention to detail and a thorough investigation of every relevant facet.",
]


class StylisticDrift(Scenario):
    """Writing style shifts over time — verbosity / formality drift.

    Should trigger drift on V1 stylometry (word length, punctuation, sentence length).
    """

    name = "stylistic_drift"
    description = "Verbosity and formality shifts. Should trigger stylometric drift."
    expected_drift = True

    def __init__(self, n: int = 25, mode: str = "verbose", seed: int | None = None) -> None:
        super().__init__(n=n, seed=seed)
        if mode not in {"verbose", "terse"}:
            raise ValueError("mode must be 'verbose' or 'terse'")
        self.mode = mode

    def generate(self, context: ScenarioContext) -> Iterator[Observation]:
        rng = context.rng()
        pool = LONG_VERBOSE if self.mode == "verbose" else SHORT_TERSE
        for i in range(self.n):
            text = rng.choice(pool)
            token_estimate = max(2, len(text.split()))
            yield Observation(
                agent_id=context.agent_id,
                session_id=context.session_id,
                timestamp=self.step_time(context.start_time, i),
                content=ObservationContent(text=text),
                context=ObservationContext(
                    task_type="customer_support",
                    model="claude-opus-4-7",
                    framework="bridgetos-harness",
                    tags=["stylistic_drift", self.mode],
                ),
                telemetry=ObservationTelemetry(
                    latency_ms=rng.uniform(500, 1500),
                    tokens_input=rng.randint(50, 200),
                    tokens_output=token_estimate,
                ),
            )
