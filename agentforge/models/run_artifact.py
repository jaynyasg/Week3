from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from agentforge.models.finding import Finding


class TargetExchange(BaseModel):
    case_id: str
    target_alias: str
    target_url: str
    request_summary: dict[str, Any] = Field(default_factory=dict)
    response_status: int | None = None
    response_summary: dict[str, Any] = Field(default_factory=dict)
    latency_ms: float | None = None
    error: str | None = None


class RunArtifact(BaseModel):
    run_id: str = Field(default_factory=lambda: f"run-{uuid4().hex[:12]}")
    campaign_id: str
    target_alias: str
    evidence_environment: str = "development"
    status: str = "completed"
    budget_usd: float = 0.0
    estimated_cost_usd: float = 0.0
    model_provider: str = "deterministic"
    model_name: str = "deterministic"
    judge_model_provider: str = "deterministic"
    judge_model_name: str = "deterministic"
    refusal_count: int = 0
    skipped_count: int = 0
    exchanges: list[TargetExchange] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    langfuse_trace_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    def finish(self) -> "RunArtifact":
        self.completed_at = datetime.now(UTC)
        return self
