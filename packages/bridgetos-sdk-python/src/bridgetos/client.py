"""HTTP client for the BridgetOS API."""

from __future__ import annotations

import os
from typing import Any

import httpx

from bridgetos.schema import Observation, ObservationResult

DEFAULT_BASE_URL = "https://api.bridgetos.com"
DEFAULT_TIMEOUT = 10.0


class BridgetOSError(Exception):
    """Base exception for BridgetOS client errors."""


class APIError(BridgetOSError):
    """The BridgetOS API returned an error response."""

    def __init__(self, status_code: int, message: str, body: Any = None) -> None:
        super().__init__(f"BridgetOS API error {status_code}: {message}")
        self.status_code = status_code
        self.body = body


class Client:
    """Synchronous client for the BridgetOS API.

    Args:
        api_key: API key issued by BridgetOS. Falls back to BRIDGETOS_API_KEY env var.
        base_url: Override the API base URL (e.g., for self-hosted deployments).
        timeout: Request timeout in seconds.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.api_key = api_key or os.environ.get("BRIDGETOS_API_KEY")
        if not self.api_key:
            raise BridgetOSError(
                "API key required. Pass api_key= or set BRIDGETOS_API_KEY env var."
            )
        self.base_url = (base_url or os.environ.get("BRIDGETOS_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self._http = httpx.Client(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "bridgetos-python/0.1.0",
            },
        )

    def observe(self, observation: Observation) -> ObservationResult:
        """Submit a single observation and return the scoring result.

        Args:
            observation: The observation to submit.

        Returns:
            ObservationResult with drift score, severity, and signed receipt.

        Raises:
            APIError: If the API returns an error response.
        """
        url = f"{self.base_url}/v1/agents/{observation.agent_id}/observe"
        response = self._http.post(url, json=observation.to_wire())
        return self._handle_response(response)

    def observe_batch(self, observations: list[Observation]) -> list[ObservationResult]:
        """Submit multiple observations in one request."""
        if not observations:
            return []
        agent_ids = {obs.agent_id for obs in observations}
        if len(agent_ids) > 1:
            raise BridgetOSError(
                "observe_batch requires all observations to share the same agent_id"
            )
        agent_id = agent_ids.pop()
        url = f"{self.base_url}/v1/agents/{agent_id}/observe/batch"
        response = self._http.post(
            url, json={"observations": [obs.to_wire() for obs in observations]}
        )
        if response.status_code >= 400:
            self._raise_for_status(response)
        body = response.json()
        return [ObservationResult.model_validate(r) for r in body.get("results", [])]

    def get_agent_state(self, agent_id: str) -> dict[str, Any]:
        """Fetch the current governance state and drift summary for an agent."""
        url = f"{self.base_url}/v1/agents/{agent_id}"
        response = self._http.get(url)
        if response.status_code >= 400:
            self._raise_for_status(response)
        return response.json()

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()

    def _handle_response(self, response: httpx.Response) -> ObservationResult:
        if response.status_code >= 400:
            self._raise_for_status(response)
        return ObservationResult.model_validate(response.json())

    def _raise_for_status(self, response: httpx.Response) -> None:
        body: Any = None
        message = response.reason_phrase or "request failed"
        try:
            body = response.json()
            if isinstance(body, dict) and "message" in body:
                message = body["message"]
        except Exception:
            body = response.text
        raise APIError(response.status_code, message, body)


class AsyncClient:
    """Async client for the BridgetOS API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.api_key = api_key or os.environ.get("BRIDGETOS_API_KEY")
        if not self.api_key:
            raise BridgetOSError(
                "API key required. Pass api_key= or set BRIDGETOS_API_KEY env var."
            )
        self.base_url = (base_url or os.environ.get("BRIDGETOS_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self._http = httpx.AsyncClient(
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "bridgetos-python/0.1.0",
            },
        )

    async def observe(self, observation: Observation) -> ObservationResult:
        url = f"{self.base_url}/v1/agents/{observation.agent_id}/observe"
        response = await self._http.post(url, json=observation.to_wire())
        if response.status_code >= 400:
            body: Any
            try:
                body = response.json()
                message = body.get("message", response.reason_phrase) if isinstance(body, dict) else response.reason_phrase
            except Exception:
                body = response.text
                message = response.reason_phrase
            raise APIError(response.status_code, message, body)
        return ObservationResult.model_validate(response.json())

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        await self.close()
