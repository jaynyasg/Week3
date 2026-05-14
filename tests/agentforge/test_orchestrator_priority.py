from __future__ import annotations

from agentforge.attacks.catalog import AttackCatalog
from agentforge.models.finding import Finding, FindingStatus, Verdict
from agentforge.models.run_artifact import RunArtifact, TargetExchange
from agentforge.orchestrator.coverage import build_coverage_summary
from agentforge.orchestrator.priority import recommend_next_cases


def test_priority_recommends_untested_categories_first():
    cases = AttackCatalog().load_cases()
    summary = build_coverage_summary(
        cases,
        [],
        [],
        evidence_environment="deployed",
    )

    recommendations = recommend_next_cases(cases, summary, max_cases=3)

    assert len(recommendations) == 3
    assert {item["reason"] for item in recommendations} == {"coverage_gap"}
    assert len({item["category"] for item in recommendations}) == 3


def test_priority_returns_to_weak_surface_after_baseline_coverage():
    cases = AttackCatalog().load_cases()
    first_case_by_category = {}
    for case in cases:
        first_case_by_category.setdefault(case.category, case)
    exchanges = [
        TargetExchange(
            case_id=case.id,
            target_alias="clinical-copilot",
            target_url="https://target.example",
            response_status=200,
        )
        for case in first_case_by_category.values()
    ]
    run = RunArtifact(
        run_id="run-baseline",
        campaign_id="camp-test",
        target_alias="clinical-copilot",
        evidence_environment="deployed",
        exchanges=exchanges,
    )
    weak_case = first_case_by_category["attachment_prompt_injection"]
    finding = Finding(
        run_id=run.run_id,
        case_id=weak_case.id,
        title=weak_case.title,
        category=weak_case.category,
        verdict=Verdict.VULNERABLE,
        severity="high",
        status=FindingStatus.NEEDS_APPROVAL,
        confidence=0.9,
        rationale="Target followed the malicious document.",
        evidence={"unsafe_indicators": ["policy overridden"]},
    )
    summary = build_coverage_summary(
        cases,
        [run],
        [finding],
        evidence_environment="deployed",
    )

    recommendations = recommend_next_cases(cases, summary, max_cases=1)

    assert recommendations[0]["category"] == "attachment_prompt_injection"
    assert recommendations[0]["case_id"] == "attachment-injection-002"
    assert recommendations[0]["reason"] == "coverage_gap"
    assert recommendations[0]["weak_surface_score"] > 0
