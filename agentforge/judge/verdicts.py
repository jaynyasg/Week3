from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agentforge.models.finding import Verdict


class JudgeResult(BaseModel):
    verdict: Verdict
    severity: str = "medium"
    confidence: float = 0.0
    judge_mode: str = "deterministic"
    rationale: str
    evidence: dict[str, Any] = Field(default_factory=dict)
