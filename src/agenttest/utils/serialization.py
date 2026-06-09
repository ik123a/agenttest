"""
Serialization utilities for trace data.

Provides msgpack-based serialization for compact trace storage.
"""

from __future__ import annotations

import json
from typing import Any


def serialize_trace(data: dict) -> bytes:
    """
    Serialize trace data to bytes.
    
    Uses msgpack if available, falls back to JSON.
    
    Args:
        data: Trace data dict
        
    Returns:
        Serialized bytes
    """
    try:
        import msgpack
        return msgpack.packb(data, use_bin_type=True)
    except ImportError:
        # Fallback to JSON
        return json.dumps(data, default=str).encode("utf-8")


def deserialize_trace(data: bytes) -> dict:
    """
    Deserialize trace data from bytes.
    
    Args:
        data: Serialized bytes
        
    Returns:
        Deserialized dict
    """
    try:
        import msgpack
        return msgpack.unpackb(data, raw=False)
    except ImportError:
        # Fallback to JSON
        return json.loads(data.decode("utf-8"))


def serialize_event(event: dict) -> str:
    """
    Serialize a single event to JSON string.
    
    Args:
        event: Event dict
        
    Returns:
        JSON string
    """
    return json.dumps(event, default=str)


def deserialize_event(data: str) -> dict:
    """
    Deserialize a single event from JSON string.
    
    Args:
        data: JSON string
        
    Returns:
        Event dict
    """
    return json.loads(data)
