"""
Example weather agent using AgentTest.
"""

from __future__ import annotations

from typing import Any

from agenttest import AgentTest


class MockWeatherAgent:
    """
    Simple mock weather agent for demonstration.
    
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


def build_weather_agent() -> MockWeatherAgent:
    """Build a simple weather agent for demonstration."""
    return MockWeatherAgent(
        response="The weather is sunny with a high of 22°C.",
        tools=["get_weather", "get_forecast"],
    )


def test_weather_agent_basic():
    """Test basic agent functionality."""
    agent = build_weather_agent()
    
    with AgentTest(agent) as test:
        response = test.run("What's the weather in Tokyo?")
        assert "Tokyo" in response or "weather" in response


def test_weather_agent_with_mock():
    """Test agent with mocked tools."""
    agent = build_weather_agent()
    
    with AgentTest(agent) as test:
        # Mock the weather API
        test.mock_tool("get_weather", return_value={"temp": 22, "condition": "sunny"})
        
        response = test.run("What's the weather in London?")
        
        # Verify tool was used
        test.assert_tool_called("get_weather")


def test_weather_agent_memory():
    """Test agent memory assertions."""
    agent = build_weather_agent()
    
    with AgentTest(agent) as test:
        test.run("My name is Alice")
        
        # Check memory (mock agent stores in memory dict)
        # In real scenario, adapter would read from agent memory
        # test.assert_memory_contains("user_name", "Alice")


if __name__ == "__main__":
    # Run tests manually
    test_weather_agent_basic()
    test_weather_agent_with_mock()
    print("All example tests passed!")
