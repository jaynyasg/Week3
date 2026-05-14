# AgentForge Final Submission Control

**Status:** final deployed evidence captured as of 2026-05-14. AgentForge is deployed on `main`, Render has run the latest attachment adapter fix (`b597142`), authenticated deployed campaigns and regression replay have been captured, and the repository now has three defensible report lanes. Remaining off-repo work is the 3-5 minute demo recording and required social post.

## Canonical Links

| Item | Value |
| --- | --- |
| AgentForge security platform | https://agentforge-security.onrender.com |
| Target Clinical Co-Pilot | https://clinical-copilot-4kwb.onrender.com |
| Platform requirements checklist | `docs/submission/platform-requirements-checklist.md` |
| Operator runbook | `deploy/docs/operator-runbook.md` |
| Deployment runbook | `deploy/docs/mvp-submission-runbook.md` |
| Final submission runbook | `deploy/docs/final-submission-runbook.md` |
| Final demo script | `deploy/docs/final-demo-script.md` |
| Demo shot list | `deploy/docs/final-demo-shot-list.md` |
| Final evidence sweep note | `deploy/docs/final-evidence-sweep.md` |
| Final capture artifacts | `deploy/captures/` |
| Social post draft | `deploy/docs/social-post.md` |
| Final completion plan | `docs/plans/2026-05-14-001-feat-agentforge-final-submission-plan.md` |

Final evidence must come from deployed AgentForge calling the deployed Clinical Co-Pilot target with `evidence_environment=deployed`. Local and development runs can support implementation, but they do not satisfy final evidence claims.

## Current Evidence Inventory

| Run ID | Environment | Cases | Findings | Submission use |
| --- | --- | ---: | ---: | --- |
| `run-b5a238a8b374` | deployed | 1 | 0 | Safe RBAC baseline; useful for deployed readiness and refusal proof. |
| `run-3fcb420ddc96` | deployed | 4 | 4 | Earlier deployed campaign; source for the cost/DoS report lane and first attachment reliability regression lane. |
| `run-6a5297ca98ab` | deployed | 5 | 2 | Final coverage-gap campaign selected from Orchestrator recommendations; completed 10/10 catalog coverage and finding curation. |
| `run-94464fc484ac` | deployed | 2 | 1 | Targeted attachment rerun after commit `b597142`; confirmed attachment payload adapter fix and exposed a deployed attachment-path 500. |
| `run-45db101ce676` | development | 1 | 1 | Excluded from final evidence; development-only context. |
| `run-971349616249` | development | 1 | 1 | Excluded from final evidence; development-only context. |

## Current Finding State

| Finding ID | Run ID | Category | Current status | Current lane |
| --- | --- | --- | --- | --- |
| `find-4e41695d42ec` | `run-3fcb420ddc96` | cost/DoS amplification | `approved` | Final report lane; latest replay `regval-c5831da1bcba` marks it `resolved`. |
| `find-2f92b8b731b0` | `run-3fcb420ddc96` | attachment prompt injection reliability | `regression_queued` | Final report lane; latest replay `regval-c5831da1bcba` marks it `reappeared`. |
| `find-63eb1564ab3c` | `run-94464fc484ac` | attachment prompt injection reliability | `regression_queued` | Final report lane after attachment adapter fix; latest replay `regval-c5831da1bcba` marks it `reappeared`. |
| Judge-flagged/rejected set | deployed runs | RBAC, scope, prompt-state, attachment | mixed | Final curation counts: `approved=1`, `regression_queued=2`, `needs_more_evidence=5`, `rejected=3`. |

## Submission Deliverables

| PDF deliverable | Current evidence | Status |
| --- | --- | --- |
| GitHub/GitLab repository with setup guide, architecture overview, deployed link, and run instructions | `README.md`, `deploy/docs/deployment.md`, `deploy/docs/operator-runbook.md`, `deploy/docs/final-submission-runbook.md`, deployed links above | Ready after final evidence-doc commit/push. |
| Threat model | `THREAT_MODEL.md` | Present; updated for final attack families and AgentForge controls. |
| User doc | `USERS.md` | Present; updated for coverage/weak-surface and regression workflows. |
| Architecture doc | `ARCHITECTURE.md`, `deploy/docs/architecture-defense.md` | Present; updated for implemented orchestration, replay, and observability behavior. |
| Demo video, 3-5 minutes | `deploy/docs/final-demo-script.md`, `deploy/docs/final-demo-shot-list.md` | Not recorded; script and shot list now reference final evidence IDs. |
| Eval dataset across at least three attack categories | `evals/cases/`, `deploy/captures/campaign-run-6a5297ca98ab-20260514-173759.json`, `deploy/captures/attachment-campaign-run-94464fc484ac-20260514-180337.json` | Complete; 10/10 cases across 5 categories tested in deployed evidence. |
| Minimum three vulnerability reports | `evals/reports/find-4e41695d42ec.md`, `evals/reports/find-2f92b8b731b0.md`, `evals/reports/find-63eb1564ab3c.md` | Complete; three defensible report lanes with approval/regression status. |
| AI cost analysis at 100 / 1K / 10K / 100K runs | `AI-COST-ANALYSIS.md` | Mostly ready; update only if final live-provider runs or hosting plans change. |
| Deployed application | AgentForge and target URLs above; final deployed commit `b597142` | Complete; final authenticated status, campaign, curation, and replay captured. |
| Final social post | `deploy/docs/social-post.md` | Drafted; publish externally and add URL before final submission. |

## Latest Public Smoke Check

Checked on 2026-05-14 during the final execution pass:

| Endpoint | Result |
| --- | --- |
| `https://agentforge-security.onrender.com/health` | `status=ok` |
| `https://agentforge-security.onrender.com/ready` | `status=ready`, target configured, `evidence_environment=deployed`, Langfuse configured |
| `https://clinical-copilot-4kwb.onrender.com/agent/health` | `status=ok` |

Authenticated evidence capture is complete. Final status artifact `deploy/captures/operator-status-final-20260514-180849.json` shows 10/10 catalog cases tested, 5 categories, final finding status counts, and two regression validations.

## Final Blockers

1. Record and link the 3-5 minute demo video.
2. Publish and link the required X or LinkedIn post tagging `@GauntletAI`.
3. Add the demo URL and social URL to this file and `deploy/docs/final-demo-script.md`.
4. Run final `python -m pytest tests\agentforge -q`, then commit and push the final evidence-doc/capture update.

## Final Evidence Rule

Do not count an artifact as final evidence unless all of the following are true:

- The run artifact has `evidence_environment=deployed`.
- The target URL is the deployed Clinical Co-Pilot target.
- The finding has an explicit final lane: confirmed, judge-flagged/unconfirmed, rejected, or excluded.
- Confirmed findings have approval history and regression or validation status.
- Reports cite run ID, finding ID, category, expected behavior, observed behavior, status, and validation result.

