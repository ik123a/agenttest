"""
Tool call assertions for verifying agent tool usage.

Provides assertions to verify which tools were called, how many times,
and with what arguments during agent execution.
"""

from __future__ import annotations

import re
from typing import Any


class ToolAssertions:
    """
    Assertions for tool calls made by an agent.
    
    Works with the ToolRegistry to verify tool execution history.
    """
    
    def __init__(self, mock_registry: Any):
        """
        Initialize tool assertions.
        
        Args:
            mock_registry: ToolRegistry instance with call history
        """
        self._registry = mock_registry
    
    def assert_tool_called(
        self,
        name: str,
        times: int | None = None,
        args_contains: dict | None = None,
    ) -> None:
        """
        Assert that a tool was called.
        
        Args:
            name: Tool name to check
            times: Expected number of calls (None = at least once)
            args_contains: Dict of args that must be present in at least one call
            
        Raises:
            AssertionError: If assertion fails
        """
        calls = self._registry.get_calls(name)
        
        if not calls:
            raise AssertionError(
                f"Tool '{name}' was never called. "
                f"Expected {'exactly ' + str(times) + ' call(s)' if times else 'at least 1 call'}."
            )
        
        if times is not None and len(calls) != times:
            raise AssertionError(
                f"Tool '{name}' was called {len(calls)} time(s), expected {times}."
            )
        
        if args_contains:
            found = False
            for call in calls:
                if self._dict_contains(call.arguments, args_contains):
                    found = True
                    break
            
            if not found:
                raise AssertionError(
                    f"Tool '{name}' was never called with arguments containing {args_contains}. "
                    f"Actual calls: {[c.arguments for c in calls]}"
                )
    
    def assert_tool_called_with(self, name: str, arguments: dict) -> None:
        """
        Assert tool was called with exact arguments.
        
        Args:
            name: Tool name
            arguments: Expected exact arguments
            
        Raises:
            AssertionError: If assertion fails
        """
        calls = self._registry.get_calls(name)
        
        if not calls:
            raise AssertionError(f"Tool '{name}' was never called.")
        
        for call in calls:
            if call.arguments == arguments:
                return  # Found match
        
        raise AssertionError(
            f"Tool '{name}' was never called with arguments {arguments}. "
            f"Actual calls: {[c.arguments for c in calls]}"
        )
    
    def assert_tool_not_called(self, name: str) -> None:
        """
        Assert tool was never called.
        
        Args:
            name: Tool name
            
        Raises:
            AssertionError: If tool was called
        """
        calls = self._registry.get_calls(name)
        
        if calls:
            raise AssertionError(
                f"Tool '{name}' was called {len(calls)} time(s) but should not have been called."
            )
    
    def assert_tool_call_order(self, *tool_names: str) -> None:
        """
        Assert tools were called in specific order.
        
        Args:
            *tool_names: Expected order of tool names
            
        Raises:
            AssertionError: If assertion fails
        """
        all_calls = self._registry.get_calls()
        
        if not all_calls:
            raise AssertionError("No tools were called.")
        
        # Extract actual call sequence
        actual_order = [call.name for call in all_calls]
        
        # Check if expected order is a subsequence
        expected_iter = iter(tool_names)
        expected_name = next(expected_iter, None)
        
        for actual_name in actual_order:
            if expected_name is not None and actual_name == expected_name:
                expected_name = next(expected_iter, None)
        
        if expected_name is not None:
            raise AssertionError(
                f"Tool call order mismatch. Expected '{expected_name}' but it was not found "
                f"in the expected position. Actual order: {actual_order}"
            )
    
    def get_tool_calls(self, name: str | None = None) -> list[dict]:
        """
        Get all recorded tool calls, optionally filtered by name.
        
        Args:
            name: Optional tool name filter
            
        Returns:
            List of tool call dicts
        """
        calls = self._registry.get_calls(name)
        return [
            {
                "name": c.name,
                "arguments": c.arguments,
                "result": c.result,
                "timestamp": c.timestamp,
                "duration_ms": c.duration_ms,
            }
            for c in calls
        ]
    
    def _dict_contains(self, haystack: dict, needle: dict) -> bool:
        """Check if haystack dict contains all key-value pairs from needle."""
        for key, value in needle.items():
            if key not in haystack:
                return False
            if isinstance(value, dict) and isinstance(haystack[key], dict):
                if not self._dict_contains(haystack[key], value):
                    return False
            elif haystack[key] != value:
                return False
        return True
