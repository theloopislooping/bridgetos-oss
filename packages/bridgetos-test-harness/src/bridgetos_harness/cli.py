"""Command-line interface for the BridgetOS drift test harness."""

from __future__ import annotations

import sys

import click
from rich.console import Console

from bridgetos_harness import scenarios
from bridgetos_harness.runner import Runner

console = Console()


SCENARIO_BUILDERS = {
    "baseline": lambda n: scenarios.Baseline(n=n),
    "prompt_injection": lambda n: scenarios.PromptInjection(n=n, position=0.6),
    "semantic_drift": lambda n: scenarios.SemanticDrift(n=n, drift_strength=0.6),
    "tool_misuse": lambda n: scenarios.ToolMisuse(n=n, misuse_rate=0.5),
    "stylistic_drift": lambda n: scenarios.StylisticDrift(n=n, mode="verbose"),
    "persona_break": lambda n: scenarios.PersonaBreak(n=n, break_rate=0.4),
}


@click.group()
def main() -> None:
    """BridgetOS drift test harness."""


@main.command(name="run")
@click.option("--agent-id", default="harness-agent-001", show_default=True)
@click.option("--scenario", "scenario_names", multiple=True, default=list(SCENARIO_BUILDERS), show_default=True,
              help="Scenarios to run. Repeat flag for multiple.")
@click.option("--n", default=20, show_default=True, help="Observations per scenario.")
@click.option("--dry-run", is_flag=True, help="Generate observations without sending to API.")
@click.option("--output", type=click.Path(), default=None, help="Save report JSON to this path.")
def run(agent_id: str, scenario_names: tuple[str, ...], n: int, dry_run: bool, output: str | None) -> None:
    """Run drift scenarios against a BridgetOS-monitored agent."""
    unknown = set(scenario_names) - set(SCENARIO_BUILDERS)
    if unknown:
        console.print(f"[red]Unknown scenarios: {sorted(unknown)}[/red]")
        sys.exit(1)
    selected = [SCENARIO_BUILDERS[name](n) for name in scenario_names]

    console.print(f"[bold]Running {len(selected)} scenarios against {agent_id}[/bold]")
    runner = Runner(agent_id=agent_id, dry_run=dry_run)
    report = runner.run(selected)

    console.print()
    console.print(report.summary())

    if output:
        report.save(output)
        console.print(f"\n[dim]Report written to {output}[/dim]")


@main.command(name="list")
def list_scenarios() -> None:
    """List available scenarios."""
    for name in SCENARIO_BUILDERS:
        builder = SCENARIO_BUILDERS[name](10)
        marker = "drift " if builder.expected_drift else "normal"
        console.print(f"  [cyan]{name:<20}[/cyan] [{marker}] {builder.description}")


if __name__ == "__main__":
    main()
