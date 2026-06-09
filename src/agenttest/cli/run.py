"""
Run command implementation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from rich.console import Console

console = Console()


def run_tests(path: str, verbose: bool = False, replay: bool = False) -> int:
    """
    Run agent tests.
    
    Args:
        path: Path to test directory or file
        verbose: Enable verbose output
        replay: Enable replay mode
        
    Returns:
        Exit code (0 = success)
    """
    console.print(f"[bold]Running tests in {path}...[/bold]")
    
    if replay:
        console.print("[yellow]Replay mode enabled[/yellow]")
    
    args = [path, "-v"] if verbose else [path]
    
    result = pytest.main(args)
    
    if result == 0:
        console.print("[green]All tests passed![/green]")
    else:
        console.print("[red]Some tests failed[/red]")
    
    return result
