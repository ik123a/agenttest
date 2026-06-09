# Assertion API

AgentTest provides comprehensive assertions for validating agent behavior.

## Tool Assertions

```python
# Assert tool was called at least once
test.assert_tool_called("search")

# Assert exact call count
test.assert_tool_called("search", times=2)

# Assert specific arguments
test.assert_tool_called_with("search", arguments={"query": "test"})

# Assert tool was NOT called
test.assert_tool_not_called("delete_file")

# Assert call order
test.assert_tool_call_order("search", "process", "save")
```

## Memory Assertions

```python
# Assert memory contains key
test.assert_memory_contains(key="user_name")

# Assert specific value
test.assert_memory_contains(key="user_name", value="Alice")

# Assert key does NOT exist
test.assert_memory_not_contains("password")

# Assert memory size
test.assert_memory_size(min_size=1, max_size=10)
```

## Output Assertions

```python
# Regex matching
test.assert_output_matches(regex=r"\d+ degrees")

# JSON schema validation
test.assert_output_matches(json_schema={
    "type": "object",
    "properties": {"result": {"type": "string"}}
})

# LLM judge evaluation
test.assert_output_matches(llm_judge="Response is polite and helpful")

# Substring presence
test.assert_output_contains("hello", "world")

# Length constraints
test.assert_output_length(min_len=10, max_len=100)

# JSON validation
test.assert_output_is_json()
```

## Hybrid Assertions

Combine deterministic and LLM-based checks:

```python
test.assert_hybrid(
    deterministic=[
        (test.assert_output_contains, ("success",), {}),
    ],
    llm_judge="Output describes a successful operation",
    require_both=True
)
```
