# Mocking Tools

AgentTest provides a flexible mocking system for replacing real tool implementations.

## Basic Mocking

```python
with AgentTest(agent) as test:
    # Mock a tool with return value
    test.mock_tool("get_weather", return_value={"temp": 22})
    
    # Mock with exception (for error testing)
    test.mock_tool("api_call", side_effect=TimeoutError("Request timed out"))
    
    response = test.run("What's the weather?")
    test.assert_tool_called("get_weather")
```

## Built-in Mocks

### HTTP Mock

```python
from agenttest.mocks import MockHTTPTool

http_mock = MockHTTPTool()
http_mock.set_response("https://api.example.com/data", {"result": "ok"})
```

### File I/O Mock

```python
from agenttest.mocks import MockFileTool

file_mock = MockFileTool()
file_mock.set_file_content("/path/to/file.txt", "file content")
```

### Database Mock

```python
from agenttest.mocks import MockDBTool

db_mock = MockDBTool()
db_mock.set_query_result("SELECT * FROM users", [{"id": 1, "name": "Alice"}])
```

## Recording Calls

All mock calls are automatically recorded:

```python
with AgentTest(agent) as test:
    test.mock_tool("search")
    test.run("Search for something")
    
    # Get all tool calls
    calls = test.get_tool_calls()
    assert calls[0]["name"] == "search"
```
