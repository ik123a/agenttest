"""
Scenario loader for YAML/JSON test definitions.

Loads multi-step test scenarios from files and parses them into
structured Scenario objects for execution.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Step:
    """
    A single step in a test scenario.
    
    Attributes:
        user: User message to send
        assert_tool_called: Tool assertion config
        assert_memory: Memory assertion config
        assert_output_matches: Output assertion config
    """
    user: str
    assert_tool_called: dict | None = None
    assert_memory: dict | None = None
    assert_output_matches: str | dict | None = None


@dataclass
class Scenario:
    """
    A complete test scenario with multiple steps.
    
    Attributes:
        name: Scenario name
        steps: List of test steps
        description: Optional description
        tags: Optional tags for filtering
    """
    name: str
    steps: list[Step]
    description: str = ""
    tags: list[str] = field(default_factory=list)


class ScenarioLoader:
    """
    Load test scenarios from YAML/JSON files.
    
    Supports both YAML and JSON formats for defining multi-step
    agent test scenarios.
    """
    
    @staticmethod
    def load(path: str) -> list[Scenario]:
        """
        Load scenarios from file.
        
        Args:
            path: Path to YAML or JSON file
            
        Returns:
            List of Scenario objects
            
        Raises:
            FileNotFoundError: If file not found
            ValueError: If file format not supported
        """
        file_path = Path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Scenario file not found: {path}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Determine format
        if file_path.suffix in (".yaml", ".yml"):
            return ScenarioLoader._parse_yaml(content)
        elif file_path.suffix == ".json":
            return ScenarioLoader._parse_json(content)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    @staticmethod
    def _parse_yaml(content: str) -> list[Scenario]:
        """Parse YAML content."""
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML required for YAML scenarios. "
                "Install with: pip install pyyaml"
            )
        
        data = yaml.safe_load(content)
        return ScenarioLoader._parse_data(data)
    
    @staticmethod
    def _parse_json(content: str) -> list[Scenario]:
        """Parse JSON content."""
        data = json.loads(content)
        return ScenarioLoader._parse_data(data)
    
    @staticmethod
    def _parse_data(data: Any) -> list[Scenario]:
        """Parse loaded data into scenarios."""
        scenarios = []
        
        # Handle single scenario or list
        if isinstance(data, dict):
            if "steps" in data:
                scenarios.append(ScenarioLoader._parse_scenario(data))
            elif "scenarios" in data:
                for s in data["scenarios"]:
                    scenarios.append(ScenarioLoader._parse_scenario(s))
            else:
                # Assume it's a single scenario with implicit structure
                scenarios.append(Scenario(name="unnamed", steps=[]))
        elif isinstance(data, list):
            for item in data:
                scenarios.append(ScenarioLoader._parse_scenario(item))
        
        return scenarios
    
    @staticmethod
    def _parse_scenario(data: dict) -> Scenario:
        """Parse a single scenario dict."""
        steps = []
        
        for step_data in data.get("steps", []):
            step = Step(
                user=step_data.get("user", ""),
                assert_tool_called=step_data.get("assert_tool_called"),
                assert_memory=step_data.get("assert_memory"),
                assert_output_matches=step_data.get("assert_output_matches"),
            )
            steps.append(step)
        
        return Scenario(
            name=data.get("name", "unnamed"),
            steps=steps,
            description=data.get("description", ""),
            tags=data.get("tags", []),
        )
    
    @staticmethod
    def from_dict(data: dict) -> Scenario:
        """
        Parse scenario dict directly.
        
        Args:
            data: Scenario dictionary
            
        Returns:
            Scenario object
        """
        return ScenarioLoader._parse_scenario(data)
