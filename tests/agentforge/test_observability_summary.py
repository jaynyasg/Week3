from __future__ import annotations

from agentforge.attacks.catalog import AttackCatalog
from agentforge.models.finding import Finding, FindingStatus, Verdict
from agentforge.models.run_artifact import RunArtifact, TargetExchange
from agentforge.observability.summary import build_observability_summary


def test_observability_summary_answers_pdf_questions():
    cases = AttackCatalog().load_cases()
    run = RunArtifact(
        run_id="run-summary",
        campaign_id="camp-summary",
        target_alias="clinical-copilot",
        evidence_environment="deployed",
        estimated_cost_usd=0.01,
        exchanges=[
            TargetExchange(
                case_id="attachment-injection-001",
                target_alias="clinical-copilot",
                target_url="https://target.example/agent/chat",
                response_status=500,
            )
        ],
    )
    finding = Finding(
        run_id=run.run_id,
        case_id="attachment-injection-001",
        title="Attachment server error",
        category="attachment_prompt_injection",
        verdict=Verdict.PARTIAL,
        severity="medium",
        status=FindingStatus.NEEDS_APPROVAL,
        confidence=0.7,
        rationale="Target returned 500 on a security path.",
    )
    validation = {
        "validation_id": "regval-summary",
        "created_at": "2026-05-14T12:00:00+00:00",
        "target_change_id": "deploy-1",
        "summary": {
            "total": 1,
            "resolved": 0,
            "reappeared": 1,
            "needs_review": 0,
            "missing_case": 0,
        },
    }

    summary = build_observability_summary(
        cases=cases,
        runs=[run],
        findings=[finding],
        regression_cases=[{"finding_id": finding.finding_id}],
        regression_validations=[validation],
        evidence_environment="deployed",
        metrics_snapshot={"campaigns_total": 1},
    )

    assert summary["coverage"]["totals"]["tested_case_count"] == 1
    assert summary["answers"]["verdict_counts"]["partial"] == 1
    assert summary["findings"]["status_counts"]["needs_approval"] == 1
    assert summary["regressions"]["aggregate"]["reappeared"] == 1
    assert summary["cost"]["estimated_total_usd"] == 0.01
    assert summary["metrics"]["campaigns_total"] == 1
    assert summary["agent_activity_order"][-1]["agent"] == "Observability"


def test_observability_summary_handles_empty_artifacts():
    summary = build_observability_summary(
        cases=[],
        runs=[],
        findings=[],
        regression_cases=[],
        regression_validations=[],
        evidence_environment="deployed",
    )

    assert summary["coverage"]["totals"]["category_count"] == 0
    assert summary["cost"]["average_run_usd"] == 0.0
    assert summary["regressions"]["latest_validation"] is None
