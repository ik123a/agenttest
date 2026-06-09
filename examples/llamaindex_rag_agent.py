"""
Example LlamaIndex RAG agent using AgentTest.
"""

from __future__ import annotations

from typing import Any, List

from agenttest import AgentTest


class MockRAGAgent:
    """
    Mock LlamaIndex-style RAG agent for demonstration.
    """
    
    def __init__(self, response: str = "Based on the documents...", tools: list[str] | None = None):
        self.response = response
        self.tools = tools or []
        self.memory: dict[str, Any] = {}
        self.chat_history: list[dict] = []
    
    def chat(self, message: str, **kwargs: Any) -> dict:
        """LlamaIndex chat interface."""
        self.chat_history.append({"role": "user", "content": message})
        
        # Simulate RAG tool call
        if "search" in message.lower() or "find" in message.lower():
            return {
                "response": f"Found relevant documents for: {message}",
                "tool_calls": [{"tool_name": "vector_search", "tool_kwargs": {"query": message}}],
            }
        
        return {
            "response": self.response,
            "tool_calls": [],
        }
    
    def query(self, message: str, **kwargs: Any) -> dict:
        """Legacy query interface."""
        return self.chat(message, **kwargs)


def build_rag_agent() -> MockRAGAgent:
    """Build a simple RAG agent for demonstration."""
    return MockRAGAgent(
        response="Based on the retrieved documents, the answer is...",
        tools=["vector_search", "web_search"],
    )


def test_rag_agent_basic():
    """Test basic RAG agent functionality."""
    agent = build_rag_agent()
    
    with AgentTest(agent) as test:
        response = test.run("What is the policy on refunds?")
        assert response is not None
        assert "refund" in response.lower() or "policy" in response.lower()


def test_rag_agent_with_search():
    """Test RAG agent with search tool."""
    agent = build_rag_agent()
    
    with AgentTest(agent) as test:
        test.mock_tool("vector_search", return_value={"results": ["doc1", "doc2"]})
        
        response = test.run("Search for information about returns")
        
        test.assert_tool_called("vector_search")


if __name__ == "__main__":
    test_rag_agent_basic()
    test_rag_agent_with_search()
    print("All RAG example tests passed!")
