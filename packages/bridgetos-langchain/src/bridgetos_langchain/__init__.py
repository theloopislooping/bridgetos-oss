"""LangChain integration for BridgetOS.

Adds a callback handler that automatically emits BridgetOS observations
from LangChain agent runs.

Usage:

    from langchain.agents import AgentExecutor
    from bridgetos_langchain import BridgetOSCallback

    callback = BridgetOSCallback(agent_id="support-bot-001")
    agent = AgentExecutor(..., callbacks=[callback])
    agent.invoke({"input": "Help me with my refund"})

Each LLM completion + tool call gets observed. If BridgetOS revokes the
agent's credential (governance_state == 'locked'), the callback raises
GovernanceLockedError to halt execution.
"""

from bridgetos_langchain.callback import BridgetOSCallback, GovernanceLockedError

__version__ = "0.1.0"
__all__ = ["BridgetOSCallback", "GovernanceLockedError"]
