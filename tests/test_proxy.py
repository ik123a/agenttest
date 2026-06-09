"""
Tests for agent proxy.
"""

import pytest
from unittest.mock import MagicMock

from agenttest.core.proxy import AgentProxy


class TestAgentProxy:
    """Test agent proxy functionality."""
    
    def test_proxy_invoke(self):
        agent = MagicMock()
        agent.invoke.return_value = {"output": "Hello", "tool_calls": []}
        
        proxy = AgentProxy(agent, agent_type="custom")
        result = proxy.invoke("Hi")
        
        assert result["output"] == "Hello"
    
    def test_proxy_records_tool_calls(self):
        agent = MagicMock()
        agent.invoke.return_value = {
            "output": "Done",
            "tool_calls": [{"name": "search", "arguments": {"q": "test"}}],
        }
        
        proxy = AgentProxy(agent, agent_type="custom")
        proxy.invoke("Search for test")
        
        calls = proxy.get_tool_calls()
        assert len(calls) == 1
        assert calls[0]["name"] == "search"
    
    def test_proxy_get_memory(self):
        agent = MagicMock()
        agent.memory = {"context": "test"}
        
        proxy = AgentProxy(agent, agent_type="custom")
        memory = proxy.get_memory()
        
        assert "context" in memory
