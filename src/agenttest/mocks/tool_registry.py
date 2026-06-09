"""
Tool registry for managing mock tools and recording calls.

Provides a central registry for mock tool implementations with
automatic call recording for assertion verification.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """Record of a single tool invocation."""
    name: str
    arguments: dict
    result: Any
    timestamp: float
    duration_ms: float


@dataclass
class MockTool:
    """Mock tool definition."""
    name: str
    return_value: Any = None
    side_effect: Exception | None = None
    call_count: int = 0


class ToolRegistry:
    """
    Registry for mock tool implementations with call recording.
    
    Manages tool mocks and records all invocations for later assertion.
    """
    
    def __init__(self) -> None:
        """Initialize empty registry."""
        self._mocks: dict[str, MockTool] = {}
        self._calls: list[ToolCall] = []
    
    def register(
        self,
        name: str,
        return_value: Any = None,
        side_effect: Exception | None = None,
    ) -> None:
        """
        Register a mock tool.
        
        Args:
            name: Tool name
            return_value: Value to return when called
            side_effect: Exception to raise instead
        """
        self._mocks[name] = MockTool(
            name=name,
            return_value=return_value,
            side_effect=side_effect,
        )
    
    def execute(self, name: str, arguments: dict | None = None) -> Any:
        """
        Execute mock tool, record call, return mock result.
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Mock return value
            
        Raises:
            KeyError: If tool not registered
            Exception: If side_effect is set
        """
        if name not in self._mocks:
            raise KeyError(f"Tool '{name}' not registered")
        
        mock = self._mocks[name]
        mock.call_count += 1
        
        start_time = time.time()
        
        # Raise side_effect if set
        if mock.side_effect is not None:
            raise mock.side_effect
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Record call
        call = ToolCall(
            name=name,
            arguments=arguments or {},
            result=mock.return_value,
            timestamp=start_time,
            duration_ms=duration_ms,
        )
        self._calls.append(call)
        
        return mock.return_value
    
    def get_calls(self, name: str | None = None) -> list[ToolCall]:
        """
        Get recorded calls, optionally filtered by name.
        
        Args:
            name: Optional tool name filter
            
        Returns:
            List of ToolCall instances
        """
        if name is None:
            return self._calls.copy()
        return [c for c in self._calls if c.name == name]
    
    def get_call_count(self, name: str) -> int:
        """Get number of times a tool was called."""
        return len(self.get_calls(name))
    
    def has_mock(self, name: str) -> bool:
        """Check if a tool has a registered mock."""
        return name in self._mocks
    
    def clear(self) -> None:
        """Clear all mocks and recorded calls."""
        self._mocks.clear()
        self._calls.clear()
    
    def reset_calls(self) -> None:
        """Clear recorded calls but keep mocks."""
        self._calls.clear()
    
    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._mocks.keys())
