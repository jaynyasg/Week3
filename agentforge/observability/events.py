from __future__ import annotations

import logging
from typing import Any

from agentforge.models.run_artifact import RunArtifact

LOG_EXTRA_EVENT = "event"


def log_agentforge_event(
    logger: logging.Logger,
    event: str,
    *,
    fields: dict[str, Any] | None = None,
) -> None:
    safe_fields = dict(fields or {})
    extra = {LOG_EXTRA_EVENT: event, **safe_fields}
    flat = " ".join(f"{key}={value!r}" for key, value in sorted(safe_fields.items()))
    logger.info("agentforge_event event=%r %s", event, flat, extra=extra)


def build_run_event(run: RunArtifact) -> dict[str, Any]:
    severities = [finding.severity for finding in run.findings]
    statuses = [finding.status.value for finding in run.findings]
    return {
        "run_id": run.run_id,
        "campaign_id": run.campaign_id,
        "target_alias": run.target_alias,
        "evidence_environment": run.evidence_environment,
        "status": run.status,
        "model_provider": run.model_provider,
        "model_name": run.model_name,
        "judge_model_provider": run.judge_model_provider,
        "judge_model_name": run.judge_model_name,
        "estimated_cost_usd": round(run.estimated_cost_usd, 6),
        "refusal_count": run.refusal_count,
        "finding_count": len(run.findings),
        "finding_severities": sorted(set(severities)),
        "finding_statuses": sorted(set(statuses)),
    }
