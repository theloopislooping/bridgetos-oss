# bridgetos-langchain

LangChain integration for BridgetOS. Adds a callback that automatically emits observations from LangChain agent runs and halts execution if BridgetOS revokes the agent's credential.

## Install

```bash
pip install bridgetos-langchain
```

## Usage

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from bridgetos_langchain import BridgetOSCallback

callback = BridgetOSCallback(
    agent_id="support-bot-001",
    task_type="customer_support",
)

llm = ChatAnthropic(model="claude-opus-4-7")
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    callbacks=[callback],
)

executor.invoke({"input": "Help me with my refund"})
```

Each LLM completion plus any tool calls within that turn are submitted to BridgetOS as a single observation. If BridgetOS reports `governance_state == 'locked'`, the callback raises `GovernanceLockedError` to halt execution.

## Configuration

```python
BridgetOSCallback(
    agent_id="support-bot-001",
    session_id="user-session-abc",
    task_type="customer_support",
    halt_on_lock=True,        # raise on locked state (default True)
    log_errors=True,          # log API errors instead of failing (default True)
)
```

Pass `log_errors=False` to fail closed when BridgetOS is unreachable.

## License

MIT
