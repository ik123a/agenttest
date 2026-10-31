"""Exercise real judge consumers with offline provider responses."""

import json
import sys
from types import ModuleType, SimpleNamespace

import pytest

from agenttest.assertions.hybrid import HybridAssertions
from agenttest.assertions.output_asserts import OutputAssertions
from agenttest.utils.llm_judge import LLMJudge


@pytest.fixture
def provider_response(monkeypatch):
    """Replace the external provider boundary, never the evaluator itself."""
    def install(content):
        provider = ModuleType("litellm")
        provider.completion = lambda **kwargs: SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )
        monkeypatch.setitem(sys.modules, "litellm", provider)

    return install


@pytest.fixture(params=["output", "hybrid", "utility"])
def assert_judgment(request):
    if request.param == "output":
        return lambda: OutputAssertions().assert_output_matches(
            "Agent answer", llm_judge="Meets the requirements"
        )
    if request.param == "hybrid":
        return lambda: HybridAssertions().assert_hybrid(
            "Agent answer", llm_judge="Meets the requirements"
        )
    return lambda: LLMJudge().assert_output("Agent answer", "Meets the requirements")


# Every response here is invalid under the schema requested in the judge prompts.
# In particular, strings and numbers must never be accepted through truthiness.
INVALID_RESPONSES = [
    '{"passed": "false", "score": 0.8, "reasoning": "Rejected"}',
    '{"passed": "true", "score": 0.8, "reasoning": "Accepted"}',
    '{"passed": 1, "score": 0.8, "reasoning": "Accepted"}',
    '{"passed": 0, "score": 0.8, "reasoning": "Rejected"}',
    '{"passed": null, "score": 0.8, "reasoning": "Rejected"}',
    '{"passed": [true], "score": 0.8, "reasoning": "Accepted"}',
    '{"score": 0.8, "reasoning": "Missing verdict"}',
    '{"passed": true, "score": -0.1, "reasoning": "Invalid score"}',
    '{"passed": true, "score": 1.1, "reasoning": "Invalid score"}',
    '{"passed": true, "score": NaN, "reasoning": "Invalid score"}',
    '{"passed": true, "score": Infinity, "reasoning": "Invalid score"}',
    '{"passed": true, "score": "0.8", "reasoning": "Invalid score"}',
    '{"passed": true, "score": true, "reasoning": "Invalid score"}',
    '{"passed": true, "score": null, "reasoning": "Invalid score"}',
    '{"passed": true, "reasoning": "Missing score"}',
    '{"passed": true, "score": 0.8, "reasoning": null}',
    '{"passed": true, "score": 0.8}',
    '[]',
    'null',
    'true',
    'not JSON',
]


@pytest.mark.parametrize("content", INVALID_RESPONSES)
def test_assertions_reject_malformed_judgments(content, provider_response, assert_judgment):
    provider_response(content)

    with pytest.raises(AssertionError):
        assert_judgment()


@pytest.mark.parametrize("content", INVALID_RESPONSES)
def test_evaluate_fails_closed_for_malformed_judgments(content, provider_response):
    provider_response(content)

    result = LLMJudge().evaluate("Agent answer", "Meets the requirements")

    assert result.passed is False
    assert result.score == 0.0
    assert isinstance(result.reasoning, str)


@pytest.mark.parametrize("passed", [True, False])
@pytest.mark.parametrize("score", [0, 0.5, 1])
def test_assertions_honor_boolean_verdicts(passed, score, provider_response, assert_judgment):
    provider_response(json.dumps({"passed": passed, "score": score, "reasoning": "Judgment"}))

    if passed:
        assert_judgment()
    else:
        with pytest.raises(AssertionError, match="Judgment"):
            assert_judgment()


@pytest.mark.parametrize("passed", [True, False])
@pytest.mark.parametrize("score", [0, 0.5, 1])
def test_evaluate_preserves_valid_judgments(passed, score, provider_response):
    provider_response(json.dumps({"passed": passed, "score": score, "reasoning": "Judgment"}))

    result = LLMJudge().evaluate("Agent answer", "Meets the requirements")

    assert result.passed is passed
    assert result.score == score
    assert result.reasoning == "Judgment"
