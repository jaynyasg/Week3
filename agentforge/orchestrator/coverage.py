from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable

from agentforge.models.campaign import AttackCase
from agentforge.models.finding import Finding, FindingStatus, Verdict
from agentforge.models.run_artifact import RunArtifact

_VERDICT_ORDER = [
    Verdict.SAFE.value,
    Verdict.VULNERABLE.value,
    Verdict.PARTIAL.value,
    Verdict.INCONCLUSIVE.value,
    Verdict.ERROR.value,
]
_VERDICT_WEIGHTS = {
    Verdict.VULNERABLE.value: 4.0,
    Verdict.PARTIAL.value: 3.0,
    Verdict.ERROR.value: 2.0,
    Verdict.INCONCLUSIVE.value: 1.0,
}
_STATUS_WEIGHTS = {
    FindingStatus.APPROVED.value: 3.0,
    FindingStatus.NEEDS_APPROVAL.value: 2.0,
    FindingStatus.NEEDS_MORE_EVIDENCE.value: 2.0,
    FindingStatus.REGRESSION_QUEUED.value: 1.0,
}
_SEVERITY_WEIGHTS = {
    "critical": 2.0,
    "high": 1.0,
}


def _enum_value(value: Any) -> str:
    return getattr(value, "value", str(value))


def _new_category_bucket(category: str) -> dict[str, Any]:
    return {
        "category": category,
        "available_case_ids": [],
        "available_case_count": 0,
        "tested_case_ids": [],
        "tested_case_count": 0,
        "untested_case_ids": [],
        "untested_case_count": 0,
        "coverage_ratio": 0.0,
        "exchange_count": 0,
        "finding_count": 0,
        "verdict_counts": {verdict: 0 for verdict in _VERDICT_ORDER},
        "finding_status_counts": {},
        "weak_surface_score": 0.0,
        "last_run_id": None,
    }


def _count_finding(bucket: dict[str, Any], finding: Finding) -> None:
    verdict = _enum_value(finding.verdict)
    status = _enum_value(finding.status)
    severity = finding.severity.lower()
    bucket["finding_count"] += 1
    bucket["verdict_counts"][verdict] = bucket["verdict_counts"].get(verdict, 0) + 1
    status_counts = bucket["finding_status_counts"]
    status_counts[status] = status_counts.get(status, 0) + 1
    bucket["weak_surface_score"] += _VERDICT_WEIGHTS.get(verdict, 0.0)
    bucket["weak_surface_score"] += _STATUS_WEIGHTS.get(status, 0.0)
    bucket["weak_surface_score"] += _SEVERITY_WEIGHTS.get(severity, 0.0)


