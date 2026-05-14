# AgentForge Adversarial AI Security Platform

AgentForge is a deployed adversarial security platform for evaluating the deployed OpenEMR Clinical Co-Pilot target from Week 2. It is not a clinical assistant and it is not a general-purpose scanner. Its job is to run bounded, allowlisted security campaigns against the deployed healthcare AI target, preserve reproducible evidence, and convert confirmed failures into vulnerability reports and regression artifacts.

## Deployed URLs

- AgentForge security platform: <https://agentforge-security.onrender.com>
- Target Clinical Co-Pilot (Week 2): <https://clinical-copilot-4kwb.onrender.com>

Submission evidence comes from the deployed AgentForge platform calling the deployed Clinical Co-Pilot target. Health and readiness checks are public:

```bash
curl https://agentforge-security.onrender.com/health
curl https://agentforge-security.onrender.com/ready
```

Operator endpoints (campaigns, findings, approvals, artifacts) require the `AGENTFORGE_OPERATOR_TOKEN` bearer header and are documented in `deploy/docs/operator-runbook.md`.

## Project Status

The MVP is complete and deployed. Final-submission completion is tracked in:

- `SUBMISSION.md`
- `docs/submission/platform-requirements-checklist.md`
- `docs/plans/2026-05-14-001-feat-agentforge-final-submission-plan.md`

Current planning artifacts:

- `docs/brainstorms/week3-adversarial-ai-security-platform-requirements.md`
- `docs/plans/2026-05-11-001-feat-agentforge-security-platform-plan.md`
- `docs/plans/2026-05-14-001-feat-agentforge-final-submission-plan.md`

U1 documentation foundation:

- `ARCHITECTURE.md`
- `deploy/docs/architecture-defense.md`
- `THREAT_MODEL.md`
- `USERS.md`
- `AI-COST-ANALYSIS.md`

## Canonical Evidence Rule

Final testing evidence must come from:

```text
deployed AgentForge security app -> deployed OpenEMR / Clinical Co-Pilot target
```

Local runs are useful for development and unit tests, but local output is not submission evidence.

## Target Reference

The Week 2 target code and docs live in:

```text
Week2 - Test Suite/
```

Important target surfaces include:

- `Week2 - Test Suite/agent/http/routes_chat.py`
- `Week2 - Test Suite/agent/http/deps.py`
- `Week2 - Test Suite/agent/tools/dispatch.py`
- `Week2 - Test Suite/agent/access/rbac.py`
- `Week2 - Test Suite/agent/services/openai_tool_loop.py`
- `Week2 - Test Suite/EVAL.md`
- `Week2 - Test Suite/render.yaml`

## Target Readiness Changes

No code changes were made to the Week 2 Clinical Co-Pilot target during Week 3. The deployed target at `https://clinical-copilot-4kwb.onrender.com` runs the Week 2 codebase as-is, with its existing RBAC, patient-scope, tool-round, body-limit, and refusal defenses unchanged. Week 3 work consisted entirely of standing up the separate AgentForge security platform (`agentforge/`, `evals/`, `deploy/`, `Dockerfile`, `render.yaml`, threat-model and architecture docs) that *calls* the deployed target. The only Week 3 commit that touched `Week2 - Test Suite/` was the initial repo organization commit that brought the Week 2 folder in as a read-only reference; subsequent Week 3 commits modified only AgentForge files. This preserves the integrity of the system under test: every finding in `evals/results/` is a verdict on the Week 2 target's published behavior, not on a custom-instrumented variant. Operator authentication for the target's chat route uses the existing demo configuration (`AGENT_DEMO_BYPASS` + role headers) documented under `Week2 - Test Suite/agent/http/deps.py`; AgentForge passes those headers per-case rather than altering the target's auth model.

