"""
Hybrid assertions combining deterministic checks with LLM-based evaluation.

Allows running both deterministic assertions and LLM judge in a single call,
with configurable pass requirements.
"""

from __future__ import annotations

from typing import Any, Callable


class HybridAssertions:
    """
    Combine deterministic checks with LLM-based evaluation.
    
    Useful when you need both exact matching (deterministic) and semantic
    understanding (LLM judge) in a single assertion.
    """
    
    def __init__(self, llm_model: str = "gpt-3.5-turbo"):
        """
        Initialize hybrid assertions.
        
        Args:
            llm_model: Model to use for LLM judge
        """
        self._llm_model = llm_model
    
    def assert_hybrid(
        self,
        output: str,
        deterministic: list[tuple[Callable, tuple, dict]] | None = None,
        llm_judge: str | None = None,
        require_both: bool = True,
    ) -> None:
        """
        Run deterministic assertions AND LLM judge.
        
        Args:
            output: Agent output to validate
            deterministic: List of (func, args, kwargs) tuples for deterministic checks
            llm_judge: Natural language criteria for LLM evaluation
            require_both: If True, both must pass. If False, either passes.
            
        Raises:
            AssertionError: If validation fails
        """
        det_passed = True
        det_errors = []
        
        llm_passed = True
        llm_error = None
        
        # Run deterministic assertions
        if deterministic:
            for func, args, kwargs in deterministic:
                try:
                    func(output, *args, **kwargs)
                except AssertionError as e:
                    det_passed = False
                    det_errors.append(str(e))
        
        # Run LLM judge
        if llm_judge:
            try:
                self._run_llm_judge(output, llm_judge)
            except AssertionError as e:
                llm_passed = False
                llm_error = str(e)
        
        # Evaluate combined result
        if require_both:
            if not det_passed and not llm_passed:
                raise AssertionError(
                    f"Both deterministic and LLM assertions failed.\n"
                    f"Deterministic errors: {det_errors}\n"
                    f"LLM error: {llm_error}"
                )
            elif not det_passed:
                raise AssertionError(
                    f"Deterministic assertions failed: {det_errors}"
                )
            elif not llm_passed:
                raise AssertionError(
                    f"LLM judge failed: {llm_error}"
                )
        else:
            if not det_passed and not llm_passed:
                raise AssertionError(
                    f"Both deterministic and LLM assertions failed.\n"
                    f"Deterministic errors: {det_errors}\n"
                    f"LLM error: {llm_error}"
                )
    
    def _run_llm_judge(self, output: str, criteria: str) -> None:
        """Run LLM judge evaluation."""
        try:
            import json
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
                    f"LLM judge failed: {result.get('reasoning', 'No reasoning')}"
                )
                
        except json.JSONDecodeError:
            raise AssertionError(f"Failed to parse LLM response: {result_text}")
        except Exception as e:
            if isinstance(e, AssertionError):
                raise
            raise AssertionError(f"LLM judge error: {e}")
