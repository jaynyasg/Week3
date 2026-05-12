# Architecture defense - talking points

_Last updated: 2026-05-12 (Week 3 planning foundation)._

Companion to the Week 3 demo script and `ARCHITECTURE.md`. One paragraph per major architecture decision, in the order a grader is likely to ask about them. Read this before the defense; do not read it on camera.

The strongest single beat is the **independent judge plus deterministic regression harness**. If there is time for only one architecture point, lead with this: AgentForge does not ask the same LLM that generated an attack to decide whether the attack worked, and high-severity or ambiguous findings require human approval before they become final evidence.

---

## ADR-001 - Deployed AgentForge to deployed OpenEMR is canonical

**The decision:** final testing evidence must come from the deployed AgentForge security platform running against the deployed OpenEMR / Clinical Co-Pilot target. Local runs are development-only evidence.

**Why:** the assignment requires live testing against the deployed target, and the security app itself must also be deployed. Treating local output as final evidence would test a different system shape than the demo and submission.

**Evidence:** `ARCHITECTURE.md` names the deployment-to-deployment boundary; the plan requires artifacts to label `evidence_environment` so local traces cannot be confused with deployed evidence.

**Defense one-liner:** "Local tests help us build; deployed-to-deployed runs are the only evidence we submit."

---

## ADR-002 - AgentForge is separate from the target

**The decision:** AgentForge is built as a separate FastAPI security app instead of modifying the Week 2 Clinical Co-Pilot target into a self-attacking system.

**Why:** the target must remain stable so attacks measure the deployed Clinical Co-Pilot behavior. A separate platform also makes trust boundaries visible: operator, target allowlist, LLM provider, evidence storage, and reporting all sit outside the clinical app.

**Evidence:** Week 2 target surfaces are referenced through `Week2 - Test Suite/`, especially `agent/http/routes_chat.py`, `agent/http/deps.py`, `agent/tools/dispatch.py`, `agent/access/rbac.py`, and `render.yaml`.

**Defense one-liner:** "We do not grade a changed target; we attack the deployed target from a separate deployed security app."

---

## ADR-003 - Target allowlist, not arbitrary scanning

**The decision:** campaign execution can call only deployment-configured allowlisted targets. Operators cannot submit arbitrary public URLs to scan.

**Why:** the project is authorized adversarial testing of a known healthcare AI target, not a general offensive scanner. This protects the platform from misuse and keeps legal/scope boundaries clear.

**Evidence:** `ARCHITECTURE.md` defines a target boundary; the implementation plan requires target override rejection and explicit deployed target configuration.

**Defense one-liner:** "The runner has a steering wheel, but the road is fenced: only the authorized deployed target is reachable."

---

## ADR-004 - Independent judge with deterministic checks and approval first

**The decision:** the Red Team Agent generates attacks, but the Judge Agent evaluates results from separate context. Deterministic checks handle clear failures before any LLM judge is used. High-severity, partial, inconclusive, or LLM-judge-only findings move to `needs_approval` before report finalization or regression promotion.

**Why:** LLM-as-judge can hallucinate, over-trust a plausible response, or share blind spots with the attack generator. Deterministic checks are cheaper and more repeatable for obvious failures like PHI leakage, wrong-role data access, patient-scope mismatch, target override, and missing refusal. Human approval keeps security claims from being auto-promoted when the evidence is severe or uncertain.

**Evidence:** OWASP and NIST both emphasize testing, measurement, and human/technical verification. The plan includes judge goldens before relying on ambiguous semantic judging, and the architecture defines the finding state machine `draft -> needs_approval -> approved -> regression_queued`.

**Defense one-liner:** "The platform does not trust an LLM to grade itself; clear failures are deterministic, and severe or ambiguous cases need a human sign-off."

---

## ADR-005 - Low-cost hosted model routing

**The decision:** deployed campaigns use Groq `llama-3.1-8b-instant` as the default Red Team Agent generator and OpenAI `gpt-5-nano` as the default LLM fallback for ambiguous judge decisions and documentation drafting. Both sit behind role-specific provider settings so they can be swapped if credentials, pricing, or refusal behavior change.

