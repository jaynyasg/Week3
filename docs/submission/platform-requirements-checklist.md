# Platform Requirements Checklist

**Source:** `Week 3 - AgentForge - Adversarial AI Security Platform.pdf`, "Platform Requirements" and "Submission Requirements".

**Last updated:** 2026-05-14.

This checklist tracks the gap between the deployed MVP and the final submission bar. It intentionally separates implemented evidence from final-submission-ready evidence.

## Status Legend

| Status | Meaning |
| --- | --- |
| Complete | Implemented and has submission-ready evidence. |
| Partial | Implemented in docs/code/artifacts, but needs hardening, status cleanup, or final evidence. |
| Missing | Not yet implemented or not yet represented in final artifacts. |
| External | Requires an off-repo action such as recording a video or publishing a social post. |

## Platform Requirements

| PDF requirement | Current evidence | Status | Remaining work |
| --- | --- | --- | --- |
| Multi-agent architecture is mandatory; a single-agent or plain pipeline architecture does not satisfy the assignment. | `ARCHITECTURE.md`, `USERS.md`, `agentforge/` role modules, `deploy/docs/architecture-defense.md` | Complete | Final docs and captures show Red Team, Orchestrator, Target Runner, Judge, Human Approver, Documentation, Regression, and Observability roles. |
| Each agent has distinct responsibilities, context, decision authority, inputs, outputs, trust level, and coordination path. | `ARCHITECTURE.md` agent responsibility table; `USERS.md` agent trust matrix; `deploy/captures/operator-status-final-20260514-180849.json` | Complete | Final status includes ordered agent activity and PHI-safe observability. |
| Red Team capability: generate novel adversarial inputs. | `agentforge/attacks/`, `evals/cases/*.yaml`, `deploy/captures/campaign-run-6a5297ca98ab-20260514-173759.json` | Complete | Final deployed evidence covers 10/10 cases across 5 attack categories. |
| Red Team capability: mutate partially successful attacks to probe bypasses. | `*_002.yaml` depth variants, attachment adapter rerun `run-94464fc484ac`, and weak-surface recirculation in final status | Complete | Partial attachment findings were replayed after the payload adapter fix and promoted into regression evidence. |
| Red Team capability: target multi-turn attack sequences, not only single prompts. | `evals/cases/cross_patient_history_injection.yaml`, `evals/cases/cross_patient_history_injection_002.yaml`, `run-6a5297ca98ab` | Complete | Final coverage includes both prompt-state/multi-turn variants. |
| Judge capability: evaluate attack success with consistent criteria across runs and versions. | `agentforge/judge/`, `evals/goldens/judge_cases.json`, `tests/agentforge/test_judge_goldens.py`, final curation captures | Complete | False positives were rejected or marked `needs_more_evidence`; confirmed lanes were queued for regression. |
| Judge independence: attack generation and attack evaluation must not happen in the same context. | Architecture docs and separate `attacks`, `judge`, and `orchestrator` modules | Complete | Red-team generation and judge evaluation remain separate modules and artifacts. |
| Orchestrator capability: prioritize attack surfaces based on coverage gaps, weak surfaces learned over time, and unresolved findings. | `agentforge/orchestrator/coverage.py`, `agentforge/orchestrator/priority.py`, `deploy/captures/operator-status-final-20260514-180849.json` | Complete | Final status shows no remaining coverage gaps and next recommendations now based on weak surfaces. |
| Orchestrator capability: halt or redirect when cost accumulates without signal. | `AI-COST-ANALYSIS.md`, campaign `budget_usd`, `estimated_cost_usd` fields, budget-halt tests | Complete | Final deployed campaigns retained bounded `budget_usd=0.25` and deterministic estimated platform model cost. |
| Orchestrator capability: trigger regression runs when the target changes. | `POST /operator/regressions/replay`, `deploy/captures/regression-replay-regval-c5831da1bcba-20260514-180755.json` | Complete | Final replay used target-change marker `render-b597142-2026-05-14`. |
| Model/provider choice is deliberate and defensible, including cost and refusal behavior. | `ARCHITECTURE.md`, `AI-COST-ANALYSIS.md`, final status provider metadata | Complete | Final evidence uses deterministic provider mode, Groq/OpenAI planned models, and explicit cost controls. |

## Documentation Agent

| PDF report requirement | Current evidence | Status | Remaining work |
| --- | --- | --- | --- |
| Unique identifier and severity rating. | `evals/reports/find-4e41695d42ec.md`, `evals/reports/find-2f92b8b731b0.md`, `evals/reports/find-63eb1564ab3c.md` | Complete | Three final report lanes cite canonical finding IDs, severities, and statuses. |
| Clear vulnerability description and clinical impact. | `agentforge/reporting/vulnerability_report.py`, final report markdown | Complete | Final reports include category-specific clinical impact. |
| Minimal reproducible attack sequence. | Final reports and captures include target, run ID, case ID, role, patient context, attachment count, and replay path | Complete | Reproduction path is recorded for all three report lanes. |
| Observed versus expected behavior. | Final reports and finding JSON include expected safe behavior and observed response evidence | Complete | Report markdown regenerated after final curation. |
| Recommended remediation approach. | Final reports include category-specific remediation guidance | Complete | Remediation is present in each final report. |
| Current status and fix validation results. | Final reports plus `regval-c5831da1bcba` | Complete | Report lanes have approval/regression status and latest replay validation. |
| Senior engineer can reproduce, validate, and fix from the report alone. | Final report set and `deploy/captures/` | Complete | Three report lanes are self-contained and linked to deployed artifacts. |

