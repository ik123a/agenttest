"""
Scenario runner for executing multi-step test scenarios.

Runs scenario steps sequentially, executing assertions after each step
and collecting results.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from agenttest.scenarios.loader import Scenario, Step

logger = logging.getLogger(__name__)


@dataclass
class StepResult:
    """
    Result of executing a single scenario step.
    
    Attributes:
        step_num: Step number (1-indexed)
        user_input: User message sent
        output: Agent's response
        assertions_passed: List of passed assertion descriptions
        assertions_failed: List of failed assertion descriptions
        error: Exception if step failed
    """
    step_num: int
    user_input: str
    output: str
    assertions_passed: list[str] = field(default_factory=list)
    assertions_failed: list[str] = field(default_factory=list)
    error: Exception | None = None


@dataclass
class ScenarioResult:
    """
    Result of executing a complete scenario.
    
    Attributes:
        scenario: Scenario name
        steps: List of step results
        passed: Overall pass/fail status
        total_assertions: Total assertions attempted
        passed_assertions: Assertions that passed
    """
    scenario: str
    steps: list[StepResult]
    passed: bool
    total_assertions: int = 0
    passed_assertions: int = 0


class ScenarioRunner:
    """
    Execute scenario steps and validate assertions.
    
    Runs multi-step agent interactions and verifies expected behavior
    after each step using the AgentTest assertion library.
    """
    
    def __init__(self, agent_test: Any) -> None:
        """
        Initialize scenario runner.
        
        Args:
            agent_test: AgentTest instance
        """
        self.test = agent_test
    
    def run(self, scenario: Scenario) -> ScenarioResult:
        """
        Execute all steps in a scenario.
        
        Args:
            scenario: Scenario to execute
            
        Returns:
            ScenarioResult with pass/fail status
        """
        logger.info(f"Running scenario: {scenario.name}")
        
        step_results: list[StepResult] = []
        all_passed = True
        total_assertions = 0
        passed_assertions = 0
        
        for i, step in enumerate(scenario.steps, 1):
            result = self.run_step(i, step)
            step_results.append(result)
            
            total_assertions += len(result.assertions_passed) + len(result.assertions_failed)
            passed_assertions += len(result.assertions_passed)
            
            if result.assertions_failed or result.error:
                all_passed = False
        
        scenario_result = ScenarioResult(
            scenario=scenario.name,
            steps=step_results,
            passed=all_passed,
            total_assertions=total_assertions,
            passed_assertions=passed_assertions,
        )
        
        logger.info(
            f"Scenario '{scenario.name}': {'PASSED' if all_passed else 'FAILED'} "
            f"({passed_assertions}/{total_assertions} assertions)"
        )
        
        return scenario_result
    
    def run_step(self, step_num: int, step: Step) -> StepResult:
        """
        Execute a single scenario step.
        
        Args:
            step_num: Step number
            step: Step to execute
            
        Returns:
            StepResult with assertions results
        """
        result = StepResult(
            step_num=step_num,
            user_input=step.user,
            output="",
        )
        
        try:
            # Execute agent
            output = self.test.run(step.user)
            result.output = output
            
            # Run assertions
            if step.assert_tool_called:
                self._run_tool_assertion(result, step.assert_tool_called)
            
            if step.assert_memory:
                self._run_memory_assertion(result, step.assert_memory)
            
            if step.assert_output_matches:
                self._run_output_assertion(result, step.assert_output_matches)
                
        except Exception as e:
            result.error = e
            result.assertions_failed.append(f"Step execution failed: {e}")
            logger.error(f"Step {step_num} failed: {e}")
        
        return result
    
    def _run_tool_assertion(self, result: StepResult, config: dict) -> None:
        """Run tool call assertion."""
        try:
            name = config.get("name")
            times = config.get("times")
            args_contains = config.get("arguments")
            
            self.test.assert_tool_called(name, times=times, args_contains=args_contains)
            result.assertions_passed.append(f"tool_called({name})")
            
        except AssertionError as e:
            result.assertions_failed.append(f"tool_called: {e}")
    
    def _run_memory_assertion(self, result: StepResult, config: dict) -> None:
        """Run memory assertion."""
        try:
            for key, value in config.items():
                self.test.assert_memory_contains(key=key, value=value)
                result.assertions_passed.append(f"memory_contains({key})")
                
        except AssertionError as e:
            result.assertions_failed.append(f"memory: {e}")
    
    def _run_output_assertion(self, result: StepResult, config: str | dict) -> None:
        """Run output assertion."""
        try:
            if isinstance(config, str):
                self.test.assert_output_matches(regex=config)
            elif isinstance(config, dict):
                self.test.assert_output_matches(
                    regex=config.get("regex"),
                    llm_judge=config.get("llm_judge"),
                )
            result.assertions_passed.append("output_matches")
            
        except AssertionError as e:
            result.assertions_failed.append(f"output: {e}")
