from __future__ import annotations

from agentforge.models.campaign import CampaignStartRequest


def test_campaign_execution_creates_deployed_finding_and_report(settings):
    from tests.agentforge.conftest import mock_target_client

    app = mock_target_client(
        settings,
        "Hemoglobin 7.9 and creatinine 2.1 are abnormal labs.",
    )

    run = app.state.executor.run(
        CampaignStartRequest(case_ids=["rbac-nurse-labs-001"], max_cases=1)
    )

    assert run.evidence_environment == "deployed"
    assert len(run.exchanges) == 1
    assert len(run.findings) == 1
    finding = run.findings[0]
    assert finding.status.value == "needs_approval"
    assert finding.evidence["expected_safe_behavior"]
    assert finding.evidence["target_role"] == "NURSE"
    assert (settings.artifact_dir / "reports" / f"{finding.finding_id}.md").exists()


def test_campaign_budget_halts_before_target_execution(settings):
    from tests.agentforge.conftest import mock_target_client

    app = mock_target_client(settings, "Hemoglobin 7.9")

    run = app.state.executor.run(
        CampaignStartRequest(
            case_ids=["rbac-nurse-labs-001"],
            max_cases=1,
            budget_usd=0.0,
        )
    )

    assert run.skipped_count == 1
    assert run.exchanges == []


def test_default_campaign_records_orchestrator_recommendations(settings):
    from tests.agentforge.conftest import mock_target_client

    app = mock_target_client(settings, "Access denied.")

    run = app.state.executor.run(CampaignStartRequest(max_cases=2))

    assert len(run.orchestrator_recommendations) == 2
    assert {item["reason"] for item in run.orchestrator_recommendations} == {
        "coverage_gap"
    }
    assert [item["case_id"] for item in run.orchestrator_recommendations] == [
        exchange.case_id for exchange in run.exchanges
    ]
