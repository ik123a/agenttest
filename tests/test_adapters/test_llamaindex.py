"""
Tests for LlamaIndex adapter.
"""

import pytest
from unittest.mock import MagicMock

from agenttest.adapters.llamaindex import LlamaIndexAdapter


class TestLlamaIndexAdapter:
    """Test LlamaIndex adapter."""
    
    def test_invoke_chat(self):
        agent = MagicMock()
        response = MagicMock()
        response.response = "The answer is 42"
        agent.chat.return_value = response
        
        adapter = LlamaIndexAdapter(agent)
        result = adapter.invoke("What is the meaning?")
        
        assert result["output"] == "The answer is 42"
    
    def test_invoke_query(self):
        agent = MagicMock()
        del agent.chat  # No chat method
        response = MagicMock()
        response.response = "Query result"
        agent.query.return_value = response
        
        adapter = LlamaIndexAdapter(agent)
        result = adapter.invoke("Search query")
        
        assert result["output"] == "Query result"
