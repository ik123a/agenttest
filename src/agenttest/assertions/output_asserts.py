"""
Output validation assertions for agent responses.

Provides assertions to validate agent output against regex patterns,
JSON schemas, substring presence, length constraints, and LLM judges.
"""

from __future__ import annotations

import json
import re
from typing import Any


class OutputAssertions:
    """
    Assertions for agent output validation.
    
    Supports multiple validation strategies:
    - Regex pattern matching
    - JSON schema validation
    - Substring presence
    - Length constraints
    - LLM-based evaluation
    """
    
    def __init__(self, llm_model: str = "gpt-3.5-turbo"):
        """
        Initialize output assertions.
        
        Args:
            llm_model: Model to use for LLM judge evaluations
        """
        self._llm_model = llm_model
    
    def assert_output_matches(
        self,
        output: str,
        regex: str | None = None,
        json_schema: dict | None = None,
        llm_judge: str | None = None,
    ) -> None:
        """
        Validate agent output.
        
        Args:
            output: Agent output to validate
            regex: Regex pattern to match
            json_schema: JSON schema for validation
            llm_judge: Natural language criteria for LLM evaluation
            
        Raises:
            AssertionError: If any validation fails
        """
        if output is None:
            raise AssertionError("Agent output is None")
        
        if regex:
            if not re.search(regex, output):
                raise AssertionError(
                    f"Output does not match regex {regex!r}. "
                    f"Output: {output[:200]}..."
                )
        
        if json_schema:
            self._validate_json_schema(output, json_schema)
        
        if llm_judge:
            self._validate_with_llm(output, llm_judge)
    
    def assert_output_contains(self, output: str, *substrs: str) -> None:
        """
        Assert output contains all substrings.
        
        Args:
            output: Agent output
            *substrs: Substrings that must be present
            
        Raises:
            AssertionError: If any substring missing
        """
        if output is None:
            raise AssertionError("Agent output is None")
        
        missing = []
        for substr in substrs:
            if substr not in output:
                missing.append(substr)
        
        if missing:
            raise AssertionError(
                f"Output missing substrings: {missing}. "
                f"Output: {output[:200]}..."
            )
    
    def assert_output_not_contains(self, output: str, *substrs: str) -> None:
        """
        Assert output does NOT contain any of the substrings.
        
        Args:
            output: Agent output
            *substrs: Substrings that must not be present
            
        Raises:
            AssertionError: If any substring found
        """
        if output is None:
            return  # None doesn't contain anything
        
        found = []
        for substr in substrs:
            if substr in output:
                found.append(substr)
        
        if found:
            raise AssertionError(
                f"Output contains forbidden substrings: {found}. "
                f"Output: {output[:200]}..."
            )
    
    def assert_output_length(
        self,
        output: str,
        min_len: int | None = None,
        max_len: int | None = None,
    ) -> None:
        """
        Assert output length constraints.
        
        Args:
            output: Agent output
            min_len: Minimum length (inclusive)
            max_len: Maximum length (inclusive)
            
        Raises:
            AssertionError: If length constraint violated
        """
        if output is None:
            raise AssertionError("Agent output is None")
        
        length = len(output)
        
        if min_len is not None and length < min_len:
            raise AssertionError(
                f"Output length is {length}, expected at least {min_len}."
            )
        
        if max_len is not None and length > max_len:
            raise AssertionError(
                f"Output length is {length}, expected at most {max_len}."
            )
    
    def assert_output_is_json(self, output: str) -> None:
        """
        Assert output is valid JSON.
        
        Args:
            output: Agent output
            
        Raises:
            AssertionError: If not valid JSON
        """
        if output is None:
            raise AssertionError("Agent output is None")
        
        try:
            json.loads(output)
        except json.JSONDecodeError as e:
            raise AssertionError(f"Output is not valid JSON: {e}")
    
    def assert_output_json_value(self, output: str, key: str, expected: Any) -> None:
        """
        Assert specific value in JSON output.
        
        Args:
            output: Agent output (must be JSON)
            key: JSON key path (dot-separated for nested)
            expected: Expected value
            
        Raises:
            AssertionError: If value doesn't match
        """
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            raise AssertionError("Output is not valid JSON")
        
        # Navigate nested keys
        keys = key.split(".")
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                raise AssertionError(
                    f"Key '{key}' not found in JSON output. "
                    f"Available keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}"
                )
        
        if current != expected:
            raise AssertionError(
                f"JSON['{key}'] = {current!r}, expected {expected!r}"
            )
    
    def _validate_json_schema(self, output: str, schema: dict) -> None:
        """Validate output against JSON schema."""
        try:
            import jsonschema
        except ImportError:
            raise ImportError(
                "jsonschema package required for schema validation. "
                "Install with: pip install jsonschema"
            )
        
        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            raise AssertionError("Output is not valid JSON")
        
        try:
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as e:
            raise AssertionError(f"Output failed schema validation: {e.message}")
    
    def _validate_with_llm(self, output: str, criteria: str) -> None:
        """Validate output using LLM judge."""
        try:
            import litellm
        except ImportError:
            raise ImportError(
                "litellm package required for LLM judge. "
                "Install with: pip install litellm"
            )
        
        prompt = f"""You are an AI judge evaluating an agent's output against criteria.

Agent Output:
{output}

Criteria:
{criteria}

Respond with ONLY a JSON object in this exact format:
{{"passed": true/false, "score": 0.0-1.0, "reasoning": "brief explanation"}}"""
        
        try:
            response = litellm.completion(
                model=self._llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            
            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)
            
            if not result.get("passed", False):
                raise AssertionError(
                    f"LLM judge failed: {result.get('reasoning', 'No reasoning provided')}"
                )
                
        except json.JSONDecodeError:
            raise AssertionError(f"Failed to parse LLM judge response: {result_text}")
        except Exception as e:
            if isinstance(e, AssertionError):
                raise
            raise AssertionError(f"LLM judge error: {e}")
