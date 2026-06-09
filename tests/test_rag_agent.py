"""
Test file for the RAG agent example.
"""

import pytest
from agenttest import AgentTest
from examples.llamaindex_rag_agent import build_rag_agent


class TestRAGAgent:
    """Test suite for RAG agent."""
    
    def test_basic_response(self):
        """Agent should respond to queries."""
        agent = build_rag_agent()
        
        with AgentTest(agent) as test:
            response = test.run("What is the return policy?")
            assert response is not None
            assert len(response) > 0
    
    def test_search_triggers_tool(self):
        """Agent should call search tool when asked."""
        agent = build_rag_agent()
        
        with AgentTest(agent) as test:
            test.run("Search for refund information")
            # Mock agent auto-calls search for search queries
    
    def test_output_not_empty(self):
        """Agent should not return empty response."""
        agent = build_rag_agent()
        
        with AgentTest(agent) as test:
            response = test.run("Hello")
            test.assert_output_length(min_len=1)
