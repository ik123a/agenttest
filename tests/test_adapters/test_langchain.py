"""
Tests for LangChain adapter.
"""

import pytest
from unittest.mock import MagicMock

from agenttest.adapters.langchain import LangChainAdapter


class TestLangChainAdapter:
    """Test LangChain adapter."""
    
    def test_invoke_returns_output(self):
        agent = MagicMock()
        agent.invoke.return_value = {"output": "Weather is sunny"}
        
        adapter = LangChainAdapter(agent)
        result = adapter.invoke("What's the weather?")
        
        assert result["output"] == "Weather is sunny"
    
    def test_invoke_string_output(self):
        agent = MagicMock()
        agent.invoke.return_value = "Direct string response"
        
        adapter = LangChainAdapter(agent)
        result = adapter.invoke("Hello")
        
        assert result["output"] == "Direct string response"
    
    def test_get_tools(self):
        agent = MagicMock()
        tool1 = MagicMock()
        tool1.name = "search"
        tool2 = MagicMock()
        tool2.name = "weather"
        agent.tools = [tool1, tool2]
        
        adapter = LangChainAdapter(agent)
        tools = adapter.get_tools()
        
        assert "search" in tools
        assert "weather" in tools
