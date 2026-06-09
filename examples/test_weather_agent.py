"""
Test file for the weather agent example.
"""

import pytest
from agenttest import AgentTest
from examples.langchain_weather_agent import build_weather_agent


class TestWeatherAgentExample:
    """Test suite for weather agent example."""
    
    def test_basic_response(self):
        """Agent should respond to weather queries."""
        agent = build_weather_agent()
        
        with AgentTest(agent) as test:
            response = test.run("What's the weather?")
            assert response is not None
            assert len(response) > 0
    
    def test_tool_mocking(self):
        """Test that tool mocking works."""
        agent = build_weather_agent()
        
        with AgentTest(agent) as test:
            test.mock_tool("get_weather", return_value={"temp": 22})
            response = test.run("Search for weather")
            # Verify agent responds
            assert response is not None
    
    def test_output_validation(self):
        """Test output validation."""
        agent = build_weather_agent()
        
        with AgentTest(agent) as test:
            response = test.run("Hello")
            test.assert_output_length(min_len=1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
