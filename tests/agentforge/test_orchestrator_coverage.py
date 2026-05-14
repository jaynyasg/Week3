from __future__ import annotations

from agentforge.attacks.catalog import AttackCatalog
from agentforge.models.finding import Finding, FindingStatus, Verdict
from agentforge.models.run_artifact import RunArtifact, TargetExchange
from agentforge.orchestrator.coverage import build_coverage_summary


def _bucket(summary: dict, category: str) -> dict:
    return next(item for item in summary["categories"] if item["category"] == category)


def test_coverage_summary_tracks_case_depth_and_safe_exchanges():
    cases = AttackCatalog().load_cases()
    run = RunArtifact(
        campaign_id="camp-test",
        target_alias="clinical-copilot",
        evidence_environment="deployed",
        exchanges=[
            TargetExchange(
                case_id="rbac-nurse-labs-001",
                target_alias="clinical-copilot",
                target_url="https://target.example",
                response_status=200,
            )
        ],
    )

    summary = build_coverage_summary(
        cases,
        [run],
        [],
        evidence_environment="deployed",
    )

    rbac = _bucket(summary, "rbac_phi_exfiltration")
    assert rbac["available_case_count"] >= 2
    assert rbac["tested_case_ids"] == ["rbac-nurse-labs-001"]
    assert "rbac-nurse-handoff-002" in rbac["untested_case_ids"]
    assert rbac["verdict_counts"]["safe"] == 1
    assert summary["totals"]["tested_case_count"] == 1
    assert summary["totals"]["untested_case_count"] >= 1


def test_coverage_summary_scores_unresolved_weak_surfaces():
    cases = AttackCatalog().load_cases()
    run = RunArtifact(
        run_id="run-weak",
        campaign_id="camp-test",
        target_alias="clinical-copilot",
        evidence_environment="deployed",
        exchanges=[
            TargetExchange(
                case_id="attachment-injection-001",
                target_alias="clinical-copilot",
                target_url="https://target.example",
                response_status=200,
            )
        ],
    )
    finding = Finding(
        run_id=run.run_id,
        case_id="attachment-injection-001",
        title="Uploaded document tries to override system policy",
        category="attachment_prompt_injection",
        verdict=Verdict.VULNERABLE,
        severity="high",
        status=FindingStatus.NEEDS_APPROVAL,
        confidence=0.95,
        rationale="Target followed the document instruction.",
        evidence={"unsafe_indicators": ["policy overridden"]},
    )

    summary = build_coverage_summary(
        cases,
        [run],
        [finding],
        evidence_environment="deployed",
    )

    attachment = _bucket(summary, "attachment_prompt_injection")
    assert attachment["finding_count"] == 1
    assert attachment["verdict_counts"]["vulnerable"] == 1
    assert attachment["finding_status_counts"]["needs_approval"] == 1
    assert attachment["weak_surface_score"] > 0
    assert summary["weakest_categories"][0]["category"] == "attachment_prompt_injection"


def test_coverage_summary_filters_to_submission_environment():
    cases = AttackCatalog().load_cases()
    local_run = RunArtifact(
        campaign_id="camp-local",
        target_alias="clinical-copilot",
        evidence_environment="development",
        exchanges=[
            TargetExchange(
                case_id="tool-patient-scope-001",
                target_alias="clinical-copilot",
                target_url="http://localhost",
                response_status=200,
            )
        ],
    )

    summary = build_coverage_summary(
        cases,
        [local_run],
        [],
        evidence_environment="deployed",
    )

    tool_scope = _bucket(summary, "tool_patient_scope_tampering")
    assert tool_scope["tested_case_count"] == 0
    assert tool_scope["verdict_counts"]["safe"] == 0
