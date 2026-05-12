# AgentForge Adversarial AI Security Platform

AgentForge is a deployed adversarial security platform for evaluating the deployed OpenEMR Clinical Co-Pilot target from Week 2. It is not a clinical assistant and it is not a general-purpose scanner. Its job is to run bounded, allowlisted security campaigns against the deployed healthcare AI target, preserve reproducible evidence, and convert confirmed failures into vulnerability reports and regression artifacts.

## Project Status

This repository is in Week 3 build-out. Current planning artifacts:

- `docs/brainstorms/week3-adversarial-ai-security-platform-requirements.md`
- `docs/plans/2026-05-11-001-feat-agentforge-security-platform-plan.md`

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
AGENTFORGE_ARTIFACT_DIR=/app/evals
```

The Render blueprint in `render.yaml` attaches persistent storage at `/app/evals`.
See `deploy/docs/deployment.md` and `deploy/docs/operator-runbook.md`.

## Non-Goals

- Arbitrary internet scanning.
- Automated exploit remediation or patch generation.
- Replacing OpenEMR access control.
- Treating local eval output as final evidence.
- Building a clinical decision support product for end users.
