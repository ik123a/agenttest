"""
Agent proxy - wraps any agent to intercept calls and record events.

The proxy sits between the test and the agent, capturing:
- LLM requests and responses
- Tool calls and results
- Memory updates
"""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class AgentProxy:
    """
    Wraps any agent to intercept LLM calls, tool executions, and memory updates.
    
    The proxy automatically detects the agent framework and uses the appropriate
    adapter to intercept calls. It records all events for later assertion and replay.
    """
    
    def __init__(self, agent: Any, adapter: Any | None = None, agent_type: str = "custom"):
        """
        Initialize the proxy.
        
        Args:
            agent: The agent instance to wrap
            adapter: Optional adapter (auto-detected if None)
            agent_type: Agent framework type
        """
        self.agent = agent
        self.agent_type = agent_type
        self._adapter = adapter
        self._mock_registry = None
        self._tool_calls: list[dict] = []
        self._memory_updates: list[dict] = []
        
        # Auto-detect adapter if not provided
        if self._adapter is None:
            self._adapter = self._detect_adapter()
    
    def _detect_adapter(self) -> Any:
        """Auto-detect agent framework and create appropriate adapter."""
        # Try LangChain
        try:
            from agenttest.adapters.langchain import LangChainAdapter
            if hasattr(self.agent, "invoke") or hasattr(self.agent, "run"):
                logger.info("Detected LangChain agent")
                return LangChainAdapter(self.agent)
        except ImportError:
            pass
        
        # Try LlamaIndex
        try:
            from agenttest.adapters.llamaindex import LlamaIndexAdapter
            if hasattr(self.agent, "query") or hasattr(self.agent, "chat"):
                logger.info("Detected LlamaIndex agent")
                return LlamaIndexAdapter(self.agent)
        except ImportError:
            pass
        
        # Default to custom adapter
        from agenttest.adapters.custom import CustomAdapter
        logger.info("Using custom adapter")
        return CustomAdapter(self.agent)
    
    def set_mock_registry(self, registry: Any) -> None:
        """Set the mock tool registry."""
        self._mock_registry = registry
        if self._adapter:
            self._adapter.set_mock_registry(registry)
    
    def invoke(self, message: str, **kwargs: Any) -> dict:
        """
        Execute agent with message, intercept and record all events.
        
        Args:
            message: User message
            **kwargs: Additional arguments
            
        Returns:
            Dict with keys: output, tool_calls, memory_updates
        """
        start_time = time.time()
        
        try:
            # Delegate to adapter
            result = self._adapter.invoke(message, **kwargs)
            
            # Record tool calls from adapter
            if "tool_calls" in result:
                for call in result["tool_calls"]:
                    self._tool_calls.append({
                        "name": call.get("name", "unknown"),
                        "arguments": call.get("arguments", {}),
                        "result": call.get("result"),
                        "timestamp": time.time(),
                    })
            
            # Record memory updates
            if "memory_updates" in result:
                self._memory_updates.extend(result["memory_updates"])
            
            duration_ms = (time.time() - start_time) * 1000
            logger.debug(f"Agent invoke completed in {duration_ms:.1f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Agent invoke failed: {e}")
            raise
    
    def get_memory(self) -> dict:
        """Extract current memory state from agent."""
        if self._adapter:
            return self._adapter.get_memory()
        return {}
    
    def set_memory(self, memory: dict) -> None:
        """Set memory state (for replay)."""
        if self._adapter:
            self._adapter.set_memory(memory)
    
    def get_tool_calls(self) -> list[dict]:
        """Get all recorded tool calls."""
        return self._tool_calls.copy()
    
    def get_memory_updates(self) -> list[dict]:
        """Get all recorded memory updates."""
        return self._memory_updates.copy()
