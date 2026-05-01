"""BridgetOS Python SDK.

Send observations from autonomous AI agents to the BridgetOS API for
behavioral identity monitoring.

Basic usage:

    from bridgetos import Client, Observation

    client = Client(api_key="your-key")

    obs = Observation(
        agent_id="my-agent",
        content={"text": "The agent's output"},
    )
    result = client.observe(obs)
    print(result.drift_score, result.severity)
"""

from bridgetos.client import AsyncClient, Client
from bridgetos.schema import (
    Observation,
    ObservationContent,
    ObservationContext,
    ObservationResult,
    ObservationTelemetry,
    ToolCall,
)

__version__ = "0.1.0"
__all__ = [
    "Client",
    "AsyncClient",
    "Observation",
    "ObservationContent",
    "ObservationContext",
    "ObservationTelemetry",
    "ObservationResult",
    "ToolCall",
]