def build_coverage_summary(
    cases: Iterable[AttackCase],
    runs: Iterable[RunArtifact],
    findings: Iterable[Finding] | None = None,
    *,
    evidence_environment: str | None = None,
) -> dict[str, Any]:
    case_list = list(cases)
    case_by_id = {case.id: case for case in case_list}
    categories: dict[str, dict[str, Any]] = {}
    tested_by_category: dict[str, set[str]] = defaultdict(set)
    verdict_totals = Counter({verdict: 0 for verdict in _VERDICT_ORDER})

    for case in case_list:
        bucket = categories.setdefault(case.category, _new_category_bucket(case.category))
        bucket["available_case_ids"].append(case.id)

    run_list = [
        run
        for run in runs
        if evidence_environment is None
        or run.evidence_environment == evidence_environment
    ]
    run_ids = {run.run_id for run in run_list}
    canonical_findings = {
        finding.finding_id: finding
        for finding in findings or []
        if finding.run_id in run_ids
    }
    findings_by_run_case: dict[tuple[str, str], list[Finding]] = defaultdict(list)

    for finding in canonical_findings.values():
        findings_by_run_case[(finding.run_id, finding.case_id)].append(finding)

    for run in run_list:
        for finding in run.findings:
            if finding.finding_id in canonical_findings:
                continue
            findings_by_run_case[(finding.run_id, finding.case_id)].append(finding)

    seen_run_cases: set[tuple[str, str]] = set()
    sorted_runs = sorted(
        run_list,
        key=lambda run: run.completed_at or run.created_at,
    )
    for run in sorted_runs:
        for exchange in run.exchanges:
            run_case_key = (run.run_id, exchange.case_id)
            seen_run_cases.add(run_case_key)
            case = case_by_id.get(exchange.case_id)
            run_case_findings = findings_by_run_case.get(run_case_key, [])
            category = (
                case.category
                if case is not None
                else run_case_findings[0].category
                if run_case_findings
                else "uncataloged"
            )
            bucket = categories.setdefault(category, _new_category_bucket(category))
            tested_by_category[category].add(exchange.case_id)
            bucket["exchange_count"] += 1
            bucket["last_run_id"] = run.run_id
            if run_case_findings:
                for finding in run_case_findings:
                    _count_finding(bucket, finding)
                    verdict_totals[_enum_value(finding.verdict)] += 1
            else:
                bucket["verdict_counts"][Verdict.SAFE.value] += 1
                verdict_totals[Verdict.SAFE.value] += 1

    for (run_id, case_id), run_case_findings in findings_by_run_case.items():
        if (run_id, case_id) in seen_run_cases:
            continue
        for finding in run_case_findings:
            category = finding.category
            bucket = categories.setdefault(category, _new_category_bucket(category))
            tested_by_category[category].add(case_id)
            bucket["last_run_id"] = run_id
            _count_finding(bucket, finding)
            verdict_totals[_enum_value(finding.verdict)] += 1

    category_summaries: list[dict[str, Any]] = []
    for category, bucket in categories.items():
        available_case_ids = bucket["available_case_ids"]
        tested_case_ids = sorted(tested_by_category.get(category, set()))
        untested_case_ids = [
            case_id for case_id in available_case_ids if case_id not in tested_case_ids
        ]
        available_count = len(available_case_ids)
        tested_count = len(tested_case_ids)
        bucket["available_case_count"] = available_count
        bucket["tested_case_ids"] = tested_case_ids
        bucket["tested_case_count"] = tested_count
        bucket["untested_case_ids"] = untested_case_ids
        bucket["untested_case_count"] = len(untested_case_ids)
        bucket["coverage_ratio"] = (
            round(tested_count / available_count, 3) if available_count else 0.0
        )
        bucket["finding_status_counts"] = dict(sorted(bucket["finding_status_counts"].items()))
        bucket["weak_surface_score"] = round(bucket["weak_surface_score"], 3)
        category_summaries.append(bucket)

    category_summaries.sort(key=lambda item: item["category"])
    weakest_categories = [
        {
            "category": item["category"],
            "weak_surface_score": item["weak_surface_score"],
            "verdict_counts": item["verdict_counts"],
            "finding_status_counts": item["finding_status_counts"],
            "last_run_id": item["last_run_id"],
        }
        for item in sorted(
            category_summaries,
            key=lambda item: (-item["weak_surface_score"], item["category"]),
        )
        if item["weak_surface_score"] > 0
    ]
    coverage_gaps = [
        {
            "category": item["category"],
            "untested_case_ids": item["untested_case_ids"],
            "untested_case_count": item["untested_case_count"],
            "available_case_count": item["available_case_count"],
            "tested_case_count": item["tested_case_count"],
        }
        for item in category_summaries
        if item["untested_case_count"] > 0
    ]

    return {
        "evidence_environment": evidence_environment,
        "categories": category_summaries,
        "coverage_gaps": coverage_gaps,
        "weakest_categories": weakest_categories,
        "totals": {
            "category_count": len(category_summaries),
            "available_case_count": sum(
                item["available_case_count"] for item in category_summaries
            ),
            "tested_case_count": sum(
                item["tested_case_count"] for item in category_summaries
            ),
            "untested_case_count": sum(
                item["untested_case_count"] for item in category_summaries
            ),
            "exchange_count": sum(item["exchange_count"] for item in category_summaries),
            "finding_count": sum(item["finding_count"] for item in category_summaries),
            "verdict_counts": dict(verdict_totals),
            "weak_surface_score": round(
                sum(item["weak_surface_score"] for item in category_summaries),
                3,
            ),
        },
    }
