# AgentTest

![PyPI](https://img.shields.io/pypi/v/agenttest)
![Tests](https://img.shields.io/github/actions/workflow/status/agenttest/agenttest/ci.yml?branch=main)
![License](https://img.shields.io/github/license/agenttest/agenttest)
![Python](https://img.shields.io/pypi/pyversions/agenttest)

**pytest for AI agents** – deterministic testing of non-deterministic systems

## The Problem

AI agents are unreliable because they combine memory, tool use, and non-deterministic reasoning. Existing tools like LangSmith and Langfuse give you observability, but not **testability**. You can see what happened, but you can't write assertions against it.

## The Solution

AgentTest gives you the first framework to write deterministic, replayable, end-to-end tests for any agent built with LangChain, LlamaIndex, or custom code.

```python
from agenttest import AgentTest

def test_weather_agent():
    agent = build_agent()
    with AgentTest(agent) as test:
        # Mock external tools
        test.mock_tool("get_weather", return_value={"temp": 22, "condition": "sunny"})
        
        # Run the agent
        response = test.run("What's the weather in Tokyo?")
        
        # Assertions
        test.assert_tool_called("get_weather", times=1)
        test.assert_tool_called_with("get_weather", arguments={"city": "Tokyo"})
        test.assert_memory_contains("last_city", "Tokyo")
        test.assert_output_matches(regex=r"22.*sunny")
```

## Features

- **Tool Mocking** – Replace real tools with mocks, verify call sequences
- **Memory Assertions** – Check agent's short-term and semantic memory
- **Output Validation** – Regex, JSON schema, or LLM judge evaluation
- **Trace Recording** – SQLite + msgpack for deterministic replay
- **Scenario Files** – YAML/JSON multi-step test workflows
- **Zero Infrastructure** – Runs entirely locally, no Docker needed

## Installation

```bash
pip install agenttest
```

## Quick Start

```python
import pytest
from agenttest import AgentTest

def test_my_agent():
    agent = MyAgent()
    with AgentTest(agent) as test:
        test.mock_tool("api_call", return_value={"status": "ok"})
        
        response = test.run("Do something")
        
        test.assert_tool_called("api_call")
        test.assert_output_contains("success")
```

## Why AgentTest?

| Tool | What It Does | AgentTest Difference |
|------|--------------|---------------------|
| pytest | Unit testing | Can't handle LLM calls or memory |
| LangSmith | Observability | No assertions, no mocking |
| deepeval | Single output eval | No multi-turn, no tool simulation |
| AgentTest | **Full agent testing** | Tools + memory + replay + scenarios |

## Supported Frameworks

- **LangChain** – AgentExecutor, LCEL chains
- **LlamaIndex** – AgentRunner, ReActAgent  
- **Custom** – Any agent with invoke/run interface

## Documentation

- [Quick Start](docs/quickstart.md)
- [Assertion API](docs/assertions.md)
- [Mocking Tools](docs/mocking.md)
- [Scenario Files](docs/scenarios.md)
- [Replay Mode](docs/replay.md)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
