"""LangChain callback that emits BridgetOS observations on each LLM/tool event."""

from __future__ import annotations

import logging
import time
from typing import Any
from uuid import UUID

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult

from bridgetos import (
    Client,
    Observation,
    ObservationContent,
    ObservationContext,
    ObservationTelemetry,
    ToolCall,
)

logger = logging.getLogger(__name__)


class GovernanceLockedError(RuntimeError):
    """Raised when BridgetOS has locked the agent's governance state."""

    def __init__(self, agent_id: str, drift_score: float | None) -> None:
        super().__init__(
            f"BridgetOS has locked agent {agent_id!r} (drift_score={drift_score}). "
            "Execution halted at governance layer."
        )
        self.agent_id = agent_id
        self.drift_score = drift_score


class BridgetOSCallback(BaseCallbackHandler):
    """LangChain callback that submits each LLM completion to BridgetOS.

    Args:
        agent_id: Stable identifier for the agent.
        client: Optional pre-configured BridgetOS Client. If not provided,
            a new client is constructed from environment variables.
        session_id: Optional session identifier to group related observations.
        task_type: Optional task type label (e.g., 'customer_support').
        halt_on_lock: If True (default), raise GovernanceLockedError when
            BridgetOS reports governance_state == 'locked'.
        log_errors: If True (default), log API errors but don't propagate them.
            Set False to fail closed when BridgetOS is unreachable.
    """

    def __init__(
        self,
        agent_id: str,
        client: Client | None = None,
        session_id: str | None = None,
        task_type: str | None = None,
        framework: str = "langchain",
        halt_on_lock: bool = True,
        log_errors: bool = True,
    ) -> None:
        super().__init__()
        self.agent_id = agent_id
        self.client = client or Client()
        self.session_id = session_id
        self.task_type = task_type
        self.framework = framework
        self.halt_on_lock = halt_on_lock
        self.log_errors = log_errors
        self._llm_starts: dict[UUID, float] = {}
        self._pending_tool_calls: list[ToolCall] = []

    # LangChain callback hooks ------------------------------------------------

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        self._llm_starts[run_id] = time.monotonic()

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        started = self._llm_starts.pop(run_id, None)
        latency_ms = (time.monotonic() - started) * 1000 if started else None

        text = self._extract_text(response)
        if not text:
            return

        usage = self._extract_token_usage(response)
        model = self._extract_model(response)

        observation = Observation(
            agent_id=self.agent_id,
            session_id=self.session_id,
            content=ObservationContent(
                text=text,
                tool_calls=self._pending_tool_calls,
            ),
            context=ObservationContext(
                task_type=self.task_type,
                model=model,
                framework=self.framework,
            ),
            telemetry=ObservationTelemetry(
                latency_ms=latency_ms,
                tokens_input=usage.get("input"),
                tokens_output=usage.get("output"),
            ),
        )
        self._pending_tool_calls = []
        self._submit(observation)

    def on_tool_end(
        self,
        output: str,
        *,
        run_id: UUID,
        name: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._pending_tool_calls.append(ToolCall(name=name or "unknown", result=output))

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        name: str | None = None,
        **kwargs: Any,
    ) -> None:
        self._pending_tool_calls.append(
            ToolCall(name=name or "unknown", error=str(error))
        )

    # Internals ---------------------------------------------------------------

    def _submit(self, observation: Observation) -> None:
        try:
            result = self.client.observe(observation)
        except Exception as exc:
            if self.log_errors:
                logger.warning("BridgetOS observe failed: %s", exc)
                return
            raise
        if self.halt_on_lock and result.governance_state == "locked":
            raise GovernanceLockedError(self.agent_id, result.drift_score)

    @staticmethod
    def _extract_text(response: LLMResult) -> str:
        try:
            generations = response.generations
            if generations and generations[0]:
                return generations[0][0].text
        except (AttributeError, IndexError):
            pass
        return ""

    @staticmethod
    def _extract_token_usage(response: LLMResult) -> dict[str, int | None]:
        usage = (
            (response.llm_output or {}).get("token_usage", {})
            if response.llm_output
            else {}
        )
        return {
            "input": usage.get("prompt_tokens") or usage.get("input_tokens"),
            "output": usage.get("completion_tokens") or usage.get("output_tokens"),
        }

    @staticmethod
    def _extract_model(response: LLMResult) -> str | None:
        if not response.llm_output:
            return None
        return response.llm_output.get("model_name") or response.llm_output.get("model")
