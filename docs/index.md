# AgentTest

**pytest for AI agents** – deterministic testing of non-deterministic systems

## Overview

AgentTest is the first testing framework designed specifically for AI agents. It provides deterministic assertions over non-deterministic systems by combining:

- **Tool mocking** – Replace real tools with mocks, verify call sequences
- **Memory assertions** – Check agent's short-term and semantic memory
- **Output validation** – Regex, JSON schema, or LLM judge evaluation
- **Trace recording** – SQLite + msgpack for deterministic replay
- **Scenario files** – YAML/JSON multi-step test workflows

## Quick Start

```bash
pip install agenttest
```

```python
from agenttest import AgentTest

def test_my_agent():
    agent = MyAgent()
    with AgentTest(agent) as test:
        test.mock_tool("api_call", return_value={"status": "ok"})
        response = test.run("Do something")
        test.assert_tool_called("api_call")
        test.assert_output_contains("success")
```

## Documentation

- [Quick Start Guide](quickstart.md)
- [Assertion API](assertions.md)
- [Mocking Tools](mocking.md)
- [Scenario Files](scenarios.md)
- [Replay Mode](replay.md)

## Links

- [GitHub Repository](https://github.com/ik123a/agenttest)
- [PyPI Package](https://pypi.org/project/agenttest/)
- [Issue Tracker](https://github.com/ik123a/agenttest/issues)