Local target validation was also performed as a development-only check. The Week 2 docker-compose target was started from `Week2 - Test Suite/docker-compose.agent-demo.yml`, `http://localhost:8080/agent/health` returned `{"status":"ok"}`, and local AgentForge was pointed at `AGENTFORGE_TARGET_URL=http://localhost:8080`. Run `evals/results/run-971349616249.json` records local AgentForge calling `http://localhost:8080/agent/chat` with `evidence_environment=development`, `response_status=200`, and the `rbac-nurse-labs-001` case. The local target enforced RBAC (`error_code=rbac_refusal`), and operator review marked finding `evals/results/findings/find-24111ce6522f.json` as `needs_more_evidence` because the deterministic judge matched lab terms inside the assistant's refusal text. This local run proves the development loop works, but the canonical submission evidence remains the deployed-to-deployed runs.

## Security Baseline

AgentForge maps findings to existing AI security guidance instead of inventing a private taxonomy:

- OWASP LLM Top 10
- OWASP GenAI Red Teaming Guide
- OWASP MCP Top 10
- MITRE ATLAS
- NIST AI 600-1
- CISA/NCSC secure AI system development guidance
- Cloud Security Alliance AI Controls Matrix

## MVP Shape

The MVP follows a deterministic-first multi-agent slice:

- Red Team Agent generates and mutates attacks.
- Orchestrator schedules bounded campaigns.
- Deployed Target Runner calls only the allowlisted deployed target.
- Judge Agent scores results independently of the red-team generator.
- Documentation Agent produces vulnerability reports.
- Regression Harness stores replayable cases.
- Observability Layer uses Langfuse traces/scores plus local artifacts to track cost, model/provider, verdicts, approval status, and PHI-safe events.

## Development Notes

Implementation follows the plan in `docs/plans/2026-05-11-001-feat-agentforge-security-platform-plan.md`.

The deployed platform will require:

- A configured deployed OpenEMR / Clinical Co-Pilot target URL.
- Operator authentication for campaign start/status/artifact endpoints.
- Groq `llama-3.1-8b-instant` for red-team mutation and OpenAI `gpt-5-nano` for limited judge fallback/documentation.
- Persistent artifact storage for deployed evidence.
- Hard budget limits for model spend and campaign size.
- Human approval for high-severity, ambiguous, partial, or LLM-judge-only findings before final report/regression promotion.

## Run Locally For Development

Local runs are development checks only. They do not replace deployed evidence.

```bash
python -m pytest tests/agentforge -q
uvicorn agentforge.http.app:create_app --factory --host 127.0.0.1 --port 8080
```

Protected operator routes accept either:

```text
Authorization: Bearer <AGENTFORGE_OPERATOR_TOKEN>
X-AgentForge-Operator-Token: <AGENTFORGE_OPERATOR_TOKEN>
```

## Deployed Operation

Deploy AgentForge separately from the Week 2 OpenEMR / Clinical Co-Pilot target. Configure the deployed target URL by environment variable:

```text
AGENTFORGE_TARGET_URL=https://<deployed-clinical-agent-or-openemr-proxy>
AGENTFORGE_TARGET_CHAT_PATH=/agent/chat
AGENTFORGE_EVIDENCE_ENVIRONMENT=deployed
AGENTFORGE_ARTIFACT_DIR=/data/agentforge
```

The Render blueprint in `render.yaml` mounts persistent storage at `/data/agentforge` and sets `AGENTFORGE_ARTIFACT_DIR` to match (so the image’s baked-in case catalog under `/app/evals/cases` is not hidden by the disk).

Final submission control: `SUBMISSION.md` and `docs/submission/platform-requirements-checklist.md`.
Submission runbook (env vars, smoke, evidence, F1-F6 mapping): `deploy/docs/mvp-submission-runbook.md`.
Also see `deploy/docs/deployment.md`, `deploy/docs/smoke-checklist.md`, `deploy/docs/operator-runbook.md`, and `deploy/scripts/Deploy-Smoke.ps1`.

## Non-Goals

- Arbitrary internet scanning.
- Automated exploit remediation or patch generation.
- Replacing OpenEMR access control.
- Treating local eval output as final evidence.
- Building a clinical decision support product for end users.
