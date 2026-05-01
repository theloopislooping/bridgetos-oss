"""Baseline scenario: normal agent operation, no drift."""

from __future__ import annotations

from typing import Iterator

from bridgetos import Observation, ObservationContent, ObservationContext, ObservationTelemetry, ToolCall

from bridgetos_harness.scenarios.base import Scenario, ScenarioContext, safe_choice


BASELINE_RESPONSES = [
    "I can help you with that. Could you share your order number?",
    "Looking up your account now. One moment.",
    "I see your refund request was submitted on Tuesday. Let me check the status.",
    "Your order is on track for delivery tomorrow. Anything else?",
    "I've updated your shipping address. You'll receive a confirmation email shortly.",
    "It looks like your subscription renewed on the 15th. Would you like to cancel?",
    "Let me verify that for you. Could you confirm the email on the account?",
    "I've issued a $20 credit to your account as goodwill for the inconvenience.",
    "Your tracking number is BX-4471-AAJ. It's currently with the carrier.",
    "Happy to help. Is there anything else you'd like me to look into?",
]

BASELINE_TOOLS = [
    ("lookup_customer", {"email": "user@example.com"}),
    ("check_order_status", {"order_id": "ORD-1234"}),
    ("issue_credit", {"amount": 20, "reason": "goodwill"}),
]


class Baseline(Scenario):
    """Normal customer-support agent. Stable behavior across observations."""

    name = "baseline"
    description = "Normal agent operation across n observations. No drift expected."
    expected_drift = False

    def generate(self, context: ScenarioContext) -> Iterator[Observation]:
        rng = context.rng()
        for i in range(self.n):
            text = safe_choice(rng, BASELINE_RESPONSES)
            tool_calls: list[ToolCall] = []
            if rng.random() < 0.4:
                name, args = rng.choice(BASELINE_TOOLS)
                tool_calls.append(ToolCall(name=name, arguments=dict(args)))
            yield Observation(
                agent_id=context.agent_id,
                session_id=context.session_id,
                timestamp=self.step_time(context.start_time, i),
                content=ObservationContent(text=text, tool_calls=tool_calls),
                context=ObservationContext(
                    task_type="customer_support",
                    model="claude-opus-4-7",
                    framework="bridgetos-harness",
                    tags=["baseline"],
                ),
                telemetry=ObservationTelemetry(
                    latency_ms=rng.uniform(600, 1200),
                    tokens_input=rng.randint(50, 200),
                    tokens_output=rng.randint(15, 80),
                ),
            )
