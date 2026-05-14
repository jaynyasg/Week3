# AgentForge Final Demo Script

Target length: 3 to 5 minutes.

Use this script after the final authenticated deployed evidence sweep. Fill in the final run, report, and replay IDs before recording.

## Pre-Recording Inputs

| Item | Final value |
| --- | --- |
| Final deployed run ID | `TODO` |
| Primary report IDs | `TODO` |
| Regression replay or validation ID | `TODO` |
| Demo video URL | `TODO` |
| Published social post URL | `TODO` |

## Recording Rules

- Do not show `AGENTFORGE_OPERATOR_TOKEN`, provider keys, Langfuse secrets, cookies, or bearer values.
- Use deployed AgentForge calling the deployed Clinical Co-Pilot target for every final evidence claim.
- Describe judge-flagged findings as unconfirmed. Do not present likely false positives as confirmed target failures.
- If Render cold-starts during recording, show the latest captured deployed artifacts and call out the warm-up state plainly.

## 0:00 - Opening

Talk track:

> This is AgentForge, an adversarial AI security platform built for the deployed Clinical Co-Pilot target. It is a multi-agent security workflow: the Red Team Agent proposes attacks, the Orchestrator prioritizes weak and under-tested surfaces, the Target Runner calls only the allowlisted deployed target, the Judge Agent evaluates independently, the Documentation Agent turns confirmed failures into reports, and the Regression Harness replays stored exploits after target changes.

Show:

- `README.md` deployed links.
- `ARCHITECTURE.md` or `deploy/docs/architecture-defense.md` agent responsibility summary.

## 0:30 - Deployed Readiness

Talk track:

> Final evidence is deployed-to-deployed. The platform is live, the target is live, and the readiness endpoint confirms this run is using the deployed evidence environment.

Show:

```powershell
Invoke-RestMethod -Uri https://agentforge-security.onrender.com/health -TimeoutSec 20
Invoke-RestMethod -Uri https://agentforge-security.onrender.com/ready -TimeoutSec 20
Invoke-RestMethod -Uri https://clinical-copilot-4kwb.onrender.com/agent/health -TimeoutSec 20
```

Expected proof points:

- AgentForge health returns `status=ok`.
- AgentForge readiness returns `status=ready`.
- Readiness shows `target_configured=true`.
- Readiness shows `evidence_environment=deployed`.
- Target health returns `status=ok`.

## 0:55 - Operator Status And Learning Loop

Talk track:

> The Orchestrator is not just running a static checklist. It reads coverage, unresolved findings, regression state, and weak surfaces, then turns that history into recommendation reasons for the next campaign.

Show authenticated operator status without exposing the token:

```powershell
$headers = @{ Authorization = "Bearer $env:AGENTFORGE_OPERATOR_TOKEN" }
Invoke-RestMethod -Uri https://agentforge-security.onrender.com/operator/status -Headers $headers -TimeoutSec 30
```

Call out:

- Category coverage.
- Weakest or gap categories.
- Finding status counts.
- Regression validation counts.
- `next_campaign_recommendation` or equivalent orchestrator recommendation output.

## 1:35 - Live Or Latest Final Campaign

Talk track:

> Here is the final deployed campaign. The Orchestrator selects cases from the attack catalog, applies budget controls, preserves run metadata, and records why these cases were prioritized.

Show either the fresh campaign request or the final run artifact:

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

Call out:

- Final run ID.
- Deployed target URL.
- Attack categories.
- Case IDs.
- Cost estimate and budget fields.
- Selection reasons or orchestrator recommendations.

## 2:15 - Finding Review And Report Quality

Talk track:

> Findings do not become submission evidence just because a judge flagged them. AgentForge preserves the raw evidence, then requires a human lane: confirmed, rejected, judge-flagged, or needs more evidence. The final report includes severity, clinical impact, reproduction steps, expected versus observed behavior, remediation, and validation status.

Show:

- A curated `evals/results/findings/find-*.json`.
- A matching `evals/reports/find-*.md`.

Call out:

- Finding ID and run ID.
- Approval or review history.
- Expected safe behavior.
- Observed behavior.
- Clinical impact.
- Remediation guidance.

## 3:00 - Regression Replay

Talk track:

> Confirmed findings are converted into replayable regression cases. When the target changes, the harness can replay stored exploits and classify them as resolved, reappeared, or needing review, which is how the platform detects whether the target is becoming more or less resilient over time.

Show:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri https://agentforge-security.onrender.com/operator/regressions/replay `
  -Headers $headers `
  -TimeoutSec 120
```

Call out:

- Replay summary.
- Validation artifact ID or path.
- Per-finding validation status.
- Any reappeared, resolved, or needs-review results.

## 3:40 - Observability And Cost

Talk track:

> Observability is the Orchestrator's data substrate, not just a dashboard. AgentForge records category coverage, verdict rates, finding status, regression state, model/provider metadata, PHI-safe traces, and cost estimates. The cost analysis projects 100, 1,000, 10,000, and 100,000 run volumes so the platform can stay bounded as coverage grows.

Show:

- `GET /operator/status` observability answers.
- `AI-COST-ANALYSIS.md` cost projection table.
- Langfuse project view if available and secrets are hidden.

## 4:20 - Close

Talk track:

> Compared with the MVP, the final version adds deeper attack coverage, clearer judge evidence handling, coverage-driven prioritization, regression replay, final report curation, cost projections, and a submission package that separates deployed evidence from development artifacts.

Show:

- `SUBMISSION.md`.
- `docs/submission/platform-requirements-checklist.md`.
- `deploy/docs/final-submission-runbook.md`.

End with:

> The remaining off-repo steps are the final video link and the required social post URL. The repository now contains the platform, docs, evidence workflow, and final packaging guide.

## Backup Path

If a live campaign is slow because of Render cold start:

- Show `/health` and `/ready`.
- Show the latest final deployed run JSON.
- Show the matching finding/report/regression artifacts.
- State that the live endpoint is warming and that the artifacts were captured from deployed AgentForge calling the deployed target.

