"""
Memory state assertions for verifying agent memory.

Provides assertions to check agent memory contents, size, and
semantic similarity for testing conversational context.
"""

from __future__ import annotations

import re
from typing import Any


class MemoryAssertions:
    """
    Assertions for agent memory state.
    
    Works with agent adapters to inspect memory backends.
    """
    
    def __init__(self, proxy: Any):
        """
        Initialize memory assertions.
        
        Args:
            proxy: AgentProxy instance for accessing agent memory
        """
        self._proxy = proxy
    
    def assert_memory_contains(self, key: str | None = None, value: Any = None) -> None:
        """
        Assert agent memory contains specific key/value.
        
        Args:
            key: Memory key to check (if None, checks for value in any key)
            value: Expected value (if None, just checks key exists)
            
        Raises:
            AssertionError: If assertion fails
        """
        memory = self._proxy.get_memory()
        
        if key is not None:
            if key not in memory:
                raise AssertionError(
                    f"Memory does not contain key '{key}'. "
                    f"Available keys: {list(memory.keys())}"
                )
            
            if value is not None:
                actual = memory[key]
                if actual != value:
                    raise AssertionError(
                        f"Memory['{key}'] = {actual!r}, expected {value!r}"
                    )
        else:
            # Check if value exists in any key
            found = False
            for k, v in memory.items():
                if v == value:
                    found = True
                    break
            
            if not found:
                raise AssertionError(
                    f"Value {value!r} not found in memory. "
                    f"Memory state: {memory}"
                )
    
    def assert_memory_not_contains(self, key: str) -> None:
        """
        Assert memory does NOT contain key.
        
        Args:
            key: Key that should not exist
            
        Raises:
            AssertionError: If key exists
        """
        memory = self._proxy.get_memory()
        
        if key in memory:
            raise AssertionError(
                f"Memory contains key '{key}' with value {memory[key]!r}, "
                f"but it should not."
            )
    
    def assert_memory_size(self, min_size: int | None = None, max_size: int | None = None) -> None:
        """
        Assert memory has expected number of entries.
        
        Args:
            min_size: Minimum number of entries (inclusive)
            max_size: Maximum number of entries (inclusive)
            
        Raises:
            AssertionError: If size constraint violated
        """
        memory = self._proxy.get_memory()
        size = len(memory)
        
        if min_size is not None and size < min_size:
            raise AssertionError(
                f"Memory has {size} entries, expected at least {min_size}."
            )
        
        if max_size is not None and size > max_size:
            raise AssertionError(
                f"Memory has {size} entries, expected at most {max_size}."
            )
    
    def assert_memory_regex(self, key: str, pattern: str) -> None:
        """
        Assert memory value matches regex pattern.
        
        Args:
            key: Memory key
            pattern: Regex pattern to match
            
        Raises:
            AssertionError: If assertion fails
        """
        memory = self._proxy.get_memory()
        
        if key not in memory:
            raise AssertionError(f"Memory does not contain key '{key}'.")
        
        value = str(memory[key])
        
        if not re.search(pattern, value):
            raise AssertionError(
                f"Memory['{key}'] = {value!r} does not match pattern {pattern!r}"
            )
    
    def assert_memory_json_schema(self, key: str, schema: dict) -> None:
        """
        Assert memory value conforms to JSON schema.
        
        Args:
            key: Memory key
            schema: JSON schema to validate against
            
        Raises:
            AssertionError: If validation fails
        """
        try:
            import jsonschema
        except ImportError:
            raise ImportError(
                "jsonschema package required for schema validation. "
                "Install with: pip install jsonschema"
            )
        
        memory = self._proxy.get_memory()
        
        if key not in memory:
            raise AssertionError(f"Memory does not contain key '{key}'.")
        
        try:
            jsonschema.validate(memory[key], schema)
        except jsonschema.ValidationError as e:
            raise AssertionError(
                f"Memory['{key}'] failed schema validation: {e.message}"
            )
    
    def get_memory_state(self) -> dict:
        """Return current memory state as dict."""
        return self._proxy.get_memory()
