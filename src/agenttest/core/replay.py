"""
Replay engine for deterministic test execution.

Loads recorded traces and replays them without executing real LLM calls,
enabling deterministic debugging and assertion verification.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Generator

logger = logging.getLogger(__name__)


class ReplayEngine:
    """
    Replays recorded test traces without executing real LLM calls.
    
    Reads events from the SQLite trace database and yields them in order,
    allowing tests to be re-run against recorded data for deterministic
    debugging and assertion verification.
    """
    
    def __init__(self, trace_dir: str = "./.agenttest/traces"):
        """
        Initialize the replay engine.
        
        Args:
            trace_dir: Directory containing trace database
        """
        self.trace_dir = Path(trace_dir)
        self.db_path = self.trace_dir / "traces.db"
        
        if not self.db_path.exists():
            raise FileNotFoundError(f"Trace database not found: {self.db_path}")
    
    def replay(self, run_id: str) -> Generator[dict, None, None]:
        """
        Yield events from a recorded trace.
        
        Args:
            run_id: Test run ID to replay
            
        Yields:
            Event dicts in sequence order
            
        Raises:
            FileNotFoundError: If run_id not found
        """
        conn = sqlite3.connect(str(self.db_path))
        
        # Verify run exists
        cursor = conn.execute(
            "SELECT * FROM test_runs WHERE id = ?",
            (run_id,),
        )
        run = cursor.fetchone()
        
        if run is None:
            conn.close()
            raise FileNotFoundError(f"Run not found: {run_id}")
        
        logger.info(f"Replaying run: {run_id} ({run[1]})")
        
        # Get events
        cursor = conn.execute(
            "SELECT * FROM trace_events WHERE run_id = ? ORDER BY sequence",
            (run_id,),
        )
        
        for row in cursor.fetchall():
            event = {
                "id": row[0],
                "run_id": row[1],
                "sequence": row[2],
                "event_type": row[3],
                "data": json.loads(row[4]),
                "timestamp": row[5],
            }
            yield event
        
        conn.close()
    
    def get_run_info(self, run_id: str) -> dict | None:
        """
        Get run metadata without loading all events.
        
        Args:
            run_id: Test run ID
            
        Returns:
            Run info dict or None
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute(
            "SELECT * FROM test_runs WHERE id = ?",
            (run_id,),
        )
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        return {
            "id": row[0],
            "test_name": row[1],
            "agent_type": row[2],
            "start_time": row[3],
            "end_time": row[4],
            "status": row[5],
            "trace_path": row[6],
        }
    
    def list_runs(self) -> list[dict]:
        """List all available runs for replay."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute(
            "SELECT id, test_name, agent_type, start_time, end_time, status FROM test_runs ORDER BY start_time DESC"
        )
        
        runs = []
        for row in cursor.fetchall():
            runs.append({
                "id": row[0],
                "test_name": row[1],
                "agent_type": row[2],
                "start_time": row[3],
                "end_time": row[4],
                "status": row[5],
            })
        
        conn.close()
        return runs
    
    def replay_to_dict(self, run_id: str) -> dict:
        """
        Replay entire run and return as structured dict.
        
        Args:
            run_id: Test run ID
            
        Returns:
            Dict with "run" info and "events" list
        """
        run_info = self.get_run_info(run_id)
        events = list(self.replay(run_id))
        
        return {
            "run": run_info,
            "events": events,
        }
