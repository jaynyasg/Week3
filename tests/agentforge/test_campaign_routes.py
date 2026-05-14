from __future__ import annotations

from fastapi.testclient import TestClient

from agentforge.models.finding import Finding, FindingStatus, Verdict
from agentforge.reporting.vulnerability_report import build_regression_case


def test_campaign_route_runs_bounded_campaign(settings):
    from tests.agentforge.conftest import mock_target_client

    app = mock_target_client(settings, "Hemoglobin 7.9 and creatinine 2.1.")
    client = TestClient(app)

    response = client.post(
        "/operator/campaigns",
        headers={"Authorization": "Bearer test-token"},
        json={"case_ids": ["rbac-nurse-labs-001"], "max_cases": 1},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["evidence_environment"] == "deployed"
    assert body["findings"][0]["status"] == "needs_approval"


def test_campaign_route_rejects_target_url_override(settings):
    from tests.agentforge.conftest import mock_target_client

    app = mock_target_client(settings, "Access denied.")
    client = TestClient(app)

    response = client.post(
        "/operator/campaigns",
        headers={"Authorization": "Bearer test-token"},
        json={"target_url": "https://attacker.example"},
    )

    assert response.status_code == 422


def test_operator_status_exposes_coverage_recommendations(settings):
    from tests.agentforge.conftest import mock_target_client

    app = mock_target_client(settings, "Access denied.")
    client = TestClient(app)

    response = client.get(
        "/operator/status",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["coverage"]["totals"]["available_case_count"] >= 10
    assert body["coverage"]["totals"]["tested_case_count"] == 0
    assert body["next_campaign_recommendation"][0]["reason"] == "coverage_gap"
    assert body["next_campaign_recommendation"][0]["case_id"]
    assert body["regressions"]["case_count"] == 0
    assert body["regressions"]["validation_count"] == 0


def test_operator_regression_replay_validates_stored_case(settings):
    from tests.agentforge.conftest import mock_target_client

    app = mock_target_client(settings, "Access denied.")
    finding = Finding(
        run_id="run-final",
        case_id="rbac-nurse-labs-001",
        title="Nurse attempts to retrieve restricted lab values",
        category="rbac_phi_exfiltration",
        verdict=Verdict.VULNERABLE,
        severity="high",
        status=FindingStatus.REGRESSION_QUEUED,
        confidence=0.95,
        rationale="Prior target response disclosed restricted labs.",
    )
    app.state.store.save_regression_case(
        finding.finding_id,
        build_regression_case(finding),
    )
    client = TestClient(app)

    response = client.post(
        "/operator/regressions/replay",
        headers={"Authorization": "Bearer test-token"},
        json={
            "finding_ids": [finding.finding_id],
            "target_change_id": "deploy-2026-05-14",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["total"] == 1
    assert body["summary"]["resolved"] == 1
    assert body["target_change_id"] == "deploy-2026-05-14"
    assert body["results"][0]["status"] == "resolved"
    assert body["results"][0]["current_verdict"] == "safe"
    assert (
        settings.artifact_dir
        / "regression"
        / "validations"
        / f"{body['validation_id']}.json"
    ).exists()
