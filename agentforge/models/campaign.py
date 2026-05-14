from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class AttackCase(BaseModel):
    id: str
    title: str
    category: str
    framework_refs: list[str] = Field(default_factory=list)
    target_role: str = "PHYSICIAN"
    patient_id: str = "demo-patient"
    user_message: str
    messages: list[dict[str, str]] = Field(default_factory=list)
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    expected_safe_behavior: str
    unsafe_indicators: list[str] = Field(default_factory=list)
    safe_indicators: list[str] = Field(default_factory=list)
    severity_if_vulnerable: str = "medium"
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CampaignPlan(BaseModel):
    campaign_id: str = Field(default_factory=lambda: f"camp-{uuid4().hex[:12]}")
    target_alias: str = "clinical-copilot"
    category: str | None = None
    case_ids: list[str] = Field(default_factory=list)
    max_cases: int = 5
    budget_usd: float = 0.25
    cases: list[AttackCase] = Field(default_factory=list)
    selection_reasons: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CampaignStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_alias: str | None = None
    category: str | None = None
    case_ids: list[str] = Field(default_factory=list)
    max_cases: int | None = None
    budget_usd: float | None = None
