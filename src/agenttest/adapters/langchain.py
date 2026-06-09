"""
LangChain adapter for AgentTest.

Provides integration with LangChain agents including LCEL chains,
AgentExecutor, and RunnableWithMessageHistory.
"""

from __future__ import annotations

import logging
from typing import Any, Protocol

from agenttest.adapters.base import BaseAgentAdapter

logger = logging.getLogger(__name__)


class LangChainAdapter(BaseAgentAdapter):
    """
    Adapter for LangChain agents.
    
    Supports:
    - AgentExecutor
    - LCEL chains with tools
    - RunnableWithMessageHistory
    
    Hooks into the agent's tool executor to intercept and mock tool calls.
    """
    
    def __init__(self, agent: Any) -> None:
        """
        Initialize LangChain adapter.
        
        Args:
            agent: LangChain agent (AgentExecutor, LCEL chain, etc.)
        """
        super().__init__(agent)
        self._tool_calls: list[dict] = []
        self._memory_updates: list[dict] = []
    
    def invoke(self, message: str, **kwargs: Any) -> dict:
        """
        Invoke LangChain agent.
        
        Args:
            message: User message
            **kwargs: Additional arguments (config, etc.)
            
        Returns:
            Structured result with output, tool_calls, memory_updates
        """
        self._tool_calls = []
        self._memory_updates = []
        
        try:
            # Handle different LangChain agent types
            if hasattr(self.agent, "invoke"):
                # LCEL chain or AgentExecutor
                # Try dict format first, fall back to string
                try:
                    result = self.agent.invoke(
                        {"input": message, **kwargs},
                        **{k: v for k, v in kwargs.items() if k != "input"},
                    )
                except (TypeError, AttributeError):
                    # Agent expects simple string input
                    result = self.agent.invoke(message, **kwargs)
            elif hasattr(self.agent, "run"):
                # Legacy AgentExecutor
                result = self.agent.run(message, **kwargs)
            else:
                raise ValueError(f"Unsupported LangChain agent type: {type(self.agent)}")
            
            # Extract output
            output = self._extract_output(result)
            
            # Extract tool calls if available
            if isinstance(result, dict):
                if "intermediate_steps" in result:
                    for step in result["intermediate_steps"]:
                        if hasattr(step, "__len__") and len(step) >= 2:
                            action, observation = step[0], step[1]
                            if hasattr(action, "tool"):
                                self._tool_calls.append({
                                    "name": action.tool,
                                    "arguments": getattr(action, "tool_input", {}),
                                    "result": observation,
                                })
            
            return {
                "output": output,
                "tool_calls": self._tool_calls,
                "memory_updates": self._memory_updates,
            }
            
        except Exception as e:
            logger.error(f"LangChain invoke failed: {e}")
            raise
    
    def _extract_output(self, result: Any) -> str:
        """Extract text output from LangChain result."""
        if isinstance(result, str):
            return result
        elif isinstance(result, dict):
            if "output" in result:
                return str(result["output"])
            elif "text" in result:
                return str(result["text"])
            elif "response" in result:
                return str(result["response"])
        elif hasattr(result, "content"):
            return str(result.content)
        elif hasattr(result, "text"):
            return str(result.text)
        return str(result)
    
    def get_memory(self) -> dict:
        """
        Extract memory from LangChain agent.
        
        Checks for common memory backends:
        - BaseChatMemory
        - ConversationBufferMemory
        - ConversationSummaryMemory
        """
        memory = {}
        
        # Check for memory attribute
        if hasattr(self.agent, "memory"):
            agent_memory = self.agent.memory
            
            if hasattr(agent_memory, "chat_memory"):
                # ConversationBufferMemory or similar
                messages = agent_memory.chat_memory.messages
                memory["messages"] = [
                    {"type": getattr(m, "type", "unknown"), "content": getattr(m, "content", "")}
                    for m in messages
                ]
            elif hasattr(agent_memory, "buffer"):
                memory["buffer"] = agent_memory.buffer
            elif hasattr(agent_memory, "variables"):
                memory.update(agent_memory.variables)
        
        # Check for message history in kwargs
        if hasattr(self.agent, "message_history"):
            memory["message_history"] = str(self.agent.message_history)
        
        return memory
    
    def set_memory(self, memory: dict) -> None:
        """Set memory state for replay."""
        if hasattr(self.agent, "memory"):
            agent_memory = self.agent.memory
            
            if hasattr(agent_memory, "chat_memory") and "messages" in memory:
                # Clear existing messages
                if hasattr(agent_memory.chat_memory, "clear"):
                    agent_memory.chat_memory.clear()
                
                # This is a simplified approach - real implementation would
                # need to reconstruct proper Message objects
                logger.warning("Memory set is simplified - may not fully restore state")
    
    def get_tools(self) -> list[str]:
        """List available tools from LangChain agent."""
        tools = []
        
        if hasattr(self.agent, "tools"):
            for tool in self.agent.tools:
                if hasattr(tool, "name"):
                    tools.append(tool.name)
                elif hasattr(tool, "__name__"):
                    tools.append(tool.__name__)
        
        return tools
