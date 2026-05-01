"""Pydantic models matching the BridgetOS observation schema v1."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolCall(BaseModel):
    """A tool invocation within an observation."""

    model_config = ConfigDict(extra="forbid")

    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: Any | None = None
    error: str | None = None


class MemoryOps(BaseModel):
    """Memory read/write operations within an observation."""

    model_config = ConfigDict(extra="forbid")

    reads: list[str] = Field(default_factory=list)
    writes: list[str] = Field(default_factory=list)


class ObservationContent(BaseModel):
    """The agent's output content for a single observation."""

    model_config = ConfigDict(extra="forbid")

    text: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    memory: MemoryOps | None = None


class ObservationContext(BaseModel):
    """Contextual metadata about the deployment context."""

    model_config = ConfigDict(extra="forbid")

    task_type: str | None = None
    prompt: str | None = None
    model: str | None = None
    framework: str | None = None
    tags: list[str] = Field(default_factory=list, max_length=32)


class ObservationTelemetry(BaseModel):
    """Operational telemetry for the observation."""

    model_config = ConfigDict(extra="forbid")

    latency_ms: float | None = Field(default=None, ge=0)
    tokens_input: int | None = Field(default=None, ge=0)
    tokens_output: int | None = Field(default=None, ge=0)
    error: str | None = None
    retries: int | None = Field(default=None, ge=0)


class Observation(BaseModel):
    """A single observation of an autonomous AI agent's output.

    This is the canonical input to the BridgetOS behavioral identity
    monitoring pipeline. Each observation associates an agent's output
    text (and optional tool calls / memory operations) with the agent's
    identifier, a timestamp, and contextual metadata.
    """

    model_config = ConfigDict(extra="forbid")

    agent_id: str = Field(min_length=1, max_length=256)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    session_id: str | None = Field(default=None, max_length=256)
    schema_version: str = "1.0"
    content: ObservationContent
    context: ObservationContext | None = None
    telemetry: ObservationTelemetry | None = None

    def to_wire(self) -> dict[str, Any]:
        """Serialize to the JSON shape expected by the BridgetOS API."""
        return self.model_dump(mode="json", exclude_none=True)


class ObservationResult(BaseModel):
    """Response returned by the BridgetOS API after submitting an observation."""

    model_config = ConfigDict(extra="ignore")

    observation_id: str
    drift_score: float | None = None
    severity: str | None = None  # 'normal', 'watchlist', 'review', 'locked'
    is_calibrated: bool = False
    governance_state: str | None = None
    receipt: dict[str, Any] | None = None  # signature, hash, keyId
