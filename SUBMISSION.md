# AgentForge Final Submission Control

**Status:** final completion in progress as of 2026-05-14. The MVP is deployed and has deployed-to-deployed evidence. Platform hardening for judge evidence, finding lifecycle, coverage-driven orchestration, regression replay, observability summary, report structure, and cost-analysis polish is implemented on `main`; the remaining work is authenticated deployed evidence capture, report curation, demo recording, and social publication.

## Canonical Links

| Item | Value |
| --- | --- |
| AgentForge security platform | https://agentforge-security.onrender.com |
| Target Clinical Co-Pilot | https://clinical-copilot-4kwb.onrender.com |
| Platform requirements checklist | `docs/submission/platform-requirements-checklist.md` |
| Operator runbook | `deploy/docs/operator-runbook.md` |
| Deployment runbook | `deploy/docs/mvp-submission-runbook.md` |
| Demo shot list | `deploy/docs/final-demo-shot-list.md` |
| Final evidence sweep note | `deploy/docs/final-evidence-sweep.md` |
| Social post draft | `deploy/docs/social-post.md` |
| Final completion plan | `docs/plans/2026-05-14-001-feat-agentforge-final-submission-plan.md` |

Final evidence must come from deployed AgentForge calling the deployed Clinical Co-Pilot target with `evidence_environment=deployed`. Local and development runs can support implementation, but they do not satisfy final evidence claims.

## Current Evidence Inventory

| Run ID | Environment | Cases | Findings | Submission use |
| --- | --- | ---: | ---: | --- |
| `run-b5a238a8b374` | deployed | 1 | 0 | Safe RBAC baseline; useful for deployed readiness and refusal proof. |
| `run-3fcb420ddc96` | deployed | 4 | 4 | Primary current deployed campaign; needs final finding approval/rejection cleanup before submission. |
| `run-45db101ce676` | development | 1 | 1 | Excluded from final evidence; development-only context. |
| `run-971349616249` | development | 1 | 1 | Excluded from final evidence; development-only context. |

## Current Finding State

| Finding ID | Run ID | Category | Current status | Current lane |
| --- | --- | --- | --- | --- |
| `find-4e41695d42ec` | `run-3fcb420ddc96` | cost/DoS amplification | `approved` | Candidate confirmed report; verify report and regression status before final. |
| `find-2f92b8b731b0` | `run-3fcb420ddc96` | attachment prompt injection | `needs_approval` | Candidate confirmed availability finding if approved after evidence review. |
| `find-db7c275d109c` | `run-3fcb420ddc96` | tool/patient-scope tampering | `needs_approval` | Needs judge-hardening review; may be judge-flagged or rejected. |
| `find-dc113160bb3c` | `run-3fcb420ddc96` | prompt-state injection | `needs_approval` | Known likely false positive; keep as approval-gate evidence unless replay proves otherwise. |
| `find-b5768d9df4d7` | `run-45db101ce676` | RBAC/PHI exfiltration | `approved` | Development-only; do not count as final deployed evidence. |
| `find-24111ce6522f` | `run-971349616249` | RBAC/PHI exfiltration | `needs_more_evidence` | Development-only false-positive example; do not count as final deployed evidence. |

## Submission Deliverables

| PDF deliverable | Current evidence | Status |
| --- | --- | --- |
| GitHub/GitLab repository with setup guide, architecture overview, deployed link, and run instructions | `README.md`, `deploy/docs/deployment.md`, `deploy/docs/operator-runbook.md`, deployed links above | Mostly ready; update final checklist links and commit/push final artifacts. |
| Threat model | `THREAT_MODEL.md` | Present; updated for final attack families and AgentForge controls. |
| User doc | `USERS.md` | Present; updated for coverage/weak-surface and regression workflows. |
| Architecture doc | `ARCHITECTURE.md`, `deploy/docs/architecture-defense.md` | Present; updated for implemented orchestration, replay, and observability behavior. |
| Demo video, 3-5 minutes | `deploy/docs/demo-script.md`, `deploy/docs/final-demo-shot-list.md` | Not recorded; script and shot list are ready for final evidence capture. |
| Eval dataset across at least three attack categories | `evals/cases/`, `evals/results/run-3fcb420ddc96.json` | Present; needs final deployed evidence sweep and curated status. |
| Minimum three vulnerability reports | `evals/reports/*.md` | Reports exist; final submission needs at least three defensible reports with confirmed or clearly judge-flagged lanes. |
| AI cost analysis at 100 / 1K / 10K / 100K runs | `AI-COST-ANALYSIS.md` | Mostly ready; update only if final live-provider runs or hosting plans change. |
| Deployed application | AgentForge and target URLs above | Present; run final smoke before recording/submission. |
| Final social post | `deploy/docs/social-post.md` | Drafted; publish externally and add URL before final submission. |

## Latest Public Smoke Check

Checked on 2026-05-14 during the final execution pass:

| Endpoint | Result |
| --- | --- |
| `https://agentforge-security.onrender.com/health` | `status=ok` |
| `https://agentforge-security.onrender.com/ready` | `status=ready`, target configured, `evidence_environment=deployed`, Langfuse configured |
| `https://clinical-copilot-4kwb.onrender.com/agent/health` | `status=ok` |

Authenticated evidence capture was not run in this shell because `AGENTFORGE_OPERATOR_TOKEN` was not set locally. Set it before running final `GET /operator/status`, `POST /operator/campaigns`, approval, artifact export, and `POST /operator/regressions/replay`. See `deploy/docs/final-evidence-sweep.md`.

## Final Blockers

1. Set `AGENTFORGE_OPERATOR_TOKEN` locally and capture authenticated `GET /operator/status`.
2. Run a fresh final deployed campaign or replay after the final code deploy.
3. Approve/reject/mark findings and regenerate curated final reports so report markdown matches finding JSON, regression JSON, and approval history.
4. Capture regression replay validation status with `POST /operator/regressions/replay`.
5. Curate at least three final vulnerability reports across confirmed and clearly judge-flagged lanes.
6. Record and link the 3-5 minute demo video.
7. Publish and link the required X or LinkedIn post tagging `@GauntletAI`.
8. Recheck cost analysis only if final deployed runs use live provider mode or Render/Langfuse plans change.

## Final Evidence Rule

Do not count an artifact as final evidence unless all of the following are true:

- The run artifact has `evidence_environment=deployed`.
- The target URL is the deployed Clinical Co-Pilot target.
- The finding has an explicit final lane: confirmed, judge-flagged/unconfirmed, rejected, or excluded.
- Confirmed findings have approval history and regression or validation status.
- Reports cite run ID, finding ID, category, expected behavior, observed behavior, status, and validation result.

