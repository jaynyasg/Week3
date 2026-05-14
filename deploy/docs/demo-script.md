# AgentForge Demo Script

Target length: **3–5 minutes** (per Week 3 submission rubric). Each step has a concrete action, the exact talking point, and the defense beat the moment is meant to land.

---

## Pre-demo checklist (do not film)

Have these open as separate browser tabs / terminals before recording:

| Tab | URL or file |
| --- | --- |
| 1 | `https://agentforge-security.onrender.com/health` |
| 2 | `https://agentforge-security.onrender.com/ready` |
| 3 | Authenticated `GET /operator/status` response, captured after latest deploy |
| 4 | Latest final deployed run JSON from `evals/results/` |
| 5 | Curated final report from `evals/reports/` |
| 6 | Regression case and latest validation from `evals/regression/` |
| 7 | Judge-flagged or needs-more-evidence finding showing the human gate |
| 8 | Langfuse dashboard filtered to the latest final run trace |
| 9 | Local file: `AI-COST-ANALYSIS.md` (scrolled to *Actual Dev Spend*) |
| 10 | PowerShell window in the repo root, ready to fire one curl/Invoke-RestMethod |

Make sure `AGENTFORGE_OPERATOR_TOKEN` is **not** visible in the recording. Use a profile/window where it isn't echoed in scrollback.

---

## Opening — 0:00–0:20 (≈20s)

**Action:** Title slide or empty terminal showing the repo root.

**Say:**
> "AgentForge is a deployed adversarial security platform for the OpenEMR Clinical Co-Pilot from Week 2. It runs bounded, allowlisted attack campaigns from one deployed app against another deployed app, judges the results independently, learns which attack surfaces look weakest over time, gates high-risk findings on human review, and turns confirmed defects into regression cases. I'll show you one end-to-end run in about four minutes."

**Defense beat:** Multi-agent by role, deployed-to-deployed evidence, human-in-the-loop on risk.

---

## Step 1 — Prove the platform is deployed and healthy — 0:20–0:50 (≈30s)

**Action:** Tab 1 (`/health`) → Tab 2 (`/ready`).

**Show in `/ready`:**
- `"status": "ready"`
- `"target_configured": true`
- `"targets": ["clinical-copilot"]`
- `"evidence_environment": "deployed"`
- `"langfuse_enabled": true`

**Say:**
> "Two deployed services. AgentForge at `agentforge-security.onrender.com`, target Clinical Co-Pilot at `clinical-copilot-4kwb.onrender.com`. Readiness shows the target is configured by deployment secret — operators cannot pass arbitrary URLs in the request body — evidence environment is `deployed` so artifacts from this run will count as submission evidence, and Langfuse tracing is on."

**Defense beats:** Stage 1 hard gate (deployed target URL + live system); R30 allowlist; canonical evidence rule.

**Action:** Authenticated `GET /operator/status`.

**Show in `/operator/status`:**
- `coverage.categories`
- `coverage.weakest_categories`
- `next_campaign_recommendation`
- `observability.answers`
- `regressions`

**Say:**
> "This status endpoint is the operator dashboard for the final submission. It answers which categories have been tested, which still need depth, where the weakest surfaces are, what findings are open, how much the runs cost, and whether regression replay has validation results."

**Defense beats:** Observability is the Orchestrator data substrate, not just a dashboard.

---

## Step 2 — Run a live campaign on camera — 0:50–1:30 (≈40s)

**Action:** PowerShell window. Paste this single command (token from `$env:AGENTFORGE_OPERATOR_TOKEN`, set off-screen earlier):

```powershell
$Base = "https://agentforge-security.onrender.com"
$H = @{ Authorization = "Bearer $env:AGENTFORGE_OPERATOR_TOKEN"; "X-AgentForge-Operator" = "demo" }
$body = @{ case_ids = @("rbac-nurse-labs-001"); max_cases = 1; budget_usd = 0.05 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$Base/operator/campaigns" -Headers $H -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 4
```

**Show in the response:**
- `"target_alias": "clinical-copilot"`
- `"target_url": "https://clinical-copilot-4kwb.onrender.com/agent/chat"`
- `"evidence_environment": "deployed"`
- `"refusal_count"`, `"estimated_cost_usd"`, `"langfuse_trace_id"`

**Say:**
> "I'm starting a bounded campaign — one case, five-cent budget cap. The campaign body never specifies a target URL; the operator can only pick from the configured allowlist. AgentForge's Orchestrator runs the case through the Red Team Agent, the Target Runner posts to the deployed target, the Judge evaluates the response, and Langfuse gets a trace. The whole loop just ran live on the deployed system."

**Defense beats:** F2 + F3 live-deployed exchange; R7 allowlist enforcement; budget cap before any target call.

> *Backup if Render is slow:* skip the live POST, jump to Step 3 with the pre-recorded `run-3fcb420ddc96.json` and explain that a previous deployed campaign produced the same shape.

---

## Step 3 — Show the real finding that broke through — 1:30–2:30 (≈60s)

**Action:** Open the latest curated final deployed run JSON. Scroll to a selected final report finding, then switch to its report in `evals/reports/`.

**Highlight in the report:**
- Finding ID, run ID, case ID, category, verdict, severity, and final lane
- Framework refs
- Clinical impact
- Minimal reproduction
- Expected vs observed behavior
- Fix validation / replay status

**Say:**
> "This is one of the curated final findings. The report is not just a model summary: it has the finding ID, deployed run ID, case ID, framework mapping, clinical impact, minimal reproduction, expected behavior, observed behavior, remediation guidance, current status, and validation state. That is the Documentation Agent's job: turn adversarial evidence into something an engineer can reproduce and fix."

