# MVP submission runbook (deployed AgentForge → deployed target)

Canonical evidence path: **deployed AgentForge** calls **deployed Week 2 Clinical Co-Pilot** only. Repo root: `C:\Users\jayny\OneDrive\Documents\GitLab\Week3`.

This runbook maps your submission checklist to plan flows **F1–F6** from `docs/plans/2026-05-11-001-feat-agentforge-security-platform-plan.md` and the origin brainstorm.

---

## Stage A — Deploy validation (checklist item 1)

1. In [Render](https://render.com), open blueprint `agentforge-security-platform` / service `agentforge-security`.
2. Confirm the active deploy matches the Git revision you intend (GitLab or GitHub branch you ship from).
3. After deploy, run automated smoke (or use the script below):

```powershell
.\deploy\scripts\Deploy-Smoke.ps1 -BaseUrl "https://<your-agentforge-host>.onrender.com"
```

4. Manually confirm: **Events** tab shows no crash loop; **Shell** (optional) `ls /app/evals/cases` shows YAML (image-baked cases).

**F2 (target readiness):** `/ready` must show `target_configured=true` once `AGENTFORGE_TARGET_URL` is set.

---

## Stage B — Environment variables (checklist item 2)

Set in Render **Environment** (see also `deploy/docs/deployment.md` → *Render dashboard: secrets to set*):

| Required for operator API | Required for live LLM path | Optional telemetry |
| --- | --- | --- |
| `AGENTFORGE_OPERATOR_TOKEN` | `GROQ_API_KEY` (if `AGENTFORGE_PROVIDER_MODE=live`) | `LANGFUSE_ENABLED=1` |
| `AGENTFORGE_TARGET_URL` | `OPENAI_API_KEY` (if `live`) | `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL` (or `LANGFUSE_HOST`) |

Keep `AGENTFORGE_EVIDENCE_ENVIRONMENT=deployed`. For deterministic MVP spend, leave `AGENTFORGE_PROVIDER_MODE=deterministic` until you intentionally enable live mutation/judge.

**Disk:** `AGENTFORGE_ARTIFACT_DIR` must match `render.yaml` disk mount (`/data/agentforge`) so `/app/evals/cases` in the image is not hidden.

---

## Stage C — Smoke test deployed AgentForge (checklist item 3)

Minimum bar (also in `deploy/docs/smoke-checklist.md`):

- [ ] `GET /health` → `{"status":"ok"}`
- [ ] `GET /ready` → `operator_auth_configured=true`, `target_configured=true`, `evidence_environment=deployed`
- [ ] `GET /operator/status` without `Authorization` → **401**
- [ ] `GET /operator/status` with `Authorization: Bearer <token>` → **200**
- [ ] `POST /operator/campaigns` with one case id and small `budget_usd` → response includes **non-empty** `exchanges` (if exchanges are empty, fix disk mount / case paths first)

`Deploy-Smoke.ps1` covers the first four; pass `-OperatorToken` (or set `$env:AGENTFORGE_OPERATOR_TOKEN`) for campaign.

---

## Stage D — Live campaign, approval, artifacts (checklist item 4)

Use `deploy/docs/operator-runbook.md` against your **deployed** AgentForge URL and **deployed** target URL.

1. **Start bounded campaign** (example: nurse RBAC case):

```bash
curl -X POST "https://<agentforge>/operator/campaigns" \
  -H "Authorization: Bearer <AGENTFORGE_OPERATOR_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"case_ids":["rbac-nurse-labs-001"],"max_cases":1,"budget_usd":0.10}'
```

2. **List findings needing approval:**

```bash
curl "https://<agentforge>/operator/findings?status=needs_approval" \
  -H "Authorization: Bearer <AGENTFORGE_OPERATOR_TOKEN>"
```

3. **Approve one high-severity finding** (replace `finding-id`):

```bash
curl -X POST "https://<agentforge>/operator/findings/<finding-id>/approval" \
  -H "Authorization: Bearer <AGENTFORGE_OPERATOR_TOKEN>" \
  -H "X-AgentForge-Operator: <your-name>" \
  -H "Content-Type: application/json" \
  -d '{"decision":"approved","rationale":"Reproduced on deployed target; evidence sufficient."}'
```

4. **Download evidence for submission** (paths are relative to `AGENTFORGE_ARTIFACT_DIR`, e.g. `/data/agentforge` on Render):

- Run JSON: `GET /operator/artifacts/results/<run-id>.json` (same `Authorization` header).
- Finding record: `GET /operator/artifacts/results/findings/<finding-id>.json`
- Report: `GET /operator/artifacts/reports/<finding-id>.md`
- Regression: `GET /operator/artifacts/regression/<finding-id>.json`

On Render, the same files live on the **persistent disk** under the mount (`results/`, `reports/`, `regression/`). Copy via Render **Shell** or repeated `curl` artifact calls for your submission bundle.

**F3** seed execution, **F4** exploit-to-regression, **F5** cost/budget fields on the run, **F6** demo narrative.

---

## Stage E — MVP plan flows F1–F6 (checklist item 5)

Your path typo `...\Week3\C:\...\Week3` means **this repo root** only. Track completion against the plan (same files the grader expects):

| Flow | Deliverable / proof |
| --- | --- |
| **F1** Architecture + defense | `ARCHITECTURE.md`, `deploy/docs/architecture-defense.md` |
| **F2** Target readiness | Deployed target URL configured; `/ready` green; allowlist behavior understood |
| **F3** Seed attack execution | `evals/cases/*.yaml`; deployed campaign with exchanges |
| **F4** Exploit → regression | Approved finding → `evals/regression/<id>.json` + report markdown |
| **F5** Cost-aware orchestration | Run JSON shows `budget_usd`, `estimated_cost_usd`, provider fields; `AI-COST-ANALYSIS.md` |
| **F6** Deployed demo | Screen recording or script walkthrough: AgentForge URL + target URL + one end-to-end campaign + approval |

Week 2 **demo-script MVP** (lab/intake/evidence) lives under `Week2 - Test Suite/deploy/docs/demo-script-mvp.md` — that is the **Clinical Co-Pilot** demo, not AgentForge. For Week 3 MVP, prioritize the table above plus `THREAT_MODEL.md`, `USERS.md`, and brainstorm/plan PDF alignment.

---

## Quick reference

| Doc | Purpose |
| --- | --- |
| `deploy/docs/deployment.md` | Env vars, blueprint, disable/rollback |
| `deploy/docs/smoke-checklist.md` | Post-deploy smoke list |
| `deploy/docs/operator-runbook.md` | curl recipes for campaigns and approvals |
| `deploy/scripts/Deploy-Smoke.ps1` | Automated partial smoke (PowerShell) |
