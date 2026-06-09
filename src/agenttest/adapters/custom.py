"""
Custom adapter for agents that don't use a specific framework.

Provides a generic adapter for agents following a simple interface.
"""

from __future__ import annotations

import logging
from typing import Any

from agenttest.adapters.base import BaseAgentAdapter

logger = logging.getLogger(__name__)


class CustomAdapter(BaseAgentAdapter):
    """
    Adapter for custom agents following a simple protocol.
    
    Expected agent interface:
    - agent.invoke(message) or agent.run(message) or agent(message)
    - Optional: agent.memory, agent.tools
    
    If the agent doesn't follow a standard interface, you can wrap it
    to conform to one of these patterns.
    """
    
    def __init__(self, agent: Any) -> None:
        """
        Initialize custom adapter.
        
        Args:
            agent: Custom agent instance
        """
        super().__init__(agent)
        self._tool_calls: list[dict] = []
        self._memory: dict = {}
    
    def invoke(self, message: str, **kwargs: Any) -> dict:
        """
        Invoke custom agent.
        
        Tries multiple invocation patterns:
        1. agent.invoke(message)
        2. agent.run(message)
        3. agent(message)
        """
        self._tool_calls = []
        
        try:
            # Try invoke pattern
            if hasattr(self.agent, "invoke"):
                result = self.agent.invoke(message, **kwargs)
            # Try run pattern
            elif hasattr(self.agent, "run"):
                result = self.agent.run(message, **kwargs)
            # Try callable pattern
            elif callable(self.agent):
                result = self.agent(message, **kwargs)
            else:
                raise ValueError(
                    f"Agent does not have invoke, run, or __call__ methods. "
                    f"Agent type: {type(self.agent)}"
                )
            
            # Extract output
            output = self._extract_output(result)
            
            # Try to extract tool calls from result
            if isinstance(result, dict):
                if "tool_calls" in result:
                    self._tool_calls = result["tool_calls"]
                elif "actions" in result:
                    self._tool_calls = result["actions"]
            
            return {
                "output": output,
                "tool_calls": self._tool_calls,
                "memory_updates": [],
            }
            
        except Exception as e:
            logger.error(f"Custom agent invoke failed: {e}")
            raise
    
    def _extract_output(self, result: Any) -> str:
        """Extract text output from agent result."""
        if isinstance(result, str):
            return result
        elif isinstance(result, dict):
            for key in ["output", "text", "response", "answer", "result"]:
                if key in result:
                    return str(result[key])
        elif hasattr(result, "text"):
            return str(result.text)
        elif hasattr(result, "content"):
            return str(result.content)
        elif hasattr(result, "__str__"):
            return str(result)
        return ""
    
    def get_memory(self) -> dict:
        """
        Extract memory from custom agent.
        
        Checks for common memory patterns.
        """
        memory = {}
        
        if hasattr(self.agent, "memory"):
            agent_memory = self.agent.memory
            
            if isinstance(agent_memory, dict):
                memory = agent_memory.copy()
            elif hasattr(agent_memory, "to_dict"):
                memory = agent_memory.to_dict()
            elif hasattr(agent_memory, "__dict__"):
                memory = {
                    k: v for k, v in agent_memory.__dict__.items()
                    if not k.startswith("_")
                }
            else:
                memory["memory"] = str(agent_memory)
        
        # Check for conversation history
        if hasattr(self.agent, "history"):
            history = self.agent.history
            if isinstance(history, list):
                memory["history"] = history
        
        return memory
    
    def set_memory(self, memory: dict) -> None:
        """Set memory state for replay."""
        if hasattr(self.agent, "memory"):
            if isinstance(self.agent.memory, dict):
                self.agent.memory.update(memory)
            elif hasattr(self.agent, "__dict__"):
                for k, v in memory.items():
                    setattr(self.agent, k, v)
    
    def get_tools(self) -> list[str]:
        """List available tools from custom agent."""
        tools = []
        
        if hasattr(self.agent, "tools"):
            tools_attr = self.agent.tools
            if isinstance(tools_attr, list):
                for tool in tools_attr:
                    if hasattr(tool, "name"):
                        tools.append(tool.name)
                    elif hasattr(tool, "__name__"):
                        tools.append(tool.__name__)
                    else:
                        tools.append(str(tool))
            elif isinstance(tools_attr, dict):
                tools = list(tools_attr.keys())
        
        return tools
