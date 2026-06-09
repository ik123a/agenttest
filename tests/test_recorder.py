"""
Tests for recorder module.
"""

import os
import tempfile
import pytest

from agenttest.core.recorder import Recorder


class TestRecorder:
    """Test SQLite recorder."""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.recorder = Recorder(self.temp_dir)
    
    def teardown_method(self):
        self.recorder.close()
    
    def test_start_run(self):
        run_id = self.recorder.start_run("test_weather", "custom")
        assert run_id is not None
        
        run = self.recorder.get_run(run_id)
        assert run is not None
        assert run["test_name"] == "test_weather"
        assert run["status"] == "running"
    
    def test_record_event(self):
        run_id = self.recorder.start_run("test", "custom")
        self.recorder.record_event(run_id, "user_message", {"content": "Hi"})
        
        events = self.recorder.get_events(run_id)
        assert len(events) == 1
        assert events[0]["event_type"] == "user_message"
    
    def test_end_run(self):
        run_id = self.recorder.start_run("test", "custom")
        self.recorder.end_run(run_id, "passed")
        
        run = self.recorder.get_run(run_id)
        assert run["status"] == "passed"
    
    def test_list_runs(self):
        self.recorder.start_run("test1", "custom")
        self.recorder.start_run("test2", "custom")
        
        runs = self.recorder.list_runs()
        assert len(runs) == 2