## Regression And Validation Harness

| PDF requirement | Current evidence | Status | Remaining work |
| --- | --- | --- | --- |
| Store confirmed exploits in a versioned, queryable format. | Deployed regression queue and final captures | Complete | Three deployed report lanes are stored/queued for regression. |
| Run full regression suite automatically when triggered by the Orchestrator. | `deploy/captures/regression-replay-regval-c5831da1bcba-20260514-180755.json` | Complete | Final replay covered 3 regression cases. |
| Detect when a previously fixed vulnerability has reappeared. | `regval-c5831da1bcba` | Complete | Latest replay reports `reappeared=2`. |
| Flag when one fix introduces a regression in another category. | Replay summary and final operator status | Complete | Regression output stores per-finding category and status. |
| Distinguish true fix from model behavior drift. | Regression records compare prior/current verdict and safe/unsafe evidence | Complete | Latest replay marks cost/DoS resolved and attachment reliability reappeared. |

## Observability Layer

| PDF question | Current evidence | Status | Remaining work |
| --- | --- | --- | --- |
| Which attack categories have been tested, and how many cases exist per category? | `deploy/captures/operator-status-final-20260514-180849.json` | Complete | Final status shows 5 categories and 10/10 cases tested. |
| Which categories need deeper attack coverage beyond one seed case? | Final status `next_campaign_recommendation` | Complete | Coverage gaps are closed; recommendations now prioritize weak surfaces. |
| What is the current pass/fail rate across all test categories and system versions? | Final status verdict totals | Complete | Final totals: safe 7, vulnerable 6, partial 4, inconclusive 1, error 0. |
| Is the target becoming more or less resilient over time? | Regression validations `regval-4b592e1ea1b6` and `regval-c5831da1bcba` | Complete | Final replay shows resolved and reappeared counts over time. |
| Which vulnerabilities are open, in progress, or resolved? | Final finding status counts | Complete | Final counts: `approved=1`, `regression_queued=2`, `needs_more_evidence=5`, `rejected=3`. |
| How much did this test run cost, and at what rate is cost scaling? | Run `estimated_cost_usd`; `AI-COST-ANALYSIS.md` | Complete | Final deterministic platform runs stayed at estimated `$0.00`; projections are documented. |
| What is each agent doing, and in what order did it happen? | Final operator status `agent_activity_order` | Complete | Ordered agent activity is captured in final status. |
| Observability is the Orchestrator data substrate, not just a human dashboard. | Final status and final campaign recommendations | Complete | Coverage gaps drove `run-6a5297ca98ab`; weak surfaces drive final recommendations. |

## Submission Requirements

| PDF deliverable | Current evidence | Status | Remaining work |
| --- | --- | --- | --- |
| Repository includes setup guide, architecture overview, deployed link, and run instructions. | `README.md`, `deploy/docs/deployment.md`, `deploy/docs/operator-runbook.md`, `deploy/docs/final-submission-runbook.md`, `SUBMISSION.md` | Complete | Commit/push final docs and captures after review. |
| Threat model with full attack surface map and key-risk summary. | `THREAT_MODEL.md` | Complete | Final evidence aligns with RBAC, attachment, cost/DoS, prompt-state, and tool-scope surfaces. |
| User doc with workflows and automation justification. | `USERS.md` | Complete | Workflows cover campaign, approval, regression, observability, and human review. |
| Architecture doc with summary, agent roles, communication, orchestration, regression harness, observability, tradeoffs, and diagram. | `ARCHITECTURE.md`, `deploy/docs/architecture-defense.md` | Complete | Architecture matches final implemented agent workflow. |
| Demo video, 3-5 minutes, showing live attacks against target. | `deploy/docs/final-demo-script.md`, `deploy/docs/final-demo-shot-list.md` | External | Record and link final video after final run/report curation. |
| Eval dataset with results across at least three attack categories. | `evals/cases/`, `deploy/captures/campaign-run-6a5297ca98ab-20260514-173759.json`, `deploy/captures/attachment-campaign-run-94464fc484ac-20260514-180337.json` | Complete | Final deployed evidence covers 10 cases across 5 categories. |
| Minimum three distinct vulnerability reports. | `evals/reports/find-4e41695d42ec.md`, `evals/reports/find-2f92b8b731b0.md`, `evals/reports/find-63eb1564ab3c.md` | Complete | Three final report lanes are curated and regression-linked. |
| AI cost analysis with actual dev spend and projected 100 / 1K / 10K / 100K costs. | `AI-COST-ANALYSIS.md` includes LLM estimates, infrastructure ranges, and 2026-05-14 pricing assumptions | Complete | Update only if final deployed runs use live provider mode or account plans change. |
| Deployed application with adversarial platform running live tests against deployed target. | AgentForge and target Render URLs; public smoke, authenticated campaigns, curation, and replay captured in `deploy/captures/` | Complete | Final deployed commit `b597142` captured. |
| Final social post on X or LinkedIn tagging `@GauntletAI`. | Not present | External | Draft post in repo and publish/link before final submission. |

## Current Final Evidence Risks

- No deployed findings remain in `needs_approval`; ambiguous cases are `needs_more_evidence`, rejected, or regression queued.
- Development-only approved findings are excluded from final report counts.
- Cost analysis is current as of 2026-05-14; update only if final live-provider runs or hosting plans change.
- Remaining final submission actions are off-repo: record/link demo video and publish/link social post.
- Repository hygiene pass removed the byte-identical duplicate assignment PDF; keep `Week 3 - AgentForge - Adversarial AI Security Platform.pdf` as the canonical local assignment reference.
