from __future__ import annotations

from agentforge.reporting.cost_report import build_cost_projection, estimated_llm_cost_per_run


def test_cost_projection_uses_documented_model_route():
    projection = build_cost_projection([100, 100000])

    assert projection[0]["llm_estimate_usd"] == "0.02"
    assert projection[1]["llm_estimate_usd"] == "18.81"
    assert "gpt-5-nano" in projection[0]["basis"]
    assert estimated_llm_cost_per_run() > 0
