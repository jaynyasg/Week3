from __future__ import annotations

from typing import Any, Iterable

from agentforge.models.campaign import AttackCase


def _case_recommendation(
    case: AttackCase,
    *,
    reason: str,
    bucket: dict[str, Any],
) -> dict[str, Any]:
    return {
        "case_id": case.id,
        "category": case.category,
        "title": case.title,
        "reason": reason,
        "weak_surface_score": bucket.get("weak_surface_score", 0.0),
        "tested_case_count": bucket.get("tested_case_count", 0),
        "available_case_count": bucket.get("available_case_count", 0),
    }


def recommend_next_cases(
    cases: Iterable[AttackCase],
    coverage_summary: dict[str, Any],
    *,
    max_cases: int = 5,
) -> list[dict[str, Any]]:
    case_by_id = {case.id: case for case in cases}
    buckets = {
        bucket["category"]: bucket
        for bucket in coverage_summary.get("categories", [])
    }
    recommendations: list[dict[str, Any]] = []
    selected_case_ids: set[str] = set()
    selected_categories: set[str] = set()

    def add(case_id: str, reason: str, bucket: dict[str, Any]) -> None:
        if len(recommendations) >= max_cases or case_id in selected_case_ids:
            return
        case = case_by_id.get(case_id)
        if case is None:
            return
        recommendations.append(_case_recommendation(case, reason=reason, bucket=bucket))
        selected_case_ids.add(case_id)
        selected_categories.add(case.category)

    gap_buckets = sorted(
        (bucket for bucket in buckets.values() if bucket.get("untested_case_ids")),
        key=lambda bucket: (
            bucket.get("tested_case_count", 0),
            -bucket.get("weak_surface_score", 0.0),
            bucket["category"],
        ),
    )
    for bucket in gap_buckets:
        if bucket["category"] in selected_categories:
            continue
        add(bucket["untested_case_ids"][0], "coverage_gap", bucket)

    weak_buckets = sorted(
        buckets.values(),
        key=lambda bucket: (
            -bucket.get("weak_surface_score", 0.0),
            bucket.get("tested_case_count", 0),
            bucket["category"],
        ),
    )
    for bucket in weak_buckets:
        if len(recommendations) >= max_cases:
            break
        candidate_ids = bucket.get("untested_case_ids") or bucket.get("available_case_ids") or []
        for case_id in candidate_ids:
            if case_id not in selected_case_ids:
                add(case_id, "weak_surface", bucket)
                break

    for case_id, case in case_by_id.items():
        if len(recommendations) >= max_cases:
            break
        bucket = buckets.get(
            case.category,
            {
                "weak_surface_score": 0.0,
                "tested_case_count": 0,
                "available_case_count": 1,
            },
        )
        add(case_id, "catalog_order", bucket)

    return recommendations
