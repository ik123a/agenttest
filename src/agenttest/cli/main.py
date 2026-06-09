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
    import pytest
    
    console.print(f"[bold]Running tests in {path}...[/bold]")
    
    args = [path, "-v"] if verbose else [path]
    
    if replay:
        console.print("[yellow]Replay mode enabled[/yellow]")
        # Replay mode would use recorded traces
    
    result = pytest.main(args)
    
    if result == 0:
        console.print("[green]All tests passed![/green]")
    else:
        console.print("[red]Some tests failed[/red]")
        raise SystemExit(result)


@cli.command()
@click.argument("run_id")
@click.option("--trace-dir", default="./.agenttest/traces", help="Trace directory")
def replay(run_id: str, trace_dir: str) -> None:
    """Replay a previous test run."""
    from agenttest.core.replay import ReplayEngine
    
    console.print(f"[bold]Replaying run: {run_id}[/bold]")
    
    try:
        engine = ReplayEngine(trace_dir)
        events = list(engine.replay(run_id))
        
        for event in events:
            event_type = event.get("event_type", "unknown")
            data = event.get("data", {})
            
            if event_type == "user_message":
                console.print(f"[blue]User:[/blue] {data.get('content', '')}")
            elif event_type == "agent_response":
                console.print(f"[green]Agent:[/green] {data.get('output', '')[:100]}...")
            elif event_type == "tool_call":
                console.print(f"[yellow]Tool:[/yellow] {data.get('name', '')}")
        
        console.print(f"\n[green]Replay complete: {len(events)} events[/green]")
        
    except FileNotFoundError:
        console.print(f"[red]Run not found: {run_id}[/red]")
        raise SystemExit(1)


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
    
    for run in runs:
        status_style = "green" if run["status"] == "passed" else "red"
        table.add_row(
            run["id"][:8] + "...",
            run["test_name"],
            f"[{status_style}]{run['status']}[/{status_style}]",
            run.get("agent_type", "unknown"),
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
