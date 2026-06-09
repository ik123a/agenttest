"""
CLI entrypoint for AgentTest.

Provides commands for running tests, replaying traces, and managing
test runs.
"""

from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="agenttest")
def cli() -> None:
    """AgentTest - pytest for AI agents."""
    pass


@cli.command()
@click.argument("path", default="tests/")
@click.option("--replay", is_flag=True, help="Replay mode using recorded traces")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def run(path: str, replay: bool, verbose: bool) -> None:
    """Run agent tests."""
    from agenttest.cli.run import run_tests
    
    result = run_tests(path, verbose=verbose, replay=replay)
    if result != 0:
        raise SystemExit(result)


@cli.command()
@click.argument("run_id")
@click.option("--trace-dir", default="./.agenttest/traces", help="Trace directory")
def replay(run_id: str, trace_dir: str) -> None:
    """Replay a previous test run."""
    from agenttest.cli.replay import replay_run
    
    replay_run(run_id, trace_dir)


@cli.command(name="list")
@click.option("--trace-dir", default="./.agenttest/traces", help="Trace directory")
@click.option("--limit", "-n", default=20, help="Maximum runs to show")
def list_runs(trace_dir: str, limit: int) -> None:
    """List past test runs."""
    from agenttest.core.recorder import Recorder
    
    recorder = Recorder(trace_dir)
    runs = recorder.list_runs(limit)
    
    if not runs:
        console.print("[yellow]No test runs found[/yellow]")
        return
    
    table = Table(title="Test Runs")
    table.add_column("ID", style="cyan")
    table.add_column("Test Name")
    table.add_column("Status")
    table.add_column("Agent Type")
    
    for run_data in runs:
        status_style = "green" if run_data["status"] == "passed" else "red"
        table.add_row(
            run_data["id"][:8] + "...",
            run_data["test_name"],
            f"[{status_style}]{run_data['status']}[/{status_style}]",
            run_data.get("agent_type", "unknown"),
        )
    
    console.print(table)


@cli.command()
def info() -> None:
    """Show AgentTest information."""
    from agenttest import __version__
    
    console.print(f"[bold]AgentTest v{__version__}[/bold]")
    console.print("pytest for AI agents")
    console.print("\nCommands:")
    console.print("  agenttest run [path]    Run agent tests")
    console.print("  agenttest replay [id]   Replay a test run")
    console.print("  agenttest list          List past runs")


if __name__ == "__main__":
    cli()