**Why:** the platform itself is deployed, so deployed campaigns need hosted inference. Groq gives a fast, low-cost mutation path for high-volume authorized tests; `gpt-5-nano` is a low-cost classification/summarization fit for the much smaller fallback judge path. Separating the red-team and judge model reduces shared blind spots.

**Evidence:** the cost plan tracks Red Team, Judge, Documentation, retries, refusals, and target infrastructure separately. The architecture records provider/model metadata on every run so actual refusal rate, latency, and spend can override assumptions.

**Defense one-liner:** "Groq mutates attacks cheaply; deterministic rules judge first; `gpt-5-nano` only helps when the result is semantically gray."

---

## ADR-006 - Persistent deployed artifacts

**The decision:** deployed run artifacts must be written to persistent storage, not ephemeral container files.

**Why:** evidence has to survive restarts and be retrievable for grading. If a deployed run disappears on restart, the platform cannot defend the result as submission evidence.

**Evidence:** the implementation plan adds `AGENTFORGE_ARTIFACT_DIR` as deployment-critical configuration and requires readiness to warn or fail when deployed storage is not persistent.

**Defense one-liner:** "A finding that disappears on restart is not evidence; deployed artifacts must be durable."

---

## ADR-007 - Framework-mapped findings

**The decision:** attack cases, threat-model entries, and vulnerability reports include framework references such as OWASP LLM Top 10, OWASP MCP Top 10, MITRE ATLAS, NIST AI 600-1, and CISA/NCSC guidance.

**Why:** the goal is to lean into known LLM security work rather than invent a private taxonomy. Framework refs make findings easier for security reviewers to understand and compare.

**Evidence:** the origin requirements define `framework_refs`; `THREAT_MODEL.md` maps categories to known frameworks and Week 2 code surfaces.

**Defense one-liner:** "Our categories are not vibes; they trace to the security community's existing maps."

---

## ADR-008 - PHI-safe Langfuse observability

**The decision:** Langfuse is the LLM observability sink for traces, observations, and scores. It records campaign metadata, model/provider, latency, token/cost estimates, refusal count, verdict, severity, judge mode, and approval status. Raw transcripts and PHI-like content remain deliberate artifacts with controlled access unless the deployment explicitly opts into a private Langfuse data boundary.

**Why:** adversarial testing of a healthcare AI target can create sensitive transcripts. Logging everything would turn observability into an exfiltration surface. Langfuse is useful because it supports traces and scores for LLM systems, but it must remain metadata-first for this healthcare demo.

**Evidence:** Week 2 already uses a PHI-safe logging policy in `Week2 - Test Suite/docs/PHI-LOGGING-POLICY.md`; AgentForge inherits that posture for run events and reports. Langfuse scores can store final verdict, confidence, and approval status without copying raw evidence into general telemetry.

**Defense one-liner:** "Langfuse tells us what happened and how confident we are, while the sensitive evidence stays in controlled artifacts."

---

## What is not built intentionally

- No arbitrary internet scanner.
- No automated remediation or patch generation.
- No replacement for OpenEMR access control.
- No clinical decision support for end users.
- No local-only evidence path for final submission.
- No claim that LLM-as-judge is sufficient without deterministic checks and goldens.
- No final high-severity or ambiguous finding without human approval.

---

## Test and eval evidence to show

- Deployed AgentForge platform URL.
- Deployed OpenEMR / Clinical Co-Pilot target URL.
- A bounded campaign launched from deployed AgentForge.
- At least three attack categories represented in `evals/`.
- A target override rejection.
- Independent judge verdicts with evidence.
- Human approval audit record for any high-severity or ambiguous finding.
- Langfuse trace or exported score showing model, judge mode, verdict, confidence, and approval status.
- Vulnerability reports under `evals/reports/`.
- Cost report with 100, 1K, 10K, and 100K run projections.
