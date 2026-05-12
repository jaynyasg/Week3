from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from agentforge.attacks.catalog import AttackCatalog
from agentforge.config import AgentForgeSettings
from agentforge.http.routes_approvals import router as approvals_router
from agentforge.http.routes_artifacts import router as artifacts_router
from agentforge.http.routes_operator import router as operator_router
from agentforge.http.schemas import ReadinessResponse
from agentforge.observability.metrics import Metrics
from agentforge.orchestrator.campaigns import CampaignExecutor
from agentforge.storage.artifact_store import ArtifactStore
from agentforge.targets.allowlist import TargetAllowlist


def create_app(settings: AgentForgeSettings | None = None) -> FastAPI:
    settings = settings or AgentForgeSettings.from_env()
    store = ArtifactStore(settings.artifact_dir)
    allowlist = TargetAllowlist(settings.target_urls)
    catalog = AttackCatalog()
    metrics = Metrics()
    executor = CampaignExecutor(
        settings=settings,
        catalog=catalog,
        store=store,
        allowlist=allowlist,
    )

    app = FastAPI(
        title="AgentForge Adversarial Security Platform",
        version="0.1.0",
        openapi_tags=[
            {"name": "health", "description": "Liveness and readiness."},
            {"name": "operator", "description": "Protected campaign controls."},
            {"name": "artifacts", "description": "Protected evidence retrieval."},
            {"name": "approvals", "description": "Human approval workflow."},
        ],
    )
    app.state.settings = settings
    app.state.store = store
    app.state.allowlist = allowlist
    app.state.catalog = catalog
    app.state.metrics = metrics
    app.state.executor = executor

    app.include_router(operator_router, tags=["operator"])
    app.include_router(artifacts_router, tags=["artifacts"])
    app.include_router(approvals_router, tags=["approvals"])

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready", tags=["health"], response_model=ReadinessResponse)
    def ready() -> ReadinessResponse:
        ready_status = (
            "ready"
            if settings.target_configured and settings.operator_auth_configured
            else "degraded"
        )
        return ReadinessResponse(
            status=ready_status,
            operator_auth_configured=settings.operator_auth_configured,
            target_configured=settings.target_configured,
            targets=sorted(settings.target_urls),
            artifact_dir=str(settings.artifact_dir),
            evidence_environment=settings.evidence_environment,
            provider_mode=settings.provider_mode,
            provider_configured=settings.provider_configured,
            langfuse_enabled=settings.langfuse_enabled,
            langfuse_configured=settings.langfuse_configured,
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(_, exc: ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    return app
