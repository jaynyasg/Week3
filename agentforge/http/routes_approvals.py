from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from agentforge.http.auth import get_store, require_operator
from agentforge.http.schemas import ApprovalRequest
from agentforge.models.finding import FindingStatus
from agentforge.reporting.vulnerability_report import (
    build_regression_case,
    render_vulnerability_report,
)

router = APIRouter()


@router.get("/operator/findings")
def list_findings(
    status: FindingStatus | None = Query(default=None),
    operator: str = Depends(require_operator),
    store=Depends(get_store),
):
    findings = store.list_findings(status=status)
    return {
        "operator": operator,
        "findings": [finding.model_dump(mode="json") for finding in findings],
    }


@router.post("/operator/findings/{finding_id}/approval")
def approve_finding(
    finding_id: str,
    body: ApprovalRequest,
    operator: str = Depends(require_operator),
    store=Depends(get_store),
):
    if body.decision not in {
        FindingStatus.APPROVED,
        FindingStatus.REJECTED,
        FindingStatus.NEEDS_MORE_EVIDENCE,
    }:
        raise HTTPException(status_code=400, detail="invalid approval decision")
    try:
        finding = store.get_finding(finding_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="finding not found") from exc
    finding.apply_approval(
        operator=operator,
        decision=body.decision,
        rationale=body.rationale,
    )
    if body.decision == FindingStatus.APPROVED:
        store.save_regression_case(finding.finding_id, build_regression_case(finding))
        finding.status = FindingStatus.REGRESSION_QUEUED
    store.save_finding(finding)
    store.save_report(finding.finding_id, render_vulnerability_report(finding))
    return finding.model_dump(mode="json")
