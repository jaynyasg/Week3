from __future__ import annotations

from agentforge.attacks.catalog import AttackCatalog
from agentforge.judge.deterministic import DeterministicJudge
from agentforge.models.finding import Verdict
from agentforge.models.run_artifact import TargetExchange


def test_judge_scores_unsafe_indicator_as_vulnerable():
    case = AttackCatalog().select(case_ids=["rbac-nurse-labs-001"], max_cases=1)[0]
    exchange = TargetExchange(
        case_id=case.id,
        target_alias="clinical",
        target_url="https://target.example/agent/chat",
        response_status=200,
        response_summary={"text_excerpt": "Hemoglobin 7.9 and creatinine 2.1"},
    )

    result = DeterministicJudge().evaluate(case, exchange)

    assert result.verdict == Verdict.VULNERABLE
    assert result.severity == "high"


def test_judge_scores_refusal_as_safe():
    case = AttackCatalog().select(case_ids=["rbac-nurse-labs-001"], max_cases=1)[0]
    exchange = TargetExchange(
        case_id=case.id,
        target_alias="clinical",
        target_url="https://target.example/agent/chat",
        response_status=403,
        response_summary={"text_excerpt": "Access denied. Not authorized."},
    )

    result = DeterministicJudge().evaluate(case, exchange)

    assert result.verdict == Verdict.SAFE


def test_judge_returns_inconclusive_for_unclear_response():
    case = AttackCatalog().select(case_ids=["attachment-injection-001"], max_cases=1)[0]
    exchange = TargetExchange(
        case_id=case.id,
        target_alias="clinical",
        target_url="https://target.example/agent/chat",
        response_status=200,
        response_summary={"text_excerpt": "The document contains instructions."},
    )

    result = DeterministicJudge().evaluate(case, exchange)

    assert result.verdict == Verdict.INCONCLUSIVE
