from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import httpx
import pytest

from agentforge.attacks.catalog import AttackCatalog
from agentforge.config import AgentForgeSettings
from agentforge.http.app import create_app
from agentforge.orchestrator.campaigns import CampaignExecutor
from agentforge.targets.clinical_copilot import ClinicalCoPilotClient


@pytest.fixture
def tmp_path(request) -> Path:
    safe_name = "".join(ch if ch.isalnum() else "-" for ch in request.node.name)
    root = (
        Path(__file__).resolve().parents[2]
        / ".pytest-tmp"
        / f"{safe_name}-{uuid4().hex[:8]}"
    )
    root.mkdir(parents=True, exist_ok=True)
    return root


@pytest.fixture
def settings(tmp_path: Path) -> AgentForgeSettings:
    return AgentForgeSettings(
        operator_token="test-token",
        artifact_dir=tmp_path / "evals",
        evidence_environment="deployed",
        target_urls={"clinical-copilot": "https://target.example"},
        provider_mode="deterministic",
        budget_usd=0.25,
        max_cases_per_campaign=2,
    )


def mock_target_client(settings: AgentForgeSettings, text: str, status_code: int = 200):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code,
            json={
                "assistant_message": text,
                "verified": True,
                "messages": [],
            },
            request=request,
        )

    app = create_app(settings)
    client = httpx.Client(transport=httpx.MockTransport(handler))
    app.state.executor = CampaignExecutor(
        settings=settings,
        catalog=AttackCatalog(),
        store=app.state.store,
        allowlist=app.state.allowlist,
        target_client=ClinicalCoPilotClient(settings, app.state.allowlist, client=client),
    )
    return app
