"""Base classes for drift scenarios."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterator

from bridgetos import Observation


@dataclass
class ScenarioContext:
    """Shared state passed to a scenario as it generates observations."""

    agent_id: str
    session_id: str
    seed: int
    start_time: datetime

    def rng(self) -> random.Random:
        return random.Random(self.seed)


class Scenario(ABC):
    """Base class for a labeled drift scenario.

    Each scenario produces a sequence of Observations representing
    synthetic agent behavior under a specific drift condition. The
    scenario also declares the expected drift signal so the harness
    can score detection accuracy.
    """

    name: str = "scenario"
    description: str = ""
    expected_drift: bool = False

    def __init__(self, n: int = 10, seed: int | None = None) -> None:
        self.n = n
        self.seed = seed if seed is not None else 0xB1D6E705

    def label(self) -> str:
        return self.name

    @abstractmethod
    def generate(self, context: ScenarioContext) -> Iterator[Observation]:
        """Yield n Observations for this scenario."""
        ...

    @staticmethod
    def step_time(start: datetime, i: int, seconds_apart: float = 1.0) -> datetime:
        return start + timedelta(seconds=i * seconds_apart)


def safe_choice(rng: random.Random, items: list[str]) -> str:
    return rng.choice(items) if items else ""
