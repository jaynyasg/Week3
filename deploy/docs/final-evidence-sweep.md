# AgentForge Final Evidence Sweep

**Date:** 2026-05-14  
**Scope:** final authenticated deployed evidence capture against the final submission plan.

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

Authenticated deployed evidence capture is complete.

| Evidence | Artifact |
| --- | --- |
| Initial authenticated status | `deploy/captures/operator-status-20260514-173346.json` |
| Final coverage-gap campaign | `deploy/captures/campaign-run-6a5297ca98ab-20260514-173759.json` |
| Full finding curation | `deploy/captures/findings-after-full-curation-20260514-174626.json` |
| First regression replay | `deploy/captures/regression-replay-regval-4b592e1ea1b6-20260514-175008.json` |
| Attachment adapter rerun | `deploy/captures/attachment-campaign-run-94464fc484ac-20260514-180337.json` |
| Third report-lane approval | `deploy/captures/approved-attachment-finding-find-63eb1564ab3c-20260514-180728.json` |
| Final regression replay | `deploy/captures/regression-replay-regval-c5831da1bcba-20260514-180755.json` |
| Final finding status | `deploy/captures/findings-after-third-report-lane-20260514-180841.json` |
| Final operator status | `deploy/captures/operator-status-final-20260514-180849.json` |

## Final Evidence Summary

| Metric | Final value |
| --- | --- |
| Final deployed commit | `b597142` |
| Deployed evidence environment | `deployed` |
| Categories tested | 5 |
| Catalog cases tested | 10 / 10 |
| Final finding status counts | `approved=1`, `regression_queued=2`, `needs_more_evidence=5`, `rejected=3` |
| Final report lanes | `find-4e41695d42ec`, `find-2f92b8b731b0`, `find-63eb1564ab3c` |
| Latest validation ID | `regval-c5831da1bcba` |
| Latest validation summary | `resolved=1`, `reappeared=2`, `needs_review=0`, `missing_case=0` |

## Acceptance Criteria For Final Capture

- `GET /operator/status` includes `coverage`, `next_campaign_recommendation`, `observability`, and `regressions`. Met in `operator-status-final-20260514-180849.json`.
- The campaign response has `evidence_environment=deployed`. Met in `run-6a5297ca98ab` and `run-94464fc484ac`.
- The campaign response records `orchestrator_recommendations`. Met in final campaign captures.
- At least three attack categories are represented across final deployed evidence. Met: 5 categories.
- Reports are regenerated from curated deployed findings after approval/replay decisions. Met for the three final report lanes.
- Confirmed findings have regression cases and, where possible, replay validation artifacts. Met in `regval-c5831da1bcba`.
- Judge-flagged findings remain clearly labeled as unconfirmed or needs-more-evidence. Met in final curation counts.
