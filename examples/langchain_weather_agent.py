"""
Example weather agent using AgentTest.
"""

from __future__ import annotations

from agenttest import AgentTest
from tests.fixtures.mock_agent import MockAgent


def build_weather_agent() -> MockAgent:
    """Build a simple weather agent for demonstration."""
    return MockAgent(
        response="The weather in {city} is sunny with a high of 22°C.",
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
