"""
LLM judge for evaluating agent outputs.

Uses a language model to evaluate agent outputs against natural language
criteria for flexible, semantic testing.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class JudgeResult:
    """
    Result from LLM judge evaluation.
    
    Attributes:
        passed: Whether criteria was met
        score: Confidence score (0.0 - 1.0)
        reasoning: Explanation of the judgment
    """
    passed: bool
    score: float
    reasoning: str


def parse_judge_response(result_text: str) -> JudgeResult:
    """Parse a judge response without coercing malformed fields into success."""
    data = json.loads(result_text)
    if not isinstance(data, dict):
        raise ValueError("LLM judge response must be a JSON object")

    passed = data.get("passed")
    if type(passed) is not bool:
        raise ValueError("LLM judge 'passed' must be a boolean")

    score = data.get("score")
    if type(score) not in (int, float) or not 0.0 <= score <= 1.0:
        raise ValueError("LLM judge 'score' must be a finite number between 0 and 1")

    reasoning = data.get("reasoning")
    if not isinstance(reasoning, str):
        raise ValueError("LLM judge 'reasoning' must be a string")

    return JudgeResult(passed=passed, score=float(score), reasoning=reasoning)


class LLMJudge:
    """
    Use LLM to evaluate agent outputs.
    
    Provides flexible, semantic evaluation of agent responses against
    natural language criteria using litellm for provider-agnostic access.
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """
        Initialize LLM judge.
        
        Args:
            model: Model to use for evaluation (via litellm)
        """
        self.model = model
    
    def evaluate(self, output: str, criteria: str) -> JudgeResult:
        """
        Evaluate output against criteria.
        
        Args:
            output: Agent output to evaluate
            criteria: Natural language evaluation criteria
            
        Returns:
            JudgeResult with pass/fail, score, and reasoning
        """
        try:
            import litellm
        except ImportError:
            raise ImportError(
                "litellm package required for LLM judge. "
                "Install with: pip install litellm"
            )
        
        prompt = f"""You are an expert AI evaluator. Assess the following agent output against the given criteria.

AGENT OUTPUT:
{output}

EVALUATION CRITERIA:
{criteria}

Provide your evaluation as a JSON object with exactly these fields:
- "passed": boolean (true if output meets criteria, false otherwise)
- "score": float between 0.0 and 1.0 (confidence in your judgment)
- "reasoning": string (brief explanation of your evaluation)

Respond ONLY with the JSON object, no other text."""
        
        try:
            response = litellm.completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=200,
            )
            
            result_text = response.choices[0].message.content.strip()
            
            return parse_judge_response(result_text)
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response: {result_text}")
            return JudgeResult(
                passed=False,
                score=0.0,
                reasoning=f"Failed to parse LLM response: {result_text}",
            )
        except Exception as e:
            logger.error(f"LLM judge error: {e}")
            return JudgeResult(
                passed=False,
                score=0.0,
                reasoning=f"LLM judge error: {e}",
            )
    
    def assert_output(self, output: str, criteria: str) -> None:
        """
        Assert output meets criteria, raising AssertionError if not.
        
        Args:
            output: Agent output
            criteria: Evaluation criteria
            
        Raises:
            AssertionError: If output doesn't meet criteria
        """
        result = self.evaluate(output, criteria)
        
        if not result.passed:
            raise AssertionError(
                f"LLM judge failed (score: {result.score:.2f}): {result.reasoning}"
            )
