from __future__ import annotations

from agentforge.models.run_artifact import RunArtifact
from agentforge.observability.events import build_run_event
from agentforge.observability.metrics import Metrics


def test_run_event_is_phi_safe_metadata():
    run = RunArtifact(
        campaign_id="camp-1",
        target_alias="clinical",
        model_provider="groq",
        model_name="llama-3.1-8b-instant",
        estimated_cost_usd=0.01,
    )

    event = build_run_event(run)

    assert event["model_name"] == "llama-3.1-8b-instant"
    assert "response_excerpt" not in event


def test_metrics_render_prometheus():
    metrics = Metrics()
    metrics.inc("campaigns_total")

    assert "agentforge_campaigns_total 1" in metrics.render_prometheus()
