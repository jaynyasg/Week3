# AgentForge Deployment

AgentForge is deployed as a separate security platform that calls the deployed
OpenEMR / Clinical Co-Pilot target over HTTPS. Final evidence must come from
deployed AgentForge calling deployed OpenEMR; local runs are development-only.

## Render Blueprint

The root `render.yaml` provisions one web service:

- `agentforge-security`: FastAPI app served by Uvicorn.
- Persistent disk mounted at `/data/agentforge` (see `render.yaml`); seed cases remain under `/app/evals/cases` in the image.
- Public health check at `/health`.
- Protected operator/API surface under `/operator/*`.
- Authenticated regression replay under `/operator/regressions/replay`.
- Operator observability summary under `/operator/status`.

## Required Environment Variables

| Variable | Purpose |
| --- | --- |
| `AGENTFORGE_OPERATOR_TOKEN` | Bearer/operator token for campaign, artifact, and approval routes. |
| `AGENTFORGE_TARGET_URL` | Deployed OpenEMR / Clinical Co-Pilot base URL. |
| `AGENTFORGE_TARGET_CHAT_PATH` | Target chat path, usually `/agent/chat`. |
| `AGENTFORGE_ARTIFACT_DIR` | Writable artifact root. On Render use `/data/agentforge` (must match disk `mountPath` in `render.yaml`). |
| `AGENTFORGE_EVIDENCE_ENVIRONMENT` | Must be `deployed` for submission evidence. |
| `AGENTFORGE_BUDGET_USD` | Per-campaign LLM budget cap. |
| `AGENTFORGE_MAX_CASES_PER_CAMPAIGN` | Default case cap when the Orchestrator chooses coverage/weak-surface recommendations. |
| `AGENTFORGE_PROVIDER_MODE` | `deterministic` for dry/safe mode, `live` for hosted LLM calls. |
| `GROQ_API_KEY` | Enables Groq `llama-3.1-8b-instant` red-team mutation when provider mode is `live`. |
| `OPENAI_API_KEY` | Enables OpenAI `gpt-5-nano` judge fallback/docs when provider mode is `live`. |
| `LANGFUSE_ENABLED` | Set `1` to enable Langfuse telemetry. |
| `LANGFUSE_PUBLIC_KEY` | Langfuse project public key. |
| `LANGFUSE_SECRET_KEY` | Langfuse project secret key. |
| `LANGFUSE_BASE_URL` | Langfuse cloud or private/self-hosted base URL. |

## Render dashboard: secrets to set (submission)

In the Render service **Environment** tab, set at least:

| Variable | Notes |
| --- | --- |
| `AGENTFORGE_OPERATOR_TOKEN` | Long random secret; required for `/operator/*`. |
| `AGENTFORGE_TARGET_URL` | Base URL of the **deployed** Week 2 Clinical Co-Pilot (no trailing slash). |
| `GROQ_API_KEY` | Required when `AGENTFORGE_PROVIDER_MODE=live` for Groq red-team. |
| `OPENAI_API_KEY` | Required when `AGENTFORGE_PROVIDER_MODE=live` for judge/docs fallback. |

Optional Langfuse (only if `LANGFUSE_ENABLED=1`):

| Variable | Notes |
| --- | --- |
| `LANGFUSE_PUBLIC_KEY` | Project public key. |
| `LANGFUSE_SECRET_KEY` | Project secret key. |
| `LANGFUSE_BASE_URL` | Or `LANGFUSE_HOST` per app config. |

Keep `AGENTFORGE_EVIDENCE_ENVIRONMENT=deployed` for canonical submission evidence.

## Security Groups And Network Boundaries

| Component | Ingress | Egress | Notes |
| --- | --- | --- | --- |
| AgentForge | Public HTTPS health and authenticated operator routes | Allowlisted target, Groq/OpenAI, Langfuse | Operator routes require token auth. |
| OpenEMR / Clinical Co-Pilot target | Public HTTPS according to Week 2 deployment | Private DB, target services | System under test. |
| Target DB | Private service network only | Service responses only | Must not be internet-exposed. |
| Artifact disk | AgentForge service only | Operator artifact downloads | Stores deployed evidence and approval records. |
| Langfuse | AgentForge trace ingestion | Dashboards/exports | Metadata-only by default. |

## Readiness

Check:

```bash
curl https://<agentforge-url>/health
curl https://<agentforge-url>/ready
```

`/ready` is degraded when no target URL is configured. It does not expose
secrets.

## Disable Procedure

1. Pause or suspend the `agentforge-security` Render service.
2. Rotate `AGENTFORGE_OPERATOR_TOKEN`.
3. Set `AGENTFORGE_PROVIDER_MODE=deterministic` to stop live LLM spend.
4. Set `LANGFUSE_ENABLED=0` if telemetry must be stopped.
5. Preserve the persistent disk (`AGENTFORGE_ARTIFACT_DIR`, e.g. `/data/agentforge`) before deleting the service if evidence is needed.

## Rollback

Redeploy the previous Render version or Docker image. Artifact storage is
separate from the image and should survive app restarts.
