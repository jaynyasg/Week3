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
- Observability Layer tracks cost, model/provider, verdicts, and PHI-safe events.

## Development Notes

Implementation follows the plan in `docs/plans/2026-05-11-001-feat-agentforge-security-platform-plan.md`.

The deployed platform will require:

- A configured deployed OpenEMR / Clinical Co-Pilot target URL.
- Operator authentication for campaign start/status/artifact endpoints.
- A hosted low-cost LLM provider for deployed campaigns.
- Persistent artifact storage for deployed evidence.
- Hard budget limits for model spend and campaign size.

## Non-Goals

- Arbitrary internet scanning.
- Automated exploit remediation or patch generation.
- Replacing OpenEMR access control.
- Treating local eval output as final evidence.
- Building a clinical decision support product for end users.
