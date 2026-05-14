# AgentForge Final Evidence Sweep

**Date:** 2026-05-14  
**Scope:** ce-work execution pass against the final submission plan.

## Public Deployed Smoke

| Check | Result |
| --- | --- |
| AgentForge `/health` | `status=ok` |
| AgentForge `/ready` | `status=ready` |
| AgentForge target configured | `targets=["clinical-copilot"]` |
| AgentForge evidence environment | `deployed` |
| AgentForge provider mode | `deterministic` |
| Langfuse | enabled and configured |
| Clinical Co-Pilot `/agent/health` | `status=ok` |
| Unauthenticated `/operator/status` | `401` as expected |

## Authenticated Evidence Capture

Authenticated final evidence capture was not run in this shell because `AGENTFORGE_OPERATOR_TOKEN` is not set locally.

Before recording the final demo or closing submission packaging, set the token off-screen and run:

```powershell
$Base = "https://agentforge-security.onrender.com"
$H = @{ Authorization = "Bearer $env:AGENTFORGE_OPERATOR_TOKEN"; "X-AgentForge-Operator" = "final-demo" }

Invoke-RestMethod -Uri "$Base/operator/status" -Headers $H | ConvertTo-Json -Depth 8

$body = @{ max_cases = 3; budget_usd = 0.10 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$Base/operator/campaigns" -Headers $H -ContentType "application/json" -Body $body | ConvertTo-Json -Depth 8

$replay = @{ target_change_id = "final-main-2026-05-14" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "$Base/operator/regressions/replay" -Headers $H -ContentType "application/json" -Body $replay | ConvertTo-Json -Depth 8
```

## Acceptance Criteria For Final Capture

- `GET /operator/status` includes `coverage`, `next_campaign_recommendation`, `observability`, and `regressions`.
- The campaign response has `evidence_environment=deployed`.
- The campaign response records `orchestrator_recommendations`.
- At least three attack categories are represented across final deployed evidence.
- Reports are regenerated from curated deployed findings after approval/replay decisions.
- Confirmed findings have regression cases and, where possible, replay validation artifacts.
- Judge-flagged findings remain clearly labeled as unconfirmed or needs-more-evidence.
