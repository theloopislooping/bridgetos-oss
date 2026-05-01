"""Drift and failure-mode scenarios for the BridgetOS test harness.

Each scenario produces a sequence of synthetic Observations representing
an agent under a specific drift condition. Scenarios are deterministic
given a seed for reproducibility in benchmarking.

Available scenarios:

- Baseline:           normal operation, no drift
- PromptInjection:    adversarial instructions injected mid-session
- SemanticDrift:      gradual topic shift away from baseline
- ToolMisuse:         agent invokes wrong tools or with wrong arguments
- StylisticDrift:     writing style shifts (verbosity, formality)
- PersonaBreak:       agent breaks character / role
"""

from bridgetos_harness.scenarios.base import Scenario
from bridgetos_harness.scenarios.baseline import Baseline
from bridgetos_harness.scenarios.persona_break import PersonaBreak
from bridgetos_harness.scenarios.prompt_injection import PromptInjection
from bridgetos_harness.scenarios.semantic_drift import SemanticDrift
from bridgetos_harness.scenarios.stylistic_drift import StylisticDrift
from bridgetos_harness.scenarios.tool_misuse import ToolMisuse

__all__ = [
    "Scenario",
    "Baseline",
    "PersonaBreak",
    "PromptInjection",
    "SemanticDrift",
    "StylisticDrift",
    "ToolMisuse",
]
