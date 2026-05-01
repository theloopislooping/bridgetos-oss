# Getting Started

This monorepo holds the open-source integration layer for BridgetOS — the runtime behavioral identity platform for autonomous AI agents.

## What's open source

- **bridgetos-schema** — the observation data contract (JSON Schema)
- **bridgetos-sdk-python** — Python client for the BridgetOS API
- **bridgetos-langchain** — LangChain callback integration
- **bridgetos-test-harness** — drift scenario generator for stress-testing identity monitors

## What's not open source

The BridgetOS analytic core is proprietary and runs as a hosted service. What stays closed:

- The scoring algorithms, vector weights, and calibration parameters
- The threshold logic and decision boundaries
- The implementation of the governance state machine
- Cryptographic credential issuance and revocation
- The integrated runtime that ties everything together

The high-level architecture — the Horizon-Defined Identity Tensor (HDIT), multi-vector behavioral monitoring across temporal horizons, governance state classification, and derivative detection — is described in our patent filings: US Patent App. 19/651,602 and HDIT Provisional 64/002,373. The architectural concepts are publicly readable; the implementations and parameters are not.

This split is intentional: the integration surface is open so the ecosystem can adopt it freely; the implementation of the analytic core stays closed because that's the work product, the operational know-how, and the patent-protected execution.

## A typical setup

```
┌──────────────────────────┐         ┌──────────────────────────────┐
│  Your LangChain agent    │         │  BridgetOS API (proprietary)  │
│                          │         │                                │
│  ┌────────────────────┐  │  POST   │  - Score observations          │
│  │ BridgetOSCallback  ├──┼────────►│  - Compute drift across vectors│
│  └────────────────────┘  │         │  - Track temporal horizons     │
│        (open source)     │         │  - Sign + hash-chain receipts  │
└──────────────────────────┘         │  - Issue / revoke credentials  │
                                     │  - Trigger governance state    │
                                     └──────────────────────────────┘
```

The open-source pieces handle the integration. The closed core handles the measurement, governance, and cryptography.

## Building a custom adapter

If you use a framework not yet covered (CrewAI, AutoGen, OpenAI Agents SDK, etc.), the pattern is:

1. Hook into your framework's per-step callback
2. On each agent output, build an `Observation` (see `bridgetos-schema`)
3. Submit via `bridgetos-sdk-python`'s `Client.observe()`
4. If the result indicates `governance_state == "locked"`, halt execution

PRs for new framework adapters welcome.

## Validating a monitor

If you're building or evaluating a behavioral identity monitor, use `bridgetos-test-harness` to generate labeled drift scenarios and measure detection accuracy:

```bash
bridgetos-harness run \
    --agent-id eval-001 \
    --scenario baseline \
    --scenario prompt_injection \
    --scenario semantic_drift \
    --n 50 \
    --output report.json
```

The harness produces accuracy, false-positive rate, false-negative rate, and per-scenario detection latency.
