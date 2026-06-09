# Scenario Files

Define multi-step agent test workflows in YAML or JSON.

## YAML Format

```yaml
name: "Flight booking happy path"
description: "Test complete booking workflow"
tags: ["booking", "happy-path"]

steps:
  - user: "Book a flight from New York to London tomorrow"
    assert_tool_called:
      name: "search_flights"
      arguments:
        origin: "NYC"
        destination: "LON"
    assert_memory:
      origin: "NYC"
      
  - user: "Pick the cheapest one"
    assert_tool_called:
      name: "book_flight"
    assert_output_matches: "confirmed"
    
  - user: "What's my booking reference?"
    assert_output_matches:
      llm_judge: "Contains a booking reference number"
```

## Running Scenarios

```python
from agenttest.scenarios import ScenarioLoader, ScenarioRunner

# Load scenarios from file
scenarios = ScenarioLoader.load("scenarios/booking.yaml")

# Run with agent test
with AgentTest(agent) as test:
    runner = ScenarioRunner(test)
    
    for scenario in scenarios:
        result = runner.run(scenario)
        assert result.passed, f"Scenario '{scenario.name}' failed"
```

## Scenario Structure

Each step can include:

- **user**: Message to send to agent
- **assert_tool_called**: Tool assertion config
- **assert_memory**: Memory state assertions
- **assert_output_matches**: Output validation (regex, JSON, or LLM judge)
