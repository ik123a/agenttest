"""
Replay command implementation.
"""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from agenttest.core.replay import ReplayEngine

console = Console()


def replay_run(run_id: str, trace_dir: str = "./.agenttest/traces") -> None:
    """
    Replay a previous test run.
    
    Args:
        run_id: Test run ID to replay
        trace_dir: Directory containing traces
    """
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
                output = data.get("output", "")
                console.print(f"[green]Agent:[/green] {output[:100]}{'...' if len(output) > 100 else ''}")
            elif event_type == "tool_call":
                console.print(f"[yellow]Tool:[/yellow] {data.get('name', '')}")
        
        console.print(f"\n[green]Replay complete: {len(events)} events[/green]")
        
    except FileNotFoundError:
        console.print(f"[red]Run not found: {run_id}[/red]")
        raise SystemExit(1)
    except Exception as e:
        console.print(f"[red]Replay error: {e}[/red]")
        raise SystemExit(1)
