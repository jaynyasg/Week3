# AgentForge Final Demo Script

Target length: 3 to 5 minutes.

Use this script after the final authenticated deployed evidence sweep. Fill in the final run, report, and replay IDs before recording.

Recommended recording path: show live `/health`, `/ready`, and `/operator/status` for credibility, then use the captured final artifacts for curated report and regression claims. If you rerun a campaign or replay live during the video, describe those outputs as fresh live results that may differ from the curated final captures.

## Pre-Recording Inputs

| Item | Final value |
| --- | --- |
| Final deployed run ID | `run-6a5297ca98ab`; attachment rerun `run-94464fc484ac` |
| Primary report IDs | `find-4e41695d42ec`, `find-2f92b8b731b0`, `find-63eb1564ab3c` |
| Curated final regression validation ID | `regval-c5831da1bcba` |
| Optional fresh live replay ID | Use the ID returned during recording, for example `regval-14e4a4072305` if using the latest live run. |
| Demo video URL | `TODO` |
| Published social post URL | `TODO` |

## Recording Rules

- Do not show `AGENTFORGE_OPERATOR_TOKEN`, provider keys, Langfuse secrets, cookies, or bearer values.
- Use deployed AgentForge calling the deployed Clinical Co-Pilot target for every final evidence claim.
- Describe judge-flagged findings as unconfirmed. Do not present likely false positives as confirmed target failures.
- Separate curated evidence from fresh live results. Curated evidence is the final checked-in capture/report set; fresh live results prove the system still runs but may need approval or review before becoming final evidence.
- If Render cold-starts during recording, show the latest captured deployed artifacts and call out the warm-up state plainly.

## 0:00 - Opening

Talk track:

> This is AgentForge, an adversarial AI security platform built for the deployed Clinical Co-Pilot target. It is a multi-agent security workflow: the Red Team Agent proposes attacks, the Orchestrator prioritizes weak and under-tested surfaces, the Target Runner calls only the allowlisted deployed target, the Judge Agent evaluates independently, the Documentation Agent turns confirmed failures into reports, and the Regression Harness replays stored exploits after target changes.
>
> Since the MVP, the architecture grew from a bounded campaign runner with reports into a feedback system. I added explicit Human Approver, Regression Harness, and Observability roles, and the Orchestrator now reads coverage gaps, weak surfaces, finding status, regression state, and cost signals. That matters because a security platform should learn what to test next and prove whether fixes hold, not just produce one-off findings.

Show:

- `README.md` deployed links.
- `ARCHITECTURE.md` or `deploy/docs/architecture-defense.md` agent responsibility summary.
- MVP-to-final additions: approval lanes, regression replay, PHI-safe observability, coverage-driven recommendations, and final report curation.

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

If showing the captured final artifacts, say:

> Here is the curated final deployed campaign evidence. This is the checked-in capture I am using for final claims: it comes from deployed AgentForge calling the deployed Clinical Co-Pilot target, and it records the selected cases, target URL, budget, findings, and orchestrator recommendations.

If rerunning live, say:

> I am also going to run a fresh live campaign to show the system still works end to end. This live run is useful operational evidence, but its new findings start in `needs_approval` or review lanes and should not replace the already curated final report evidence without another curation pass.

Show either the fresh campaign request or the final run artifact:

```powershell
$body = @{
  max_cases = 5
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

- Captured final run ID, or the fresh live run ID if rerunning.
- Deployed target URL.
- Attack categories.
- Case IDs.
- Cost estimate and budget fields.
- Selection reasons or orchestrator recommendations.
- If the fresh run returns new findings such as `needs_approval`, say they are uncurated live findings.

Final artifact to show if you do not rerun live during recording:

- `deploy/captures/campaign-run-6a5297ca98ab-20260514-173759.json`
- `deploy/captures/attachment-campaign-run-94464fc484ac-20260514-180337.json`

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

If showing the captured final replay, say:

> In the curated final replay, `regval-c5831da1bcba` replayed all three stored regression cases. It marked the cost/DoS case resolved and the two attachment reliability cases reappeared, which is why the final status artifact shows both resolved and reappeared regression outcomes.

If rerunning live and the output matches `regval-14e4a4072305`, say:

> In this fresh live replay, the harness still replayed all three stored regression cases. The cost/DoS case is resolved, and the two attachment reliability cases are `needs_review` because the LLM fallback judge was unavailable for those inconclusive attachment outcomes. I am not going to call those reappeared in this live run; the important point is that the regression harness separates resolved, reappeared, and needs-review results instead of flattening them into one pass/fail bucket.

Show:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri https://agentforge-security.onrender.com/operator/regressions/replay `
  -Headers $headers `
  -ContentType "application/json" `
  -Body (@{ target_change_id = "render-b597142-2026-05-14"; finding_ids = @() } | ConvertTo-Json) `
  -TimeoutSec 120
```

