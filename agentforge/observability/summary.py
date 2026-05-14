from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from agentforge.models.campaign import AttackCase
from agentforge.models.finding import Finding
from agentforge.models.run_artifact import RunArtifact
from agentforge.orchestrator.coverage import build_coverage_summary


def _latest_validation(validations: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not validations:
        return None
    return sorted(
        validations,
        key=lambda item: str(item.get("created_at") or item.get("validation_id") or ""),
    )[-1]


def _regression_summary(
    regression_cases: Iterable[dict[str, Any]],
    validations: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    case_list = list(regression_cases)
    validation_list = list(validations)
    aggregate = Counter(
        {
            "total": 0,
            "resolved": 0,
            "reappeared": 0,
            "needs_review": 0,
            "missing_case": 0,
        }
    )
    for validation in validation_list:
        aggregate.update(validation.get("summary", {}))
    latest = _latest_validation(validation_list)
    return {
        "case_count": len(case_list),
        "validation_count": len(validation_list),
        "aggregate": dict(aggregate),
        "latest_validation": {
            "validation_id": latest.get("validation_id"),
            "target_change_id": latest.get("target_change_id"),
            "summary": latest.get("summary", {}),
        }
        if latest
        else None,
    }


def _finding_status_counts(findings: Iterable[Finding]) -> dict[str, int]:
    return dict(Counter(finding.status.value for finding in findings))


def _agent_activity_order(run_count: int, finding_count: int, validation_count: int) -> list[dict[str, str]]:
    activity = [
        {
            "agent": "Orchestrator",
            "activity": "Selects cases from coverage gaps, weak-surface score, budget, and explicit operator request.",
        },
        {
            "agent": "Red Team",
            "activity": "Loads or mutates adversarial cases within allowlisted targets and campaign budget.",
        },
        {
            "agent": "Target Runner",
            "activity": "Calls the deployed Clinical Co-Pilot target and records PHI-safe exchange metadata.",
        },
        {
            "agent": "Judge",
            "activity": "Scores target behavior independently from the red-team generator.",
        },
    ]
    if finding_count:
        activity.append(
            {
                "agent": "Human Approver",
                "activity": "Approves, rejects, or requests more evidence for high-risk or ambiguous findings.",
            }
        )
        activity.append(
            {
                "agent": "Documentation",
                "activity": "Renders vulnerability reports from canonical finding and run artifacts.",
            }
        )
    if validation_count:
        activity.append(
            {
                "agent": "Regression Harness",
                "activity": "Replays approved regression cases after target changes and stores validation status.",
            }
        )
    activity.append(
        {
            "agent": "Observability",
            "activity": f"Summarizes {run_count} runs without exposing raw clinical transcript text.",
        }
    )
    return activity


def build_observability_summary(
    *,
    cases: Iterable[AttackCase],
    runs: Iterable[RunArtifact],
    findings: Iterable[Finding],
    regression_cases: Iterable[dict[str, Any]],
    regression_validations: Iterable[dict[str, Any]],
    evidence_environment: str,
    metrics_snapshot: dict[str, int] | None = None,
) -> dict[str, Any]:
    case_list = list(cases)
    run_list = [
        run for run in runs if run.evidence_environment == evidence_environment
    ]
    finding_list = list(findings)
    validation_list = list(regression_validations)
    coverage = build_coverage_summary(
        case_list,
        run_list,
        finding_list,
        evidence_environment=evidence_environment,
    )
    regressions = _regression_summary(regression_cases, validation_list)
    total_cost = round(sum(run.estimated_cost_usd for run in run_list), 6)
    finding_status_counts = _finding_status_counts(finding_list)
    open_statuses = {
        "draft",
        "needs_approval",
        "needs_more_evidence",
        "regression_queued",
    }
    open_finding_count = sum(
        count
        for status, count in finding_status_counts.items()
        if status in open_statuses
    )

    return {
        "evidence_environment": evidence_environment,
        "coverage": coverage,
        "findings": {
            "total": len(finding_list),
            "status_counts": finding_status_counts,
            "open_count": open_finding_count,
            "resolved_count": finding_status_counts.get("rejected", 0)
            + regressions["aggregate"].get("resolved", 0),
        },
        "cost": {
            "estimated_total_usd": total_cost,
            "run_count": len(run_list),
            "average_run_usd": round(total_cost / len(run_list), 6)
            if run_list
            else 0.0,
        },
        "regressions": regressions,
        "agent_activity_order": _agent_activity_order(
            len(run_list),
            len(finding_list),
            len(validation_list),
        ),
        "metrics": metrics_snapshot or {},
        "answers": {
            "categories_tested": coverage["totals"]["tested_case_count"],
            "category_count": coverage["totals"]["category_count"],
            "untested_case_count": coverage["totals"]["untested_case_count"],
            "weakest_categories": [
                item["category"] for item in coverage["weakest_categories"]
            ],
            "verdict_counts": coverage["totals"]["verdict_counts"],
            "finding_status_counts": finding_status_counts,
            "regression_validation_count": regressions["validation_count"],
        },
    }
