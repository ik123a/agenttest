"""
AgentTest context manager - the main entry point for testing agents.

Usage:
    from agenttest import AgentTest
    
    def test_weather_agent():
        agent = build_agent()
        with AgentTest(agent) as test:
            test.mock_tool("get_weather", return_value={"temp": 22})
            response = test.run("What's the weather in Tokyo?")
            test.assert_tool_called("get_weather", times=1)
            test.assert_memory_contains("last_city", "Tokyo")
"""

from __future__ import annotations

import logging
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Generator

from agenttest.core.proxy import AgentProxy
from agenttest.core.recorder import Recorder
from agenttest.core.replay import ReplayEngine
from agenttest.mocks.tool_registry import ToolRegistry
from agenttest.assertions.tool_asserts import ToolAssertions
from agenttest.assertions.memory_asserts import MemoryAssertions
from agenttest.assertions.output_asserts import OutputAssertions

logger = logging.getLogger(__name__)


class AgentTest:
    """
    pytest for AI agents - deterministic testing of non-deterministic systems.
    
    Wraps any agent (LangChain, LlamaIndex, or custom) and provides:
    - Tool mocking and call recording
    - Memory state inspection
    - Output assertions (regex, JSON, LLM judge)
    - Trace recording and replay
    
    Example:
        with AgentTest(agent) as test:
            test.mock_tool("search", return_value="results")
            response = test.run("search for X")
            test.assert_tool_called("search")
    """
    
    def __init__(
        self,
        agent: Any,
        adapter: Any | None = None,
        trace_dir: str = "./.agenttest/traces",
        agent_type: str = "custom",
    ):
        """
        Initialize AgentTest.
        
        Args:
            agent: The agent instance to test
            adapter: Optional adapter for agent framework (auto-detected if None)
            trace_dir: Directory to store trace files
            agent_type: Agent framework type ("langchain", "llamaindex", "custom")
        """
        self.agent = agent
        self.trace_dir = Path(trace_dir)
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self._recorder = Recorder(str(self.trace_dir))
        self._mock_registry = ToolRegistry()
        self._proxy = AgentProxy(agent, adapter=adapter, agent_type=agent_type)
        
        # Assertion mixins
        self._tool_asserts = ToolAssertions(self._mock_registry)
        self._memory_asserts = MemoryAssertions(self._proxy)
        self._output_asserts = OutputAssertions()
        
        # State
        self._run_id: str | None = None
        self._last_output: str | None = None
        self._tool_calls: list[dict] = []
        self._entered = False
        
    def __enter__(self) -> AgentTest:
        """Start test session."""
        self._entered = True
        self._run_id = self._recorder.start_run(
            test_name="agent_test",
            agent_type=self._proxy.agent_type,
        )
        logger.info(f"AgentTest session started: {self._run_id}")
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """End test session and save trace."""
        if not self._entered:
            return
            
        status = "passed" if exc_type is None else "failed"
        self._recorder.end_run(self._run_id, status)
        self._entered = False
        logger.info(f"AgentTest session ended: {self._run_id} ({status})")
    
    def run(self, message: str, **kwargs: Any) -> str:
        """
        Execute agent with a message and record all events.
        
        Args:
            message: User message to send to agent
            **kwargs: Additional arguments passed to agent
            
        Returns:
            Agent's response as string
            
        Raises:
            RuntimeError: If used outside context manager
        """
        if not self._entered:
            raise RuntimeError("AgentTest must be used as context manager")
            
        # Record user message
        self._recorder.record_event(
            self._run_id,
            "user_message",
            {"content": message},
        )
        
        # Execute via proxy (intercepts tool calls, etc.)
        result = self._proxy.invoke(message, **kwargs)
        
        # Extract output
        output = result.get("output", "")
        self._last_output = output
        self._tool_calls = result.get("tool_calls", [])
        
        # Record response
        self._recorder.record_event(
            self._run_id,
            "agent_response",
            {"output": output, "tool_calls": self._tool_calls},
        )
        
        return output
    
    def mock_tool(
        self,
        name: str,
        return_value: Any = None,
        side_effect: Exception | None = None,
    ) -> None:
        """
        Register a mock tool replacement.
        
        Args:
            name: Tool name to mock
            return_value: Value to return when tool is called
            side_effect: Exception to raise instead of returning value
        """
        self._mock_registry.register(name, return_value=return_value, side_effect=side_effect)
        self._proxy.set_mock_registry(self._mock_registry)
        logger.info(f"Mocked tool: {name}")
    
    # --- Tool Assertions ---
    
    def assert_tool_called(
        self,
        name: str,
        times: int | None = None,
        args_contains: dict | None = None,
    ) -> None:
        """Assert tool was called with expectations."""
        self._tool_asserts.assert_tool_called(name, times=times, args_contains=args_contains)
    
    def assert_tool_called_with(self, name: str, arguments: dict) -> None:
        """Assert tool was called with exact arguments."""
        self._tool_asserts.assert_tool_called_with(name, arguments)
    
    def assert_tool_not_called(self, name: str) -> None:
        """Assert tool was never called."""
        self._tool_asserts.assert_tool_not_called(name)
    
    def assert_tool_call_order(self, *tool_names: str) -> None:
        """Assert tools were called in specific order."""
        self._tool_asserts.assert_tool_call_order(*tool_names)
    
    # --- Memory Assertions ---
    
    def assert_memory_contains(self, key: str | None = None, value: Any = None) -> None:
        """Assert agent memory contains specific key/value."""
        self._memory_asserts.assert_memory_contains(key=key, value=value)
    
    def assert_memory_not_contains(self, key: str) -> None:
        """Assert memory does NOT contain key."""
        self._memory_asserts.assert_memory_not_contains(key)
    
    def assert_memory_size(self, min_size: int | None = None, max_size: int | None = None) -> None:
        """Assert memory has expected number of entries."""
        self._memory_asserts.assert_memory_size(min_size=min_size, max_size=max_size)
    
    # --- Output Assertions ---
    
    def assert_output_matches(
        self,
        regex: str | None = None,
        json_schema: dict | None = None,
        llm_judge: str | None = None,
    ) -> None:
        """Validate agent output against patterns or LLM judge."""
        self._output_asserts.assert_output_matches(
            self._last_output,
            regex=regex,
            json_schema=json_schema,
            llm_judge=llm_judge,
        )
    
    def assert_output_contains(self, *substrs: str) -> None:
        """Assert output contains all substrings."""
        self._output_asserts.assert_output_contains(self._last_output, *substrs)
    
    def assert_output_length(self, min_len: int | None = None, max_len: int | None = None) -> None:
        """Assert output length constraints."""
        self._output_asserts.assert_output_length(self._last_output, min_len=min_len, max_len=max_len)
    
    def assert_output_is_json(self) -> None:
        """Assert output is valid JSON."""
        self._output_asserts.assert_output_is_json(self._last_output)
    
    # --- Utility ---
    
    def get_tool_calls(self) -> list[dict]:
        """Get all recorded tool calls."""
        return self._tool_calls
    
    def get_memory_state(self) -> dict:
        """Get current agent memory state."""
        return self._memory_asserts.get_memory_state()
    
    @property
    def run_id(self) -> str | None:
        """Get current run ID."""
        return self._run_id
