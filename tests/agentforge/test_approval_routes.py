from __future__ import annotations

from fastapi.testclient import TestClient


def test_approval_route_promotes_high_severity_finding(settings):
    from tests.agentforge.conftest import mock_target_client

    app = mock_target_client(settings, "Hemoglobin 7.9 and creatinine 2.1.")
    client = TestClient(app)
    run = client.post(
        "/operator/campaigns",
        headers={
            "Authorization": "Bearer test-token",
            "X-AgentForge-Operator": "alice",
        },
        json={"case_ids": ["rbac-nurse-labs-001"], "max_cases": 1},
    ).json()
    finding_id = run["findings"][0]["finding_id"]

    queued = client.get(
        "/operator/findings?status=needs_approval",
        headers={"Authorization": "Bearer test-token"},
    ).json()
    assert queued["findings"][0]["finding_id"] == finding_id

    approved = client.post(
        f"/operator/findings/{finding_id}/approval",
        headers={
            "Authorization": "Bearer test-token",
            "X-AgentForge-Operator": "alice",
        },
        json={"decision": "approved", "rationale": "Evidence is clear."},
    )

    assert approved.status_code == 200
    assert approved.json()["status"] == "regression_queued"
    assert (settings.artifact_dir / "regression" / f"{finding_id}.json").exists()


def test_approval_route_allows_request_more_evidence(settings):
    from tests.agentforge.conftest import mock_target_client

    app = mock_target_client(settings, "The document contains instructions.")
    client = TestClient(app)
    run = client.post(
        "/operator/campaigns",
        headers={"Authorization": "Bearer test-token"},
        json={"case_ids": ["attachment-injection-001"], "max_cases": 1},
    ).json()
    finding_id = run["findings"][0]["finding_id"]

    response = client.post(
        f"/operator/findings/{finding_id}/approval",
        headers={"Authorization": "Bearer test-token"},
        json={"decision": "needs_more_evidence", "rationale": "Response is unclear."},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "needs_more_evidence"
