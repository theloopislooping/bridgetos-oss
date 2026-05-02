"""Orchestrates scenario execution against a behavioral identity monitor."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Sequence

from bridgetos import Client

from bridgetos_harness.report import Report, ScenarioOutcome
from bridgetos_harness.scenarios.base import Scenario, ScenarioContext

logger = logging.getLogger(__name__)


class Runner:
    """Runs drift scenarios against a behavioral identity monitor.

    The runner submits each scenario's synthetic observations to the
    BridgetOS API and records the per-observation drift scores, severity,
    and governance state transitions. The resulting Report captures
    detection accuracy, latency to detection, and false-positive rate.

    Args:
        agent_id: Stable identifier for the synthetic agent. Each scenario
            uses this as its agent_id, so the API treats them as a single
            agent under different conditions.
        client: Pre-configured BridgetOS Client. If None, builds from env vars.
        dry_run: If True, generate observations but do not submit them to the API.
    """

    def __init__(
        self,
        agent_id: str,
        client: Client | None = None,
        dry_run: bool = False,
    ) -> None:
        self.agent_id = agent_id
        self.dry_run = dry_run
        if dry_run:
            self.client: Client | None = None
        else:
            self.client = client or Client()

    def run(self, scenarios: Sequence[Scenario], seed: int | None = None) -> Report:
        """Execute each scenario in order. Returns a consolidated Report."""
        outcomes: list[ScenarioOutcome] = []
        start_time = datetime.now(timezone.utc)
        for scenario in scenarios:
            outcome = self._run_one(scenario, start_time, seed)
            outcomes.append(outcome)
        return Report(agent_id=self.agent_id, outcomes=outcomes, started_at=start_time)

    def _run_one(
        self,
        scenario: Scenario,
        start_time: datetime,
        seed: int | None,
    ) -> ScenarioOutcome:
        session_id = f"harness-{uuid.uuid4().hex[:12]}"
        context = ScenarioContext(
            agent_id=self.agent_id,
            session_id=session_id,
            seed=seed if seed is not None else scenario.seed,
            start_time=start_time,
        )
        observations = list(scenario.generate(context))
        scores: list[float | None] = []
        severities: list[str | None] = []
        governance_states: list[str | None] = []
        first_detection_index: int | None = None

        for i, obs in enumerate(observations):
            if self.dry_run or self.client is None:
                scores.append(None)
                severities.append(None)
                governance_states.append(None)
                continue
            try:
                result = self.client.observe(obs)
            except Exception as exc:
                logger.warning("observe failed at i=%d: %s", i, exc)
                scores.append(None)
                severities.append(None)
                governance_states.append(None)
                continue
            scores.append(result.drift_score)
            severities.append(result.severity)
            governance_states.append(result.governance_state)
            if first_detection_index is None and result.severity not in (
                None,
                "normal",
            ):
                first_detection_index = i

        return ScenarioOutcome(
            scenario_name=scenario.name,
            scenario_description=scenario.description,
            expected_drift=scenario.expected_drift,
            n_observations=len(observations),
            drift_scores=scores,
            severities=severities,
            governance_states=governance_states,
            first_detection_index=first_detection_index,
            session_id=session_id,
        )
