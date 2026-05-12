from __future__ import annotations

from fastapi.testclient import TestClient


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