Call out:

- Replay summary.
- Validation artifact ID or path.
- Per-finding validation status.
- Any reappeared, resolved, or needs-review results.
- If live replay differs from the final capture, narrate the live summary exactly and keep the final capture as the curated report evidence.

Final replay artifact to show if you do not rerun live during recording:

- `deploy/captures/regression-replay-regval-c5831da1bcba-20260514-180755.json`

## 3:40 - Observability And Cost

Talk track:

> Observability is the Orchestrator's data substrate, not just a dashboard. AgentForge records category coverage, verdict rates, finding status, regression state, model/provider metadata, PHI-safe traces, and cost estimates. The cost analysis projects 100, 1,000, 10,000, and 100,000 run volumes so the platform can stay bounded as coverage grows.

Show:

- Expanded `GET /operator/status` observability answers:

```powershell
$status = Invoke-RestMethod `
  -Uri https://agentforge-security.onrender.com/operator/status `
  -Headers $headers `
  -TimeoutSec 30

$status.observability.answers | Format-List
$status.coverage.totals | Format-List
$status.regressions.latest_validation.summary | Format-List
$status.observability.findings.status_counts | Format-List
$status.observability.cost | Format-List
$status.observability.agent_activity_order | Format-Table agent, activity -Wrap
$status.next_campaign_recommendation |
  Select-Object case_id, category, reason, weak_surface_score, tested_case_count, available_case_count |
  Format-Table -Wrap
```

Say:

> PowerShell collapses nested objects in the first status view, so I expand the observability fields directly. These answers show the category and case coverage, finding status counts, regression validation counts, cost summary, agent activity order, and the Orchestrator's next weak-surface recommendations.

- `AI-COST-ANALYSIS.md` cost projection table.
- Langfuse project view if available and secrets are hidden.

## 4:20 - Close

Talk track:

> Compared with the MVP, the final version adds deeper attack coverage, clearer judge evidence handling, coverage-driven prioritization, regression replay, final report curation, cost projections, and a submission package that separates deployed evidence from development artifacts.
>
> The biggest obstacle was evidence quality. Early judge output could flag safe refusals because unsafe terms appeared in echoed prompts, and the attachment flow initially failed before AgentForge sent the target-compatible payload shape. I handled that by separating confirmed, rejected, and needs-more-evidence lanes, replaying approved findings through regression, and rerunning the attachment case after the adapter fix so the final claims are tied to deployed evidence.
>
> During this recording, the live checks also showed the system is still healthy: AgentForge and the Clinical Co-Pilot target returned `ok` or `ready`, the operator status still showed deployed evidence mode with weak-surface recommendations, a fresh campaign completed as `run-c5be40e52ab5`, and a fresh replay `regval-14e4a4072305` replayed all three regression cases with one resolved case and two needs-review attachment cases. I am treating those as current operational results, while the checked-in final artifacts remain the curated submission evidence.

Show:

- `SUBMISSION.md`.
- `docs/submission/platform-requirements-checklist.md`.
- `deploy/docs/final-submission-runbook.md`.
- `deploy/captures/findings-after-third-report-lane-20260514-180841.json`.
- Optional live outputs: `run-c5be40e52ab5` and `regval-14e4a4072305` if you showed them during recording.

End with:

> The remaining off-repo steps are the final video link and the required social post URL. The repository now contains the platform, docs, evidence workflow, and final packaging guide.

## Backup Path

If a live campaign is slow because of Render cold start:

- Show `/health` and `/ready`.
- Show the latest final deployed run JSON.
- Show the matching finding/report/regression artifacts.
- State that the live endpoint is warming and that the artifacts were captured from deployed AgentForge calling the deployed target.
