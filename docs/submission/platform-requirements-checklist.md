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
| Multi-agent architecture is mandatory; a single-agent or plain pipeline architecture does not satisfy the assignment. | `ARCHITECTURE.md`, `USERS.md`, `agentforge/` role modules, `deploy/docs/architecture-defense.md` | Partial | Final architecture wording should describe implemented state, not MVP aspiration, after the final code pass. |
| Each agent has distinct responsibilities, context, decision authority, inputs, outputs, trust level, and coordination path. | `ARCHITECTURE.md` agent responsibility table; `USERS.md` agent trust matrix | Partial | Add/confirm exact final inputs, outputs, and trust levels for Red Team, Judge, Orchestrator, Documentation, Regression, Observability, and Human Approver. |
| Red Team capability: generate novel adversarial inputs. | `agentforge/attacks/`, `evals/cases/*.yaml`, provider routing in AgentForge | Partial | Final evidence should show either live mutation or clearly documented deterministic seed mode plus mutation-ready provider path. |
| Red Team capability: mutate partially successful attacks to probe bypasses. | Final plan calls for this in U2/U5; seed cases exist | Partial | Implement or document mutation behavior for partial findings, and cite at least one artifact or test. |
| Red Team capability: target multi-turn attack sequences, not only single prompts. | `evals/cases/cross_patient_history_injection.yaml`, run artifacts | Partial | Ensure final run/report includes multi-turn evidence or explicitly marks the multi-turn case status. |
| Judge capability: evaluate attack success with consistent criteria across runs and versions. | `agentforge/judge/`, `evals/goldens/judge_cases.json`, `tests/agentforge/test_judge_goldens.py` | Partial | Harden false-positive handling and expand goldens for safe refusal, echoed attack text, partial/server-error, and inconclusive cases. |
| Judge independence: attack generation and attack evaluation must not happen in the same context. | Architecture docs and separate `attacks`, `judge`, and `orchestrator` modules | Partial | Keep final docs explicit that the red-team generator does not self-grade. |
| Orchestrator capability: prioritize attack surfaces based on coverage gaps, weak surfaces learned over time, and unresolved findings. | `agentforge/orchestrator/coverage.py`, `agentforge/orchestrator/priority.py`, default campaign `selection_reasons`, run `orchestrator_recommendations`, `GET /operator/status` | Partial | Deploy latest code, run/capture final operator status and campaign JSON showing recommendation reasons and weakest/gap categories. |
| Orchestrator capability: halt or redirect when cost accumulates without signal. | `AI-COST-ANALYSIS.md`, campaign `budget_usd`, `estimated_cost_usd` fields | Partial | Add final demo/status evidence for budget halt or skip reason; replace `TBD` infrastructure costs. |
| Orchestrator capability: trigger regression runs when the target changes. | `POST /operator/regressions/replay`, `evals/regression/*.json`, `evals/regression/validations/*.json`, `deploy/docs/operator-runbook.md` | Partial | Deploy latest code and capture final replay validation artifact after a target-change marker. |
| Model/provider choice is deliberate and defensible, including cost and refusal behavior. | `ARCHITECTURE.md`, `AI-COST-ANALYSIS.md`, Groq/OpenAI model choices | Partial | Recheck pricing before final submission and record final assumptions/date. |

## Documentation Agent

| PDF report requirement | Current evidence | Status | Remaining work |
| --- | --- | --- | --- |
| Unique identifier and severity rating. | `evals/reports/*.md`, `evals/results/findings/*.json` | Partial | Ensure every final report uses the same finding ID and severity as canonical finding JSON. |
| Clear vulnerability description and clinical impact. | `agentforge/reporting/vulnerability_report.py` now renders a dedicated clinical impact section by category | Partial | Regenerate final reports from curated deployed findings. |
| Minimal reproducible attack sequence. | Reports now include target, run ID, case ID, role, patient context, attachment count, and campaign/replay path | Partial | Regenerate final reports from curated deployed findings. |
| Observed versus expected behavior. | New findings store `expected_safe_behavior`; reports render expected and observed behavior sections | Partial | Regenerate final reports from curated deployed findings. |
| Recommended remediation approach. | Reports now render category-specific remediation guidance | Partial | Confirm final report wording against the deployed target behavior. |
| Current status and fix validation results. | Reports now render approval status and replay/validation guidance | Partial | Regenerate reports after approval/replay so status and validation are current. |
| Senior engineer can reproduce, validate, and fix from the report alone. | Report generator now includes reproduction, impact, expected/observed behavior, remediation, and validation sections | Partial | Curate at least three final reports with explicit lanes: confirmed or judge-flagged/unconfirmed. |

## Regression And Validation Harness

