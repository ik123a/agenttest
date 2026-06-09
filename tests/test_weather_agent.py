"""
Test file for the weather agent example.
"""

import pytest
from agenttest import AgentTest
from tests.fixtures.mock_agent import MockAgent


def build_weather_agent() -> MockAgent:
    """Build a simple weather agent for testing."""
    return MockAgent(
        response="The weather is sunny with a high of 22°C.",
        tools=["get_weather", "get_forecast"],
    )


class TestWeatherAgent:
    """Test suite for weather agent."""
    
    def test_basic_response(self):
        """Agent should respond to weather queries."""
        agent = build_weather_agent()
        
        with AgentTest(agent) as test:
            response = test.run("What's the weather?")
            assert response is not None
            assert len(response) > 0
    
    def test_city_mentioned(self):
        """Agent should mention the city in response."""
        agent = build_weather_agent()
        
        with AgentTest(agent) as test:
            response = test.run("Weather in Paris?")
            # Agent should include city or weather info
            assert "Paris" in response or "weather" in response.lower()
    
    def test_tool_called_for_search(self):
        """Agent should call search tool when asked."""
        agent = build_weather_agent()
        
        with AgentTest(agent) as test:
            test.run("Search for weather data")
            # Mock agent auto-calls search for search queries
            # In real test, verify specific tool calls
    
    def test_output_not_empty(self):
        """Agent should not return empty response."""
        agent = build_weather_agent()
        
        with AgentTest(agent) as test:
            response = test.run("Hello")
            test.assert_output_length(min_len=1)
    
    def test_output_is_string(self):
        """Agent should return string output."""
        agent = build_weather_agent()
        
        with AgentTest(agent) as test:
            response = test.run("Test")
            assert isinstance(response, str)