**Defense beats:** AE4 attachment injection; F4 exploit-to-regression; rationale tied to OWASP/MITRE; demonstrates the platform finds *real, reproducible* defects in deployment, not just theoretical jailbreaks.

---

## Step 4 — Show the human-approval gate catching false positives — 2:30–3:15 (≈45s)

**Action:** Open a judge-flagged or `needs_more_evidence` finding.

**Highlight:**
- Judge verdict and confidence
- Human approval/review status
- Approval rationale explaining why it is confirmed, rejected, or judge-flagged

**Say:**
> "The deterministic judge is useful, but the platform does not pretend every automated verdict is final. High-severity, partial, inconclusive, and ambiguous findings are held for human approval. This is how AgentForge keeps judge-flagged evidence visible without mixing it into confirmed vulnerability claims."

**Defense beats:** R9 + R10 independent judge; R24 untrusted-AI-finding policy; explicit human gate prevents false-positive contamination of the regression suite.

---

## Step 5 — Show the regression artifact and Langfuse trace — 3:15–3:55 (≈40s)

**Action:** Open the regression case for the selected confirmed finding, then open the latest validation artifact under `evals/regression/validations/`.

**Highlight:**
- `expected_future_behavior` clause
- `framework_refs` carried forward
- validation status: `resolved`, `reappeared`, or `needs_review`
- `target_change_id` when present

**Say:**
> "When the operator approves a finding, AgentForge writes a regression case. After a target change, `POST /operator/regressions/replay` replays the original catalog case, re-judges the current behavior, and stores a validation artifact. The status is explicit: resolved, reappeared, or needs review."

**Action:** Tab 7 — Langfuse, filter to trace `run-3fcb420ddc96`.

**Show:**
- The trace with observations for the four exchanges
- Score on the trace (verdict + severity + judge mode)
- Metadata: model provider, cost estimate, target alias, evidence environment

**Say:**
> "Langfuse holds metadata-only traces — no raw transcripts or PHI by default. Operators can review every campaign's agent decisions and judge verdicts after the fact, and the trace ID is recorded on the run JSON so submission evidence and observability are linked."

**Defense beats:** F4 regression-as-deterministic test; F5 cost/observability visibility; R22 PHI-safe logging.

---

## Step 6 — Cost story and close — 3:55–4:30 (≈35s)

**Action:** Tab 8 — `AI-COST-ANALYSIS.md`, scroll to *Actual Dev Spend*.

**Highlight:**
- The two real run IDs and their `$0.00` LLM cost
- The 100 / 1K / 10K / 100K projection table

**Say:**
> "The cost analysis separates LLM usage from Render, disk, and Langfuse infrastructure. Deterministic mode keeps hosted-model spend at zero for seed campaigns; live mode adds low-cost Groq mutation and OpenAI judge fallback only when those calls earn their keep. The projection table covers 100, 1,000, 10,000, and 100,000 runs with dated assumptions."

**Closing:**
> "Deployed-to-deployed adversarial testing, multi-agent by role, coverage-driven orchestration, independent judge with a human gate, regression-replayable evidence, framework-mapped findings, PHI-safe observability, low cost. That's AgentForge."

**Defense beats:** F5 cost discipline; AE8 cost analysis evidence; ties the demo back to the original case-study standard.

---

## Defense Beats — quick-fire (use if pressed in Q&A)

- The target is a separate deployed service. AgentForge attacks it; it does not modify it.
- Campaigns cannot scan arbitrary URLs. Target hosts come from deployment secrets, not request bodies.
- The Red Team Agent is one role. The Judge Agent is another. They never share context, so the attack generator never grades itself.
- Deterministic checks judge clear pass/fail cases. Groq `llama-3.1-8b-instant` mutates attacks in `live` mode. OpenAI `gpt-5-nano` is reserved for inconclusive verdicts only.
- High-severity, partial, inconclusive, or LLM-only verdicts require operator approval before becoming reports or regressions.
- Langfuse stores metadata and scores. Raw transcripts stay in controlled artifact storage; no PHI in general logs.
- Final evidence is deployed-to-deployed by design and labeled `evidence_environment=deployed`. Local development runs are explicitly labeled `development` and excluded from submission claims.

---

## Recovery moves (if something breaks on camera)

| Failure | Recovery |
| --- | --- |
| Render cold-start delays the campaign POST | Skip Step 2's live POST, narrate using `evals/results/run-3fcb420ddc96.json` ("here's the same shape from a previous run two minutes ago") |
| Token accidentally visible in shell | Stop, blank the terminal, rotate `AGENTFORGE_OPERATOR_TOKEN` after recording, re-record the affected segment |
| Langfuse view loads slowly | Skip Tab 7, point at `langfuse_trace_id` field in the run JSON: "trace ID is recorded; we can pull it after this." |
| Browser tabs out of order | Use the file paths in `evals/` directly from VS Code rather than browser tabs |

---

## Appendix — tool decisions

| Tool | Why chosen | Alternative considered | Why not |
| --- | --- | --- | --- |
| FastAPI | Matches Week 2 and keeps a small deployable API surface | Flask | Less alignment with existing target app |
| Render | Matches Week 2 deployment story and supports a persistent disk | Fly.io | Adds another deployment narrative |
| Groq `llama-3.1-8b-instant` | Low-cost, fast red-team mutation | Premium model for all attacks | Too expensive for high-volume testing |
| OpenAI `gpt-5-nano` | Low-cost judge fallback / docs | Same model as red team | Shared blind spots |
| Deterministic judge | Repeatable clear pass/fail checks | LLM-only judge | More expensive and less defensible |
| Langfuse | Trace and score review for LLM systems | Plain logs only | Harder to inspect model disagreement |
| Human approval queue | Keeps severe / ambiguous evidence honest | Auto-finalize all findings | Too risky for healthcare security claims |
