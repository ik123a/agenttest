"""
Abstract base adapter for agent frameworks.

Defines the interface that all agent adapters must implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAgentAdapter(ABC):
    """
    Abstract adapter for agent frameworks.
    
    All adapters must implement these methods to allow AgentTest
    to work with different agent frameworks (LangChain, LlamaIndex, etc.).
    """
    
    def __init__(self, agent: Any) -> None:
        """
        Initialize adapter.
        
        Args:
            agent: The agent instance to adapt
        """
        self.agent = agent
        self._mock_registry = None
    
    def set_mock_registry(self, registry: Any) -> None:
        """Set the mock tool registry."""
        self._mock_registry = registry
    
    @abstractmethod
    def invoke(self, message: str, **kwargs: Any) -> dict:
        """
        Run agent with message, return structured result.
        
        Args:
            message: User message
            **kwargs: Additional arguments
            
        Returns:
            Dict with keys:
                - output: Agent's response text
                - tool_calls: List of tool call dicts
                - memory_updates: List of memory update dicts
        """
        ...
    
    @abstractmethod
    def get_memory(self) -> dict:
        """
        Extract current memory state.
        
        Returns:
            Dict representing agent's memory
        """
        ...
    
    @abstractmethod
    def set_memory(self, memory: dict) -> None:
        """
        Set memory state (for replay).
        
        Args:
            memory: Memory state dict
        """
        ...
    
    @abstractmethod
    def get_tools(self) -> list[str]:
        """
        List available tools.
        
        Returns:
            List of tool names
        """
        ...
