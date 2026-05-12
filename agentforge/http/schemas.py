from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from agentforge.models.finding import FindingStatus


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: FindingStatus
    rationale: str


class ReadinessResponse(BaseModel):
    status: str
    operator_auth_configured: bool
    target_configured: bool
    targets: list[str]
    artifact_dir: str
    evidence_environment: str
    provider_mode: str
    provider_configured: bool
    langfuse_enabled: bool
    langfuse_configured: bool
