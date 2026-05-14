# AgentForge Final Submission Runbook

This runbook is the final packaging guide for the Week 3 submission. It is not equivalent to `deploy/docs/operator-runbook.md`.

The operator runbook explains how to use AgentForge's protected APIs day to day. This final submission runbook explains how to collect, curate, record, link, and verify every final deliverable required by the assignment.

## Completion Standard

Do not mark the final submission complete until all of these are true:

- Latest `main` is deployed.
- Public health and readiness checks pass.
- Authenticated operator status is captured with `evidence_environment=deployed`.
- A final deployed campaign or replay is captured after the latest deploy.
- At least three final vulnerability reports have deliberate final lanes: confirmed, judge-flagged/unconfirmed, rejected, or excluded.
- Confirmed findings have approval history and regression or validation status.
- `SUBMISSION.md` contains final run IDs, report IDs, replay IDs, demo URL, and social post URL.
- The 3 to 5 minute demo video is recorded.
- The required X or LinkedIn post tagging `@GauntletAI` is published and linked.

## 1. Confirm Repository And Deployment State

Work on `main`.

```powershell
git status --short --branch
git log --oneline -5
```

Confirm the deployment platform has picked up the latest `main` commit before capturing final evidence. If the deploy is still in progress, wait for it to complete.

## 2. Run Public Smoke Checks

```powershell
Invoke-RestMethod -Uri https://agentforge-security.onrender.com/health -TimeoutSec 20
Invoke-RestMethod -Uri https://agentforge-security.onrender.com/ready -TimeoutSec 20
Invoke-RestMethod -Uri https://clinical-copilot-4kwb.onrender.com/agent/health -TimeoutSec 20
```

Required results:

- AgentForge `/health` returns `status=ok`.
- AgentForge `/ready` returns `status=ready`.
- AgentForge `/ready` shows `target_configured=true`.
- AgentForge `/ready` shows `evidence_environment=deployed`.
- Clinical Co-Pilot `/agent/health` returns `status=ok`.

Record the date, time, and outputs in `SUBMISSION.md` or `deploy/docs/final-evidence-sweep.md`.

## 3. Prepare Authenticated Operator Access

Set the operator token locally without printing it in terminal output, screenshots, or the final demo.

```powershell
$env:AGENTFORGE_OPERATOR_TOKEN = "<set locally, do not record>"
$headers = @{ Authorization = "Bearer $env:AGENTFORGE_OPERATOR_TOKEN" }
```

Check authenticated status:

```powershell
Invoke-RestMethod -Uri https://agentforge-security.onrender.com/operator/status -Headers $headers -TimeoutSec 30
```

Capture proof points:

- Category coverage.
- Weak or gap categories.
- Finding status counts.
- Regression summary.
- Orchestrator next-campaign recommendation.
- Model/provider and cost metadata if present.

## 4. Run The Final Deployed Campaign

Use a bounded final campaign so it is demo-friendly and budget-safe.

```powershell
$body = @{
  max_cases = 3
  categories = @(
    "rbac_phi_exfiltration",
    "prompt_injection",
    "tool_misuse"
  )
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri https://agentforge-security.onrender.com/operator/campaigns `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body `
  -TimeoutSec 120
```

Required artifact checks:

- Run artifact has `evidence_environment=deployed`.
- Run target URL is `https://clinical-copilot-4kwb.onrender.com`.
- Run includes at least three attack categories across the final evidence set.
- Run includes case IDs, verdicts, expected safe behavior, observed behavior, and cost estimates.
- Run includes selection reasons or orchestrator recommendation data when available.

## 5. Curate Findings

Review every deployed finding before treating it as final evidence.

Use these final lanes:

- `confirmed`: target behavior is a defensible vulnerability.
- `judge_flagged_unconfirmed`: useful evidence of the judge and review gate, but not a confirmed target failure.
- `rejected`: false positive or safe target behavior.
- `excluded`: development-only, local-only, or otherwise not final submission evidence.

Final report rule:

- Confirmed findings may be counted as vulnerability reports.
- Judge-flagged findings may be shown as platform evidence, but label them clearly.
- Development-only findings must not be counted as deployed final vulnerabilities.

Regenerate final reports after status changes so Markdown reports, finding JSON, approval history, and regression state agree.

## 6. Capture Regression Replay

Replay the final regression inventory after findings are curated.

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri https://agentforge-security.onrender.com/operator/regressions/replay `
  -Headers $headers `
  -TimeoutSec 120
```

Capture:

- Replay or validation ID.
- Finding IDs included.
- Prior verdict versus current verdict.
- `resolved`, `reappeared`, or `needs_review` classification.
- Any category where a fix appears to cause a new regression.

## 7. Update Final Submission Files

Update these files after final evidence capture:

- `SUBMISSION.md`
- `docs/submission/platform-requirements-checklist.md`
- `deploy/docs/final-evidence-sweep.md`
- `deploy/docs/final-demo-script.md`
- `deploy/docs/final-demo-shot-list.md`
- `deploy/docs/social-post.md` after publishing

The final control files should cite concrete IDs instead of placeholders:

- Final deployed run ID.
- Final finding IDs.
- Final report paths.
- Regression validation ID or path.
- Demo video URL.
- Social post URL.

## 8. Record The Demo

Use:

- `deploy/docs/final-demo-script.md`
- `deploy/docs/final-demo-shot-list.md`

Video requirements:

- 3 to 5 minutes.
- Show live deployed AgentForge and deployed Clinical Co-Pilot evidence.
- Show multi-agent architecture and why the agents have separate responsibilities.
- Show at least one deployed campaign or latest deployed run artifact.
- Show curated finding/report evidence.
- Show regression replay or validation artifact.
- Show cost and observability summary.

## 9. Publish The Social Post

Use `deploy/docs/social-post.md` as the draft source. Publish on X or LinkedIn and tag `@GauntletAI`.

After publishing, add the URL to:

- `SUBMISSION.md`
- `deploy/docs/social-post.md`
- `deploy/docs/final-demo-script.md` pre-recording inputs if recording after publication

## 10. Final Verification

Run the test suite before final commit if any code changed:

```powershell
python -m pytest tests\agentforge -q
```

For documentation-only changes, at minimum re-run:

```powershell
git status --short --branch
git diff --check
```

Final repository gate:

- `main` contains the final docs and evidence references.
- No duplicate assignment PDF is reintroduced.
- No token, provider key, cookie, or secret appears in committed artifacts.
- All final claims in `SUBMISSION.md` are backed by deployed evidence.

