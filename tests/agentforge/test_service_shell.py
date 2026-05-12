from __future__ import annotations

from fastapi.testclient import TestClient

from agentforge.config import AgentForgeSettings
from agentforge.http.app import create_app


def test_health_and_ready_report_configuration(settings):
    client = TestClient(create_app(settings))

    assert client.get("/health").json() == {"status": "ok"}
    ready = client.get("/ready").json()

    assert ready["status"] == "ready"
    assert ready["target_configured"] is True
    assert ready["evidence_environment"] == "deployed"
    assert ready["provider_mode"] == "deterministic"


def test_ready_degraded_without_target(tmp_path):
    settings = AgentForgeSettings(
        operator_token="test-token",
        artifact_dir=tmp_path / "evals",
        target_urls={},
    )
    client = TestClient(create_app(settings))

    ready = client.get("/ready").json()

    assert ready["status"] == "degraded"
    assert ready["target_configured"] is False


def test_deployed_env_does_not_default_operator_token(monkeypatch):
    monkeypatch.setenv("AGENTFORGE_EVIDENCE_ENVIRONMENT", "deployed")
    monkeypatch.delenv("AGENTFORGE_OPERATOR_TOKEN", raising=False)

    settings = AgentForgeSettings.from_env()

    assert settings.operator_token == ""
    assert settings.operator_auth_configured is False


def test_operator_routes_require_auth(settings):
    client = TestClient(create_app(settings))

    assert client.get("/operator/status").status_code == 401

    response = client.get(
        "/operator/status",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json()["redteam_model"] == "llama-3.1-8b-instant"
