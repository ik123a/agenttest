"""
Tests for agent proxy.
"""

import pytest
from unittest.mock import MagicMock

from agenttest.core.proxy import AgentProxy
from agenttest.adapters.custom import CustomAdapter


class TestAgentProxy:
    """Test agent proxy functionality."""
    
    def test_proxy_invoke(self):
        agent = MagicMock()
        agent.invoke.return_value = {"output": "Hello", "tool_calls": []}
        
        # Explicitly use CustomAdapter to avoid auto-detection
        adapter = CustomAdapter(agent)
        proxy = AgentProxy(agent, adapter=adapter, agent_type="custom")
        result = proxy.invoke("Hi")
        
        assert result["output"] == "Hello"
    
    def test_proxy_records_tool_calls(self):
        """Test that tool calls from agent result are recorded."""
        agent = MagicMock()
        agent.invoke.return_value = {
            "output": "Done",
            "tool_calls": [{"name": "search", "arguments": {"q": "test"}}],
        }
        
        # Explicitly use CustomAdapter
        adapter = CustomAdapter(agent)
        proxy = AgentProxy(agent, adapter=adapter, agent_type="custom")
        result = proxy.invoke("Search for test")
        
        # Tool calls should be in the result
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["name"] == "search"
        
        # And also recorded in proxy
        calls = proxy.get_tool_calls()
        assert len(calls) == 1
        assert calls[0]["name"] == "search"
    
    def test_proxy_get_memory(self):
        agent = MagicMock()
        agent.memory = {"context": "test"}
        # Remove message_history to avoid fallback
        del agent.message_history
        
        # Explicitly use CustomAdapter
        adapter = CustomAdapter(agent)
        proxy = AgentProxy(agent, adapter=adapter, agent_type="custom")
        memory = proxy.get_memory()
        
        assert "context" in memory
