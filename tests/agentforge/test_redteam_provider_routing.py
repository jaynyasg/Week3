from __future__ import annotations

from agentforge.attacks.catalog import AttackCatalog
from agentforge.config import AgentForgeSettings
from agentforge.redteam.providers import DeterministicRedTeamProvider, create_redteam_provider


def test_default_provider_is_deterministic_without_live_key(settings):
    provider = create_redteam_provider(settings)

    assert isinstance(provider, DeterministicRedTeamProvider)


def test_deterministic_provider_returns_case_without_cost():
    case = AttackCatalog().select(case_ids=["rbac-nurse-labs-001"], max_cases=1)[0]
    result = DeterministicRedTeamProvider().mutate(case)

    assert result.case.id == case.id
    assert result.estimated_cost_usd == 0
    assert result.refusal is False


def test_live_groq_provider_selected_when_configured(tmp_path):
    settings = AgentForgeSettings(
        operator_token="test-token",
        artifact_dir=tmp_path / "evals",
        target_urls={"clinical": "https://target.example"},
        provider_mode="live",
        groq_api_key="secret",
    )

    provider = create_redteam_provider(settings)

    assert provider.provider == "groq"
    assert provider.model == "llama-3.1-8b-instant"
