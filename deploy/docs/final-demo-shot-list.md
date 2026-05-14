# AgentForge Final Demo Shot List

Use this checklist immediately before recording the 3-5 minute final demo.

## Must Show

| Shot | Evidence | Status |
| --- | --- | --- |
| Deployed AgentForge health | `https://agentforge-security.onrender.com/health` returns `{"status":"ok"}` | Captured manually before recording |
| Deployed AgentForge readiness | `https://agentforge-security.onrender.com/ready` shows `status=ready`, target configured, `evidence_environment=deployed` | Captured manually before recording |
| Deployed target health | `https://clinical-copilot-4kwb.onrender.com/agent/health` returns `{"status":"ok"}` | Captured manually before recording |
| Operator status | Authenticated `GET /operator/status` shows coverage, weak surfaces, recommendations, observability answers, regression state | Requires `AGENTFORGE_OPERATOR_TOKEN` |
| Live or latest deployed campaign | `POST /operator/campaigns` response or latest `evals/results/run-*.json` | Requires `AGENTFORGE_OPERATOR_TOKEN` for a fresh run |
| Vulnerability report | Curated `evals/reports/find-*.md` with impact, reproduction, expected/observed behavior, remediation, validation | Regenerate after final finding decisions |
| Human approval gate | Finding JSON with approval history or `needs_more_evidence` rationale | Use a real deployed finding |
| Regression replay | `POST /operator/regressions/replay` response plus `evals/regression/validations/*.json` | Requires `AGENTFORGE_OPERATOR_TOKEN` |
| Cost story | `AI-COST-ANALYSIS.md` projection table and actual spend section | Ready unless live-provider final run changes spend |
| Social post draft | `deploy/docs/social-post.md` | Publish externally before final submission |

## Recording Notes

- Do not show `AGENTFORGE_OPERATOR_TOKEN`, provider keys, Langfuse secrets, cookies, or bearer values.
- Use deployed-to-deployed artifacts only for final claims.
- Label judge-flagged findings as unconfirmed; do not present them as confirmed vulnerabilities.
- If Render cold-starts, show the latest captured deployed run artifact and say the live endpoint is warming.
- Keep the talk track focused on: multi-agent roles, allowlisted target, independent judge, human approval, regression replay, coverage-driven orchestration, PHI-safe observability, and cost controls.

## Current Local Blocker

As of 2026-05-14, public smoke checks pass, but this local shell does not have `AGENTFORGE_OPERATOR_TOKEN` set. Set it before capturing authenticated status, campaign, approval, artifact, and regression replay evidence.
