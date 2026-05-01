"""Reporting for scenario runs."""

from __future__ import annotations

import json
import statistics
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ScenarioOutcome:
    """The result of executing a single scenario."""

    scenario_name: str
    scenario_description: str
    expected_drift: bool
    n_observations: int
    drift_scores: list[float | None]
    severities: list[str | None]
    governance_states: list[str | None]
    first_detection_index: int | None
    session_id: str

    def detected(self) -> bool:
        return self.first_detection_index is not None

    def correct(self) -> bool:
        """Did the monitor classify this scenario correctly?"""
        return self.detected() == self.expected_drift

    def max_drift_score(self) -> float | None:
        scores = [s for s in self.drift_scores if s is not None]
        return max(scores) if scores else None

    def mean_drift_score(self) -> float | None:
        scores = [s for s in self.drift_scores if s is not None]
        return statistics.fmean(scores) if scores else None

    def detection_latency(self) -> int | None:
        """How many observations until detection. None if never detected."""
        return self.first_detection_index

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "detected": self.detected(),
            "correct": self.correct(),
            "max_drift_score": self.max_drift_score(),
            "mean_drift_score": self.mean_drift_score(),
            "detection_latency": self.detection_latency(),
        }


@dataclass
class Report:
    """Summary across multiple scenarios."""

    agent_id: str
    outcomes: list[ScenarioOutcome]
    started_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        lines = [
            f"Run summary for agent {self.agent_id}",
            f"Started: {self.started_at.isoformat()}",
            f"Scenarios: {len(self.outcomes)}",
            "",
            f"{'Scenario':<22} {'Expected':<10} {'Detected':<10} {'Correct':<10} {'MaxDrift':<10} {'Latency':<10}",
            "-" * 78,
        ]
        for outcome in self.outcomes:
            max_drift = outcome.max_drift_score()
            latency = outcome.detection_latency()
            lines.append(
                f"{outcome.scenario_name:<22} "
                f"{'drift' if outcome.expected_drift else 'normal':<10} "
                f"{'yes' if outcome.detected() else 'no':<10} "
                f"{'yes' if outcome.correct() else 'NO':<10} "
                f"{f'{max_drift:.3f}' if max_drift is not None else '-':<10} "
                f"{str(latency) if latency is not None else '-':<10}"
            )
        accuracy = self.accuracy()
        lines.append("-" * 78)
        lines.append(f"Detection accuracy: {accuracy:.1%}")
        false_pos = self.false_positive_rate()
        false_neg = self.false_negative_rate()
        if false_pos is not None:
            lines.append(f"False positive rate: {false_pos:.1%}")
        if false_neg is not None:
            lines.append(f"False negative rate: {false_neg:.1%}")
        return "\n".join(lines)

    def accuracy(self) -> float:
        if not self.outcomes:
            return 0.0
        correct = sum(1 for o in self.outcomes if o.correct())
        return correct / len(self.outcomes)

    def false_positive_rate(self) -> float | None:
        normal = [o for o in self.outcomes if not o.expected_drift]
        if not normal:
            return None
        return sum(1 for o in normal if o.detected()) / len(normal)

    def false_negative_rate(self) -> float | None:
        drift = [o for o in self.outcomes if o.expected_drift]
        if not drift:
            return None
        return sum(1 for o in drift if not o.detected()) / len(drift)

    def to_json(self) -> str:
        payload = {
            "agent_id": self.agent_id,
            "started_at": self.started_at.isoformat(),
            "metadata": self.metadata,
            "accuracy": self.accuracy(),
            "false_positive_rate": self.false_positive_rate(),
            "false_negative_rate": self.false_negative_rate(),
            "outcomes": [o.to_dict() for o in self.outcomes],
        }
        return json.dumps(payload, indent=2, default=str)

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            f.write(self.to_json())
