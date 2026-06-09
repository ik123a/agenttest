"""
SQLite recorder for storing test execution traces.

Stores all agent actions (LLM calls, tool results, memory updates) in a local
SQLite database for deterministic replay and debugging.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Database schema
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS test_runs (
    id TEXT PRIMARY KEY,
    test_name TEXT NOT NULL,
    agent_type TEXT,
    start_time INTEGER NOT NULL,
    end_time INTEGER,
    status TEXT,
    trace_path TEXT
);

CREATE TABLE IF NOT EXISTS trace_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    event_type TEXT,
    data_json TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    FOREIGN KEY(run_id) REFERENCES test_runs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_run_id ON trace_events(run_id);
CREATE INDEX IF NOT EXISTS idx_sequence ON trace_events(run_id, sequence);
"""


class Recorder:
    """
    Records all agent actions to SQLite and msgpack trace files.
    
    Creates a SQLite database at the specified trace directory and stores
    test runs and their associated events for later replay and analysis.
    """
    
    def __init__(self, trace_dir: str):
        """
        Initialize the recorder.
        
        Args:
            trace_dir: Directory to store trace database
        """
        self.trace_dir = Path(trace_dir)
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.trace_dir / "traces.db"
        self._conn: sqlite3.Connection | None = None
        
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize SQLite database and create tables."""
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()
        logger.debug(f"Initialized trace database: {self.db_path}")
    
    def start_run(self, test_name: str, agent_type: str) -> str:
        """
        Create a new test run.
        
        Args:
            test_name: Name of the test
            agent_type: Agent framework type
            
        Returns:
            Run ID (UUID)
        """
        run_id = str(uuid.uuid4())
        start_time = int(time.time() * 1000)
        
        self._conn.execute(
            "INSERT INTO test_runs (id, test_name, agent_type, start_time, status) VALUES (?, ?, ?, ?, ?)",
            (run_id, test_name, agent_type, start_time, "running"),
        )
        self._conn.commit()
        
        logger.info(f"Started test run: {run_id}")
        return run_id
    
    def record_event(self, run_id: str, event_type: str, data: dict) -> None:
        """
        Record a trace event.
        
        Args:
            run_id: Test run ID
            event_type: Event type (user_message, agent_response, tool_call, etc.)
            data: Event data payload
        """
        # Get next sequence number
        cursor = self._conn.execute(
            "SELECT COALESCE(MAX(sequence), 0) + 1 FROM trace_events WHERE run_id = ?",
            (run_id,),
        )
        sequence = cursor.fetchone()[0]
        
        timestamp = int(time.time() * 1000)
        data_json = json.dumps(data, default=str)
        
        self._conn.execute(
            "INSERT INTO trace_events (run_id, sequence, event_type, data_json, timestamp) VALUES (?, ?, ?, ?, ?)",
            (run_id, sequence, event_type, data_json, timestamp),
        )
        self._conn.commit()
    
    def end_run(self, run_id: str, status: str) -> None:
        """
        Mark a test run as complete.
        
        Args:
            run_id: Test run ID
            status: Final status ("passed" or "failed")
        """
        end_time = int(time.time() * 1000)
        
        self._conn.execute(
            "UPDATE test_runs SET end_time = ?, status = ? WHERE id = ?",
            (end_time, status, run_id),
        )
        self._conn.commit()
        
        logger.info(f"Ended test run: {run_id} ({status})")
    
    def get_run(self, run_id: str) -> dict | None:
        """
        Retrieve run details.
        
        Args:
            run_id: Test run ID
            
        Returns:
            Run data dict or None if not found
        """
        cursor = self._conn.execute(
            "SELECT * FROM test_runs WHERE id = ?",
            (run_id,),
        )
        row = cursor.fetchone()
        
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
    
    def list_runs(self, limit: int = 50) -> list[dict]:
        """
        List recent test runs.
        
        Args:
            limit: Maximum number of runs to return
            
        Returns:
            List of run dicts
        """
        cursor = self._conn.execute(
            "SELECT * FROM test_runs ORDER BY start_time DESC LIMIT ?",
            (limit,),
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
        
        return runs
    
    def get_events(self, run_id: str) -> list[dict]:
        """
        Get all events for a test run.
        
        Args:
            run_id: Test run ID
            
        Returns:
            List of event dicts
        """
        cursor = self._conn.execute(
            "SELECT * FROM trace_events WHERE run_id = ? ORDER BY sequence",
            (run_id,),
        )
        
        events = []
        for row in cursor.fetchall():
            events.append({
                "id": row[0],
                "run_id": row[1],
                "sequence": row[2],
                "event_type": row[3],
                "data": json.loads(row[4]),
                "timestamp": row[5],
            })
        
        return events
    
    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def __del__(self) -> None:
        """Cleanup on garbage collection."""
        self.close()
