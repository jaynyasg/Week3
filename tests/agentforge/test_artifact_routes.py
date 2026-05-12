from __future__ import annotations

from fastapi.testclient import TestClient


def test_artifact_route_returns_run_file(settings):
    from tests.agentforge.conftest import mock_target_client

    app = mock_target_client(settings, "Hemoglobin 7.9 and creatinine 2.1.")
    client = TestClient(app)
    run = client.post(
        "/operator/campaigns",
        headers={"Authorization": "Bearer test-token"},
        json={"case_ids": ["rbac-nurse-labs-001"], "max_cases": 1},
    ).json()

    response = client.get(
        f"/operator/artifacts/results/{run['run_id']}.json",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json()["run_id"] == run["run_id"]


def test_artifact_route_blocks_path_escape(settings):
    from tests.agentforge.conftest import mock_target_client

    app = mock_target_client(settings, "Access denied.")
    client = TestClient(app)

    response = client.get(
        "/operator/artifacts/../README.md",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code in {400, 404}
