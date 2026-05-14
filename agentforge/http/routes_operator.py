from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse

from agentforge.http.auth import (
    get_executor,
    get_metrics,
    get_settings,
    get_store,
    require_operator,
)
from agentforge.http.schemas import RegressionReplayRequest
from agentforge.models.campaign import CampaignStartRequest
from agentforge.observability.summary import build_observability_summary
from agentforge.orchestrator.priority import recommend_next_cases

router = APIRouter()


@router.get("/operator", response_class=HTMLResponse)
def operator_home(operator: str = Depends(require_operator)) -> str:
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>AgentForge</title></head>
<body>
  <main>
    <h1>AgentForge Security Platform</h1>
    <p>Authenticated operator: {operator}</p>
    <ul>
      <li><code>POST /operator/campaigns</code> starts a bounded campaign.</li>
      <li><code>GET /operator/findings?status=needs_approval</code> reviews findings.</li>
      <li><code>POST /operator/regressions/replay</code> replays approved regression cases.</li>
      <li><code>GET /operator/status</code> shows deployment readiness.</li>
    </ul>
  </main>
</body>
</html>"""


@router.get("/operator/status")
def operator_status(
    operator: str = Depends(require_operator),
    settings=Depends(get_settings),
    executor=Depends(get_executor),
    store=Depends(get_store),
    metrics=Depends(get_metrics),
):
    cases = executor.catalog.load_cases()
    runs = store.list_runs(evidence_environment=settings.evidence_environment)
    findings = store.list_findings()
    regression_cases = store.list_regression_cases()
    regression_validations = store.list_regression_validations()
    observability = build_observability_summary(
        cases=cases,
        runs=runs,
        findings=findings,
        regression_cases=regression_cases,
        regression_validations=regression_validations,
        evidence_environment=settings.evidence_environment,
        metrics_snapshot=metrics.snapshot(),
    )
    coverage = observability["coverage"]
    return {
        "operator": operator,
        "targets": sorted(settings.target_urls),
        "artifact_dir": str(settings.artifact_dir),
        "evidence_environment": settings.evidence_environment,
        "provider_mode": settings.provider_mode,
        "redteam_model": settings.redteam_model,
        "judge_model": settings.judge_model,
        "langfuse_enabled": settings.langfuse_enabled,
        "coverage": coverage,
        "next_campaign_recommendation": recommend_next_cases(
            cases,
            coverage,
            max_cases=settings.max_cases_per_campaign,
        ),
        "regressions": observability["regressions"],
        "observability": observability,
    }


@router.post("/operator/campaigns")
def start_campaign(
    body: CampaignStartRequest,
    operator: str = Depends(require_operator),
    executor=Depends(get_executor),
    metrics=Depends(get_metrics),
):
    try:
        run = executor.run(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    metrics.inc("campaigns_total")
    metrics.inc("findings_total", len(run.findings))
    return run.model_dump(mode="json") | {"operator": operator}


@router.post("/operator/regressions/replay")
def replay_regressions(
    body: RegressionReplayRequest,
    operator: str = Depends(require_operator),
    executor=Depends(get_executor),
    metrics=Depends(get_metrics),
):
    try:
        validation = executor.replay_regressions(
            finding_ids=body.finding_ids or None,
            target_change_id=body.target_change_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    metrics.inc("regression_replays_total")
    metrics.inc("regression_replay_cases_total", validation["summary"]["total"])
    return validation | {"operator": operator}


@router.get("/operator/runs/{run_id}")
def get_run(
    run_id: str,
    operator: str = Depends(require_operator),
    store=Depends(get_store),
):
    try:
        run = store.get_run(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="run not found") from exc
    return run.model_dump(mode="json") | {"operator": operator}


@router.get("/metrics", response_class=PlainTextResponse)
def metrics(operator: str = Depends(require_operator), metrics=Depends(get_metrics)) -> str:
    return metrics.render_prometheus()
