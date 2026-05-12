from __future__ import annotations

from typing import Any

from agentforge.config import AgentForgeSettings
from agentforge.models.run_artifact import RunArtifact


class LangfuseRecorder:
    def __init__(self, settings: AgentForgeSettings) -> None:
        self.settings = settings

    def build_payload(self, run: RunArtifact) -> dict[str, Any]:
        return {
            "trace_name": "agentforge-campaign",
            "trace_id": run.run_id,
            "metadata": {
                "campaign_id": run.campaign_id,
                "target_alias": run.target_alias,
                "evidence_environment": run.evidence_environment,
                "model_provider": run.model_provider,
                "model_name": run.model_name,
                "judge_model_provider": run.judge_model_provider,
                "judge_model_name": run.judge_model_name,
                "estimated_cost_usd": round(run.estimated_cost_usd, 6),
                "refusal_count": run.refusal_count,
            },
            "scores": [
                {
                    "name": "finding_count",
                    "value": len(run.findings),
                    "data_type": "NUMERIC",
                },
                {
                    "name": "approval_statuses",
                    "value": ",".join(
                        sorted({finding.status.value for finding in run.findings})
                    )
                    or "none",
                    "data_type": "CATEGORICAL",
                },
            ],
            "observations": [
                {
                    "name": "target-exchange",
                    "case_id": exchange.case_id,
                    "status": exchange.response_status,
                    "latency_ms": exchange.latency_ms,
                    "error": exchange.error,
                }
                for exchange in run.exchanges
            ],
        }

    def record_run(self, run: RunArtifact) -> dict[str, Any]:
        payload = self.build_payload(run)
        if not self.settings.langfuse_configured:
            payload["recorded"] = False
            payload["reason"] = "langfuse_not_configured"
            return payload
        try:
            from langfuse import get_client  # type: ignore

            client = get_client()
            with client.start_as_current_observation(
                as_type="span",
                name=payload["trace_name"],
                metadata=payload["metadata"],
            ) as span:
                span.update(output={"run_id": run.run_id, "findings": len(run.findings)})
            client.flush()
            payload["recorded"] = True
        except Exception as exc:  # pragma: no cover - depends on optional service
            payload["recorded"] = False
            payload["reason"] = f"langfuse_error: {exc}"
        return payload
