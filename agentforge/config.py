from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _parse_target_urls(raw_urls: str | None, raw_default: str | None) -> dict[str, str]:
    targets: dict[str, str] = {}
    raw_urls = (raw_urls or "").strip()
    if raw_urls:
        for chunk in raw_urls.split(","):
            item = chunk.strip()
            if not item:
                continue
            if "=" in item:
                alias, url = item.split("=", 1)
            else:
                alias, url = "clinical-copilot", item
            targets[alias.strip()] = url.strip().rstrip("/")
    raw_default = (raw_default or "").strip()
    if raw_default and "clinical-copilot" not in targets:
        targets["clinical-copilot"] = raw_default.rstrip("/")
    return targets


class AgentForgeSettings(BaseModel):
    operator_token: str = Field(default="dev-agentforge-token")
    artifact_dir: Path = Field(default=Path("evals"))
    evidence_environment: str = Field(default="development")
    target_urls: dict[str, str] = Field(default_factory=dict)
    target_chat_path: str = Field(default="/agent/chat")
    target_demo_bypass: bool = Field(default=True)
    target_authorization: str | None = Field(default=None)
    target_cookie: str | None = Field(default=None)
    provider_mode: str = Field(default="deterministic")
    redteam_provider: str = Field(default="groq")
    redteam_model: str = Field(default="llama-3.1-8b-instant")
    judge_provider: str = Field(default="openai")
    judge_model: str = Field(default="gpt-5-nano")
    groq_api_key: str | None = Field(default=None)
    openai_api_key: str | None = Field(default=None)
    budget_usd: float = Field(default=0.25)
    max_cases_per_campaign: int = Field(default=5)
    langfuse_enabled: bool = Field(default=False)
    langfuse_public_key: str | None = Field(default=None)
    langfuse_secret_key: str | None = Field(default=None)
    langfuse_base_url: str | None = Field(default=None)

    @classmethod
    def from_env(cls) -> "AgentForgeSettings":
        raw_langfuse_base = os.environ.get("LANGFUSE_BASE_URL") or os.environ.get(
            "LANGFUSE_HOST"
        )
        evidence_environment = os.environ.get(
            "AGENTFORGE_EVIDENCE_ENVIRONMENT", "development"
        )
        operator_token = os.environ.get("AGENTFORGE_OPERATOR_TOKEN")
        if operator_token is None and evidence_environment != "deployed":
            operator_token = "dev-agentforge-token"
        return cls(
            operator_token=operator_token or "",
            artifact_dir=Path(os.environ.get("AGENTFORGE_ARTIFACT_DIR", "evals")),
            evidence_environment=evidence_environment,
            target_urls=_parse_target_urls(
                os.environ.get("AGENTFORGE_TARGET_URLS"),
                os.environ.get("AGENTFORGE_TARGET_URL"),
            ),
            target_chat_path=os.environ.get(
                "AGENTFORGE_TARGET_CHAT_PATH", "/agent/chat"
            ),
            target_demo_bypass=_truthy(
                os.environ.get("AGENTFORGE_TARGET_DEMO_BYPASS", "1")
            ),
            target_authorization=os.environ.get("AGENTFORGE_TARGET_AUTHORIZATION"),
            target_cookie=os.environ.get("AGENTFORGE_TARGET_COOKIE"),
            provider_mode=os.environ.get("AGENTFORGE_PROVIDER_MODE", "deterministic"),
            redteam_provider=os.environ.get("AGENTFORGE_REDTEAM_PROVIDER", "groq"),
            redteam_model=os.environ.get(
                "AGENTFORGE_REDTEAM_MODEL", "llama-3.1-8b-instant"
            ),
            judge_provider=os.environ.get("AGENTFORGE_JUDGE_PROVIDER", "openai"),
            judge_model=os.environ.get("AGENTFORGE_JUDGE_MODEL", "gpt-5-nano"),
            groq_api_key=os.environ.get("GROQ_API_KEY"),
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            budget_usd=float(os.environ.get("AGENTFORGE_BUDGET_USD", "0.25")),
            max_cases_per_campaign=int(
                os.environ.get("AGENTFORGE_MAX_CASES_PER_CAMPAIGN", "5")
            ),
            langfuse_enabled=_truthy(os.environ.get("LANGFUSE_ENABLED", "0")),
            langfuse_public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
            langfuse_secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
            langfuse_base_url=raw_langfuse_base,
        )

    @property
    def default_target_alias(self) -> str | None:
        if not self.target_urls:
            return None
        return next(iter(self.target_urls))

    @property
    def target_configured(self) -> bool:
        return bool(self.target_urls)

    @property
    def provider_configured(self) -> bool:
        if self.provider_mode == "deterministic":
            return True
        return bool(self.groq_api_key or self.openai_api_key)

    @property
    def operator_auth_configured(self) -> bool:
        return bool(self.operator_token)

    @property
    def langfuse_configured(self) -> bool:
        return bool(
            self.langfuse_enabled
            and self.langfuse_public_key
            and self.langfuse_secret_key
        )
