"""
LlamaIndex adapter for AgentTest.

Provides integration with LlamaIndex agents including AgentRunner
and ReActAgent.
"""

from __future__ import annotations

import logging
from typing import Any

from agenttest.adapters.base import BaseAgentAdapter

logger = logging.getLogger(__name__)


class LlamaIndexAdapter(BaseAgentAdapter):
    """
    Adapter for LlamaIndex agents.
    
    Supports:
    - AgentRunner
    - ReActAgent
    - SubQuestionQueryEngine
    """
    
    def __init__(self, agent: Any) -> None:
        """
        Initialize LlamaIndex adapter.
        
        Args:
            agent: LlamaIndex agent instance
        """
        super().__init__(agent)
        self._tool_calls: list[dict] = []
        self._memory_updates: list[dict] = []
    
    def invoke(self, message: str, **kwargs: Any) -> dict:
        """
        Invoke LlamaIndex agent.
        
        Args:
            message: User message
            **kwargs: Additional arguments
            
        Returns:
            Structured result
        """
        self._tool_calls = []
        self._memory_updates = []
        
        try:
            # Handle different LlamaIndex agent types
            if hasattr(self.agent, "chat"):
                # AgentRunner
                response = self.agent.chat(message, **kwargs)
            elif hasattr(self.agent, "query"):
                # QueryEngine or older agent
                response = self.agent.query(message, **kwargs)
            elif hasattr(self.agent, "step"):
                # ReActAgent
                response = self.agent.step(message, **kwargs)
            else:
                raise ValueError(f"Unsupported LlamaIndex agent type: {type(self.agent)}")
            
            # Extract output
            output = self._extract_output(response)
            
            # Extract tool calls if available
            if hasattr(response, "tool_calls"):
                for tc in response.tool_calls:
                    self._tool_calls.append({
                        "name": getattr(tc, "tool_name", "unknown"),
                        "arguments": getattr(tc, "tool_kwargs", {}),
                        "result": getattr(tc, "output", None),
                    })
            
            return {
                "output": output,
                "tool_calls": self._tool_calls,
                "memory_updates": self._memory_updates,
            }
            
        except Exception as e:
            logger.error(f"LlamaIndex invoke failed: {e}")
            raise
    
    def _extract_output(self, response: Any) -> str:
        """Extract text output from LlamaIndex response."""
        if hasattr(response, "response"):
            return str(response.response)
        elif hasattr(response, "text"):
            return str(response.text)
        elif isinstance(response, str):
            return response
        elif isinstance(response, dict):
            return response.get("response", response.get("text", str(response)))
        return str(response)
    
    def get_memory(self) -> dict:
        """
        Extract memory from LlamaIndex agent.
        
        Checks for ChatMemoryBuffer and other memory types.
        """
        memory = {}
        
        # Check for chat history
        if hasattr(self.agent, "chat_history"):
            history = self.agent.chat_history
            if hasattr(history, "get"):
                memory["chat_history"] = [
                    {"role": getattr(m, "role", "unknown"), "content": getattr(m, "content", "")}
                    for m in history.get_all()
                ] if hasattr(history, "get_all") else str(history)
        
        # Check for memory buffer
        if hasattr(self.agent, "memory"):
            agent_memory = self.agent.memory
            if hasattr(agent_memory, "get"):
                memory["memory_buffer"] = str(agent_memory.get())
        
        return memory
    
    def set_memory(self, memory: dict) -> None:
        """Set memory state for replay."""
        if hasattr(self.agent, "chat_history") and "chat_history" in memory:
            # Clear existing history
            if hasattr(self.agent.chat_history, "reset"):
                self.agent.chat_history.reset()
            logger.warning("Memory set is simplified - may not fully restore state")
    
    def get_tools(self) -> list[str]:
        """List available tools from LlamaIndex agent."""
        tools = []
        
        if hasattr(self.agent, "tools"):
            for tool in self.agent.tools:
                if hasattr(tool, "name"):
                    tools.append(tool.name)
                elif hasattr(tool, "metadata"):
                    tools.append(tool.metadata.name)
        
        return tools
