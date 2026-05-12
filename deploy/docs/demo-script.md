# AgentForge Demo Script

## Opening

"AgentForge is the deployed security app for Week 3. It attacks the deployed
OpenEMR Clinical Co-Pilot target within an allowlist, preserves evidence, and
turns confirmed failures into reports and regression cases."

## Walkthrough

1. Open the deployed AgentForge `/ready` endpoint.
2. Show that `evidence_environment` is `deployed`.
3. Show the configured target alias without exposing secrets.
4. Start a bounded campaign with one RBAC/PHI case.
5. Open the run artifact under `evals/results/`.
6. Show the Judge Agent verdict and evidence fields.
7. Open `needs_approval` findings.
8. Approve one high-severity finding with rationale.
9. Show the generated report under `evals/reports/`.
10. Show the regression artifact under `evals/regression/`.
11. Show the Langfuse metadata payload or trace if enabled.
12. Show cost projections in `AI-COST-ANALYSIS.md`.

## Defense Beats

- The target is separate from the security platform.
- Campaigns cannot scan arbitrary URLs.
- Groq generates red-team mutations; deterministic rules judge first.
- OpenAI `gpt-5-nano` is only a fallback for semantic gray areas.
- Human approval is required for high-severity or ambiguous findings.
- Langfuse receives metadata and scores, not raw PHI-like transcripts by default.
- Final evidence is deployed-to-deployed, not local.

## Appendix

| Tool | Why chosen | Alternative considered | Why not |
| --- | --- | --- | --- |
| FastAPI | Matches Week 2 and keeps a small deployable API surface | Flask | Less alignment with existing target app |
| Render | Matches Week 2 deployment story and supports a persistent disk | Fly.io | Adds another deployment narrative |
| Groq `llama-3.1-8b-instant` | Low-cost, fast red-team mutation | Premium model for all attacks | Too expensive for high-volume testing |
| OpenAI `gpt-5-nano` | Low-cost judge fallback/docs | Same model as red team | Shared blind spots |
| Deterministic judge | Repeatable clear pass/fail checks | LLM-only judge | More expensive and less defensible |
| Langfuse | Trace and score review for LLM systems | Plain logs only | Harder to inspect model disagreement |
| Human approval queue | Keeps severe/ambiguous evidence honest | Auto-finalize all findings | Too risky for healthcare security claims |
