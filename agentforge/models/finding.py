from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Verdict(str, Enum):
    SAFE = "safe"
    VULNERABLE = "vulnerable"
    PARTIAL = "partial"
    INCONCLUSIVE = "inconclusive"
    ERROR = "error"


class FindingStatus(str, Enum):
    DRAFT = "draft"
    NEEDS_APPROVAL = "needs_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_MORE_EVIDENCE = "needs_more_evidence"
    REGRESSION_QUEUED = "regression_queued"


class ApprovalRecord(BaseModel):
    operator: str
    decision: FindingStatus
    rationale: str
    decided_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Finding(BaseModel):
    finding_id: str = Field(default_factory=lambda: f"find-{uuid4().hex[:12]}")
    run_id: str
    case_id: str
    title: str
    category: str
    framework_refs: list[str] = Field(default_factory=list)
    verdict: Verdict
    severity: str = "medium"
    status: FindingStatus = FindingStatus.DRAFT
    confidence: float = 0.0
    judge_mode: str = "deterministic"
    rationale: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    approval_history: list[ApprovalRecord] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def requires_human_approval(self) -> bool:
        if self.severity.lower() in {"high", "critical"}:
            return True
        if self.verdict in {Verdict.PARTIAL, Verdict.INCONCLUSIVE}:
            return True
        return self.judge_mode == "llm"

    def with_default_status(self) -> "Finding":
        if self.verdict == Verdict.SAFE:
            self.status = FindingStatus.REJECTED
        elif self.requires_human_approval():
            self.status = FindingStatus.NEEDS_APPROVAL
        else:
            self.status = FindingStatus.APPROVED
        self.updated_at = datetime.now(UTC)
        return self

    def apply_approval(
        self,
        *,
        operator: str,
        decision: FindingStatus,
        rationale: str,
    ) -> "Finding":
        if decision not in {
            FindingStatus.APPROVED,
            FindingStatus.REJECTED,
            FindingStatus.NEEDS_MORE_EVIDENCE,
        }:
            raise ValueError("approval decision must finalize or request more evidence")
        self.status = decision
        self.approval_history.append(
            ApprovalRecord(operator=operator, decision=decision, rationale=rationale)
        )
        self.updated_at = datetime.now(UTC)
        return self
