# Quick Start Guide

## Installation

```bash
pip install agenttest
```

## Your First Test

```python
from agenttest import AgentTest
from my_agent import build_agent  # Your agent factory

def test_agent_basic():
    agent = build_agent()
    with AgentTest(agent) as test:
        response = test.run("Hello!")
        assert response is not None
```

## Mocking Tools

```python
def test_with_mocked_tools():
    agent = build_agent()
    with AgentTest(agent) as test:
        # Replace real tool with mock
        test.mock_tool("search_api", return_value={"results": []})
        
        response = test.run("Search for something")
        
        # Verify tool was called
        test.assert_tool_called("search_api", times=1)
```

## Checking Memory

```python
def test_memory():
    agent = build_agent()
    with AgentTest(agent) as test:
        test.run("My name is Alice")
        
        # Check agent remembers
        test.assert_memory_contains("user_name", "Alice")
```

## Running Tests

```bash
# Using pytest
pytest tests/

# Using AgentTest CLI
agenttest run tests/
```

## Next Steps

- [Assertion API](assertions.md) - All available assertions
- [Mocking Guide](mocking.md) - Advanced mocking patterns
- [Scenario Files](scenarios.md) - YAML-based test workflows
- [Replay Mode](replay.md) - Debug with recorded traces
