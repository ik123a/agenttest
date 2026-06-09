"""
Tests for assertion modules.
"""

import pytest
from unittest.mock import MagicMock

from agenttest.assertions.tool_asserts import ToolAssertions
from agenttest.assertions.memory_asserts import MemoryAssertions
from agenttest.assertions.output_asserts import OutputAssertions


class TestToolAssertions:
    """Test tool call assertions."""
    
    def setup_method(self):
        self.registry = MagicMock()
        self.asserts = ToolAssertions(self.registry)
    
    def test_assert_tool_called_passes(self):
        call = MagicMock(name="search", arguments={"q": "test"}, result="ok")
        self.registry.get_calls.return_value = [call]
        
        self.asserts.assert_tool_called("search")
    
    def test_assert_tool_called_fails(self):
        self.registry.get_calls.return_value = []
        
        with pytest.raises(AssertionError, match="was never called"):
            self.asserts.assert_tool_called("search")
    
    def test_assert_tool_called_times(self):
        calls = [MagicMock() for _ in range(3)]
        self.registry.get_calls.return_value = calls
        
        self.asserts.assert_tool_called("search", times=3)
    
    def test_assert_tool_not_called(self):
        self.registry.get_calls.return_value = []
        self.asserts.assert_tool_not_called("delete")
    
    def test_assert_tool_not_called_fails(self):
        self.registry.get_calls.return_value = [MagicMock()]
        
        with pytest.raises(AssertionError, match="should not have been called"):
            self.asserts.assert_tool_not_called("delete")


class TestMemoryAssertions:
    """Test memory assertions."""
    
    def setup_method(self):
        self.proxy = MagicMock()
        self.proxy.get_memory.return_value = {"name": "Alice", "count": 5}
        self.asserts = MemoryAssertions(self.proxy)
    
    def test_assert_memory_contains_key(self):
        self.asserts.assert_memory_contains(key="name")
    
    def test_assert_memory_contains_key_fails(self):
        with pytest.raises(AssertionError, match="does not contain key"):
            self.asserts.assert_memory_contains(key="missing")
    
    def test_assert_memory_contains_key_value(self):
        self.asserts.assert_memory_contains(key="name", value="Alice")
    
    def test_assert_memory_contains_value_fails(self):
        with pytest.raises(AssertionError, match="expected"):
            self.asserts.assert_memory_contains(key="name", value="Bob")
    
    def test_assert_memory_not_contains(self):
        self.asserts.assert_memory_not_contains("missing")
    
    def test_assert_memory_not_contains_fails(self):
        with pytest.raises(AssertionError, match="should not"):
            self.asserts.assert_memory_not_contains("name")


class TestOutputAssertions:
    """Test output assertions."""
    
    def setup_method(self):
        self.asserts = OutputAssertions()
    
    def test_assert_output_matches_regex(self):
        self.asserts.assert_output_matches("The temperature is 22°C", regex=r"\d+°C")
    
    def test_assert_output_matches_regex_fails(self):
        with pytest.raises(AssertionError, match="does not match"):
            self.asserts.assert_output_matches("Hello world", regex=r"\d+°C")
    
    def test_assert_output_contains(self):
        self.asserts.assert_output_contains("Hello world", "Hello", "world")
    
    def test_assert_output_contains_fails(self):
        with pytest.raises(AssertionError, match="missing"):
            self.asserts.assert_output_contains("Hello world", "Goodbye")
    
    def test_assert_output_length(self):
        self.asserts.assert_output_matches("Hi", min_len=2, max_len=10)
    
    def test_assert_output_is_json(self):
        self.asserts.assert_output_is_json('{"key": "value"}')
    
    def test_assert_output_is_json_fails(self):
        with pytest.raises(AssertionError, match="not valid JSON"):
            self.asserts.assert_output_is_json("not json")
    
    def test_assert_output_none(self):
        with pytest.raises(AssertionError, match="is None"):
            self.asserts.assert_output_matches(None, regex=".*")
