"""
Built-in mock tools for common external services.

Provides pre-configured mocks for HTTP requests, file I/O, and database
operations to simplify testing of agents that use these services.
"""

from __future__ import annotations

import json
from typing import Any


class MockHTTPTool:
    """
    Mock HTTP requests with configurable responses.
    
    Usage:
        mock = MockHTTPTool()
        mock.set_response("https://api.example.com/data", {"result": "ok"})
        result = mock.execute("http_get", url="https://api.example.com/data")
    """
    
    def __init__(self) -> None:
        self._responses: dict[str, Any] = {}
        self._calls: list[dict] = []
    
    def set_response(self, url: str, response: Any, status_code: int = 200) -> None:
        """Set mock response for a URL."""
        self._responses[url] = {
            "response": response,
            "status_code": status_code,
        }
    
    def execute(self, method: str, url: str, **kwargs: Any) -> dict:
        """
        Execute mock HTTP request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional request params
            
        Returns:
            Mock response dict
        """
        self._calls.append({
            "method": method,
            "url": url,
            "kwargs": kwargs,
        })
        
        if url in self._responses:
            return self._responses[url]
        
        return {
            "response": None,
            "status_code": 404,
            "error": f"No mock configured for {url}",
        }
    
    def get_calls(self) -> list[dict]:
        """Get all recorded HTTP calls."""
        return self._calls.copy()


class MockFileTool:
    """
    Mock file I/O operations.
    
    Usage:
        mock = MockFileTool()
        mock.set_file_content("/path/to/file.txt", "file content")
        content = mock.execute("read_file", path="/path/to/file.txt")
    """
    
    def __init__(self) -> None:
        self._files: dict[str, str | bytes] = {}
        self._calls: list[dict] = []
    
    def set_file_content(self, path: str, content: str | bytes) -> None:
        """Set mock file content."""
        self._files[path] = content
    
    def execute(self, operation: str, path: str, **kwargs: Any) -> Any:
        """
        Execute mock file operation.
        
        Args:
            operation: Operation type (read_file, write_file, exists)
            path: File path
            **kwargs: Additional params
            
        Returns:
            Operation result
        """
        self._calls.append({
            "operation": operation,
            "path": path,
            "kwargs": kwargs,
        })
        
        if operation == "read_file":
            if path in self._files:
                return {"content": self._files[path], "exists": True}
            return {"content": None, "exists": False, "error": "File not found"}
        
        elif operation == "write_file":
            self._files[path] = kwargs.get("content", "")
            return {"success": True}
        
        elif operation == "exists":
            return {"exists": path in self._files}
        
        return {"error": f"Unknown operation: {operation}"}
    
    def get_calls(self) -> list[dict]:
        """Get all recorded file operations."""
        return self._calls.copy()


class MockDBTool:
    """
    Mock database queries.
    
    Usage:
        mock = MockDBTool()
        mock.set_query_result("SELECT * FROM users", [{"id": 1, "name": "Alice"}])
        result = mock.execute("query", sql="SELECT * FROM users")
    """
    
    def __init__(self) -> None:
        self._results: dict[str, Any] = {}
        self._calls: list[dict] = []
    
    def set_query_result(self, sql: str, result: Any) -> None:
        """Set mock result for SQL query."""
        self._results[sql] = result
    
    def execute(self, operation: str, sql: str = "", **kwargs: Any) -> Any:
        """
        Execute mock database operation.
        
        Args:
            operation: Operation type (query, execute)
            sql: SQL query
            **kwargs: Additional params
            
        Returns:
            Query result
        """
        self._calls.append({
            "operation": operation,
            "sql": sql,
            "kwargs": kwargs,
        })
        
        if sql in self._results:
            return {"rows": self._results[sql], "success": True}
        
        return {"rows": [], "success": True, "note": "No mock result configured"}
    
    def get_calls(self) -> list[dict]:
        """Get all recorded database operations."""
        return self._calls.copy()
