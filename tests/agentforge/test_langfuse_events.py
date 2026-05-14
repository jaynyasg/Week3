from __future__ import annotations

from agentforge.models.finding import Finding, Verdict
from agentforge.models.run_artifact import RunArtifact, TargetExchange
from agentforge.observability.langfuse_client import LangfuseRecorder


def test_langfuse_payload_is_metadata_only(settings):
    finding = Finding(
        run_id="run-1",
        case_id="case-1",
        title="Finding",
        category="rbac",
        verdict=Verdict.VULNERABLE,
        severity="high",
        rationale="unsafe",
    ).with_default_status()
    run = RunArtifact(
        run_id="run-1",
        campaign_id="camp-1",
        target_alias="clinical",
        findings=[finding],
        exchanges=[
            TargetExchange(
                case_id="case-1",
                target_alias="clinical",
                target_url="https://target.example/agent/chat",
                response_summary={"text_excerpt": "Hemoglobin 7.9"},
            )
        ],
    )

    payload = LangfuseRecorder(settings).record_run(run)

    assert payload["recorded"] is False
    assert payload["scores"][1]["value"] == "needs_approval"
    assert payload["scores"][2]["value"] == "vulnerable"
    assert payload["scores"][3]["value"] == "rbac"
    assert payload["metadata"]["agent_activity_order"][0] == "orchestrator"
    assert "Hemoglobin" not in str(payload)
