# Replay Mode

AgentTest records all agent actions for deterministic replay and debugging.

## How It Works

When you run tests, AgentTest automatically:

1. Records all LLM requests and responses
2. Logs tool calls and results
3. Tracks memory updates
4. Saves everything to SQLite (`./.agenttest/traces/traces.db`)

## Viewing Traces

```bash
# List all test runs
agenttest list

# Replay a specific run
agenttest replay <run-id>
```

## Programmatic Replay

```python
from agenttest.core.replay import ReplayEngine

engine = ReplayEngine("./.agenttest/traces")

# Get run info
run = engine.get_run_info("run-id-here")

# Replay all events
for event in engine.replay("run-id-here"):
    print(f"{event['event_type']}: {event['data']}")
```

## Use Cases

- **Debugging**: See exactly what happened in a failing test
- **Deterministic re-runs**: Re-execute assertions without real LLM calls
- **Audit trail**: Keep records of all agent interactions
- **CI/CD**: Compare traces between runs to detect regressions
