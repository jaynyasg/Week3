# AgentForge Operator Runbook

Use this runbook when operating the deployed Week 3 security platform.

## Start A Bounded Campaign

```bash
curl -X POST "https://<agentforge-url>/operator/campaigns" \
  -H "Authorization: Bearer <AGENTFORGE_OPERATOR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"case_ids":["rbac-nurse-labs-001"],"max_cases":1,"budget_usd":0.10}'
```

Expected result:

- `evidence_environment` is `deployed`.
- `target_alias` is the configured deployed target.
- `findings` are either approved automatically for lower-risk deterministic
  cases or placed into `needs_approval`.
- `langfuse_trace_id` is populated with the run ID even when Langfuse is
  disabled.
- Default campaigns include `orchestrator_recommendations` so the operator can
  see whether each case was selected for a coverage gap, a weak surface, or an
  explicit request.

## Check Coverage And Priority

```bash
curl "https://<agentforge-url>/operator/status" \
  -H "Authorization: Bearer <AGENTFORGE_OPERATOR_TOKEN>"
```

Expected result:

- `coverage.categories` lists available, tested, and untested case IDs by
  attack category.
- `coverage.weakest_categories` ranks categories with vulnerable, partial,
  error, or unresolved finding history.
- `next_campaign_recommendation` explains which cases the Orchestrator would
  choose next.
- `regressions` summarizes queued regression cases and the latest validation.

## Review Findings

```bash
curl "https://<agentforge-url>/operator/findings?status=needs_approval" \
  -H "Authorization: Bearer <AGENTFORGE_OPERATOR_TOKEN>"
```

High-severity, ambiguous, partial, inconclusive, or LLM-judge-only findings
must be reviewed by a human before they are final evidence.

## Approve Or Reject

Approve:

```bash
curl -X POST "https://<agentforge-url>/operator/findings/<finding-id>/approval" \
  -H "Authorization: Bearer <AGENTFORGE_OPERATOR_TOKEN>" \
  -H "X-AgentForge-Operator: <operator-name>" \
  -H "Content-Type: application/json" \
  -d '{"decision":"approved","rationale":"Evidence is clear and reproducible."}'
```

Request more evidence:

```bash
curl -X POST "https://<agentforge-url>/operator/findings/<finding-id>/approval" \
  -H "Authorization: Bearer <AGENTFORGE_OPERATOR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"decision":"needs_more_evidence","rationale":"Response is ambiguous."}'
```

Approval creates a regression artifact under `evals/regression/` and updates
the finding status to `regression_queued`.

## Replay Regression Cases

```bash
curl -X POST "https://<agentforge-url>/operator/regressions/replay" \
  -H "Authorization: Bearer <AGENTFORGE_OPERATOR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"finding_ids":["<finding-id>"],"target_change_id":"deploy-2026-05-14"}'
```

Expected result:

- The target is called with the original catalog case for each regression.
- Current behavior is re-judged as `resolved`, `reappeared`, or `needs_review`.
- A validation artifact is written under `evals/regression/validations/`.

## Retrieve Artifacts

```bash
curl "https://<agentforge-url>/operator/artifacts/results/<run-id>.json" \
  -H "Authorization: Bearer <AGENTFORGE_OPERATOR_TOKEN>"
```

Reports are under:

```text
evals/reports/<finding-id>.md
```

Regression cases are under:

```text
evals/regression/<finding-id>.json
```

Regression validation results are under:

```text
evals/regression/validations/<validation-id>.json
```

## Evidence Rules

- Use only deployed AgentForge to deployed OpenEMR runs for final submission.
- Keep raw sensitive transcripts out of general logs and Langfuse metadata.
- Preserve approval rationale for high-risk or ambiguous findings.
- Record actual provider/model and cost fields for final cost analysis.