| PDF requirement | Current evidence | Status | Remaining work |
| --- | --- | --- | --- |
| Store confirmed exploits in a versioned, queryable format. | `evals/regression/*.json` | Partial | Ensure only deployed confirmed findings are promoted to final regression inventory, or mark non-final files clearly. |
| Run full regression suite automatically when triggered by the Orchestrator. | `POST /operator/regressions/replay` replays stored regression cases and can be scoped by finding IDs or run across the queue | Partial | Capture a final deployed replay response/validation artifact. |
| Detect when a previously fixed vulnerability has reappeared. | Regression validation results store prior verdict, current verdict, and `resolved`/`reappeared`/`needs_review` status | Partial | Run final replay against deployed target after latest deploy. |
| Flag when one fix introduces a regression in another category. | Replay summary and `GET /operator/status` expose validation counts; per-result categories are stored in validation artifacts | Partial | Capture a multi-category replay artifact or note insufficient final regression inventory. |
| Distinguish true fix from model behavior drift. | Architecture docs mention this risk | Partial | Regression criteria must check target behavior against explicit expected safe behavior, not only changed text. |

## Observability Layer

| PDF question | Current evidence | Status | Remaining work |
| --- | --- | --- | --- |
| Which attack categories have been tested, and how many cases exist per category? | `GET /operator/status` coverage summary, `agentforge/orchestrator/coverage.py`, `evals/cases/` | Partial | Capture final deployed status output after the latest deploy. |
| Which categories need deeper attack coverage beyond one seed case? | Ten seed/depth cases in `evals/cases/`; coverage tracks tested versus available case IDs and feeds `next_campaign_recommendation` | Partial | Capture final deployed recommendation output after the latest deploy. |
| What is the current pass/fail rate across all test categories and system versions? | Coverage summary includes verdict counts by category and global totals | Partial | Add target version/change marker or note insufficient longitudinal data in final demo/docs. |
| Is the target becoming more or less resilient over time? | Regression validations and run history can show resolved/reappeared counts over time | Partial | Capture final replay artifact or mark longitudinal trend as insufficient data if only one validation exists. |
| Which vulnerabilities are open, in progress, or resolved? | Finding JSON statuses plus coverage `finding_status_counts` | Partial | Normalize final lanes after approval/replay and capture final status counts. |
| How much did this test run cost, and at what rate is cost scaling? | Run `estimated_cost_usd`; `AI-COST-ANALYSIS.md` | Partial | Complete infrastructure estimates and final actual-spend table. |
| What is each agent doing, and in what order did it happen? | Langfuse metadata and run artifacts are described | Partial | Ensure local artifacts or operator status show ordered activity when Langfuse is unavailable. |
| Observability is the Orchestrator data substrate, not just a human dashboard. | Coverage/status summaries now feed default campaign selection and are exposed through `GET /operator/status` | Partial | Deploy latest code and capture final status/campaign artifacts as submission evidence. |

## Submission Requirements

| PDF deliverable | Current evidence | Status | Remaining work |
| --- | --- | --- | --- |
| Repository includes setup guide, architecture overview, deployed link, and run instructions. | `README.md`, `deploy/docs/deployment.md`, `deploy/docs/operator-runbook.md` | Partial | Add final checklist links and push final branch. |
| Threat model with full attack surface map and key-risk summary. | `THREAT_MODEL.md` | Partial | Review after final evidence to align highest-risk categories. |
| User doc with workflows and automation justification. | `USERS.md` | Partial | Review after final evidence for final user/report workflow accuracy. |
| Architecture doc with summary, agent roles, communication, orchestration, regression harness, observability, tradeoffs, and diagram. | `ARCHITECTURE.md`, `deploy/docs/architecture-defense.md` | Partial | Final-pass stale MVP language and make regression/observability claims match implementation. |
| Demo video, 3-5 minutes, showing live attacks against target. | `deploy/docs/demo-script.md` | External | Record and link final video after final run/report curation. |
| Eval dataset with results across at least three attack categories. | `evals/cases/`, `evals/results/run-3fcb420ddc96.json` | Partial | Curate final deployed run artifacts and exclude development runs from final claims. |
| Minimum three distinct vulnerability reports. | `evals/reports/*.md` | Partial | Approve/reject/replay findings and produce at least three defensible final reports across confirmed and judge-flagged lanes. |
| AI cost analysis with actual dev spend and projected 100 / 1K / 10K / 100K costs. | `AI-COST-ANALYSIS.md` | Partial | Replace infrastructure `TBD` values and update final actual-spend language. |
| Deployed application with adversarial platform running live tests against deployed target. | AgentForge and target Render URLs; current deployed run artifacts | Partial | Run final smoke and final deployed campaign after last code deploy. |
| Final social post on X or LinkedIn tagging `@GauntletAI`. | Not present | External | Draft post in repo and publish/link before final submission. |

## Current Final Evidence Risks

- Some report and regression artifacts exist for findings that are still `needs_approval`, creating lifecycle drift.
- At least two deployed findings may be deterministic judge false positives caused by unsafe terms in echoed prompt text.
- Development-only approved findings must not be counted as final deployed vulnerabilities.
- The cost analysis still has `TBD` infrastructure estimates.
- There is no recorded final demo video link or social post link.
- There are two assignment PDFs in the repo root; decide whether the duplicate belongs in the final submission.
