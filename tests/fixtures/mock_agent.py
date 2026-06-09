"""
Mock agent for testing.
"""

from __future__ import annotations

from typing import Any


class MockAgent:
    """
    Simple mock agent for testing AgentTest.
    
    Returns configured responses and tracks tool calls.
    """
    
    def __init__(self, response: str = "Hello!", tools: list[str] | None = None):
        self.response = response
        self.tools = tools or []
        self.memory: dict[str, Any] = {}
        self.tool_calls: list[dict] = []
    
    def invoke(self, message: str, **kwargs: Any) -> dict:
        """Invoke the mock agent."""
        # Simulate tool call
        if "search" in message.lower():
            self.tool_calls.append({
                "name": "search",
                "arguments": {"query": message},
            })
            return {
                "output": f"Search results for: {message}",
                "tool_calls": self.tool_calls,
            }
        
        return {
            "output": self.response,
            "tool_calls": [],
        }
    
    def run(self, message: str, **kwargs: Any) -> str:
        """Legacy run method."""
        return self.invoke(message, **kwargs)["output"]
