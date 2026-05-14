# AgentForge AI Cost Analysis

**Status:** Final-submission baseline. Prices rechecked 2026-05-14 against official vendor pages; recheck again only if the submission date moves or account plans change.

## Cost Principles

- Deployed campaigns use hosted models. Local-only models may help development but do not produce final evidence.
- Red-team generation should use low-cost models.
- Deterministic judging handles clear failures before any LLM judge call.
- Premium models are escalation tools, not the default path.
- Every deployed run should record model/provider, estimated input/output tokens, refusal count, retry count, and cost bucket.

## Model Roles

| Role | Default provider/model | Cost control |
| --- | --- | --- |
| Red Team Agent | Groq `llama-3.1-8b-instant` | Cap mutations per case and track refusal rate |
| Judge Agent | Deterministic rules first; OpenAI `gpt-5-nano` for gray areas | Use LLM judge only when deterministic result is inconclusive |
| Documentation Agent | Template-first; OpenAI `gpt-5-nano` when drafting help is useful | Generate only for confirmed/partial findings |
| Orchestrator Agent | Deterministic planning | No LLM call required for simple coverage/budget decisions |
| Observability | Langfuse traces and scores | Metadata-only by default; no raw PHI-like transcript logging |

## Pricing Sources To Recheck

- Groq `llama-3.1-8b-instant`: `https://console.groq.com/docs/model/llama-3.1-8b-instant`
- OpenAI `gpt-5-nano`: `https://platform.openai.com/docs/models/gpt-5-nano/`
- OpenAI pricing: `https://platform.openai.com/docs/pricing/`
- Gemini pricing fallback reference: `https://ai.google.dev/gemini-api/docs/pricing`
- Claude pricing: `https://platform.claude.com/docs/en/about-claude/pricing`
- Render pricing: `https://render.com/pricing`
- Langfuse docs: `https://langfuse.com/docs/`

## Current Token Rates Used For Planning

| Provider/model | Input | Output | Notes |
| --- | ---: | ---: | --- |
| Groq `llama-3.1-8b-instant` | $0.05 / 1M tokens | $0.08 / 1M tokens | Red Team Agent default |
| OpenAI `gpt-5-nano` | $0.05 / 1M tokens | $0.40 / 1M tokens | Judge fallback and documentation drafting |

## Infrastructure Assumptions

These estimates are monthly incremental AgentForge platform costs, not the already-deployed Week 2 target's hosting cost. Render pricing checked on 2026-05-14 lists web services from Free, Starter at $7/month, Standard at $25/month, and persistent disks at $0.25/GB/month. Render bandwidth is included up to the plan allowance and then metered; the estimates below assume metadata-heavy artifacts and no unusual media or transcript downloads.

Langfuse pricing checked on 2026-05-14 lists a free Hobby path and Core pricing with a $29/month base plus graduated usage; the MVP uses metadata-only traces, so classroom/demo use can stay on free or credit-covered usage unless trace volume grows materially. If Langfuse Core is required, add $29/month plus the published usage tier to the infrastructure estimate.

## Per-Run Cost Model

Use this formula per campaign run:

```text
run_cost =
  red_team_input_tokens * red_team_input_rate
+ red_team_output_tokens * red_team_output_rate
+ judge_input_tokens * judge_input_rate
+ judge_output_tokens * judge_output_rate
+ documentation_input_tokens * documentation_input_rate
+ documentation_output_tokens * documentation_output_rate
+ retry_cost
+ deployed_infrastructure_allocation
```

## Scenario Assumptions

These are planning assumptions, not invoices.

| Quantity | Conservative MVP assumption |
| --- | ---: |
| Average red-team prompt input | 1,000 tokens |
| Average red-team output | 500 tokens |
| Average deterministic judge cost | $0 |
| LLM judge rate | 20 percent of runs |
| Average LLM judge input | 1,500 tokens |
| Average LLM judge output | 300 tokens |
| Documentation calls | 10 percent of runs |
| Average documentation input | 2,000 tokens |
| Average documentation output | 800 tokens |
| Retry/refusal overhead | 10 percent planning buffer |

## Required Projection Table

These estimates cover LLM usage only. Infrastructure is tracked separately because Render, persistent disk, logs, and target hosting may be covered by existing deployment settings or plan-specific pricing.

| Runs | Architecture note | LLM estimate | Infrastructure estimate | Notes |
| ---: | --- | ---: | ---: | --- |
| 100 | Single deployed AgentForge service, persistent artifact storage | ~$0.02 | $0.25-$7.25/mo | MVP demo scale; Free compute plus 1 GB disk, or Starter to avoid sleep. |
| 1,000 | Same service, stricter budget caps and batch scheduling | ~$0.19 | ~$7.25/mo | Starter web service plus 1 GB disk. |
| 10,000 | Queueing, provider rate-limit handling, artifact lifecycle policy | ~$1.88 | ~$26.25/mo | Standard web service plus 5 GB disk. |
| 100,000 | Batch jobs, reserved capacity or negotiated pricing, stronger storage lifecycle | ~$18.81 | ~$56.25+/mo | Two Standard-scale services/workers plus 25 GB disk; add bandwidth/Langfuse Core if usage exceeds included tiers. |

Calculation basis per run:

```text
red_team = (1,000 * 0.05 + 500 * 0.08) / 1,000,000 = $0.000090
judge = 20% * ((1,500 * 0.05 + 300 * 0.40) / 1,000,000) = $0.000039
docs = 10% * ((2,000 * 0.05 + 800 * 0.40) / 1,000,000) = $0.000042
buffered_run_cost = (red_team + judge + docs) * 1.10 = $0.0001881
```

## Actual Dev Spend

The deployed AgentForge platform (`https://agentforge-security.onrender.com`) ran two bounded campaigns against the deployed Clinical Co-Pilot target (`https://clinical-copilot-4kwb.onrender.com/agent/chat`) on 2026-05-12. Both runs executed in `provider_mode=deterministic`, which routes the Red Team Agent through seed-only generation and the Judge Agent through deterministic rules first, with `gpt-5-nano` reserved as the LLM-judge fallback. Neither run needed the LLM-judge fallback, so `estimated_cost_usd` on each run artifact recorded `$0.00`. Langfuse traces (`run-b5a238a8b374`, `run-3fcb420ddc96`) confirm zero hosted-model calls were issued during these campaigns. Render compute, persistent disk, and Langfuse-hosted observability remain the only paid line items at this stage and are covered by existing Week 2 / Week 3 deployment plans; they are tracked under *Infrastructure estimate* rather than per-run LLM spend. This zero-LLM-cost baseline matches the per-run formula above when no red-team mutation or LLM-judge fallback is triggered, and it sets a floor: the moment `AGENTFORGE_PROVIDER_MODE=live` is enabled for a campaign, Groq red-team mutation cost (~$0.00009/run) and any LLM-judge gray-area calls (~$0.00004/run × fallback rate) will begin to register against the projection table.

| Date | Run ID | Provider | Cases | Findings | Estimated cost | Notes |
| --- | --- | --- | ---: | ---: | ---: | --- |
| 2026-05-12 | `run-b5a238a8b374` | deterministic + `gpt-5-nano` (fallback unused) | 1 | 0 (SAFE — RBAC defense held) | $0.00 | First deployed-to-deployed run; nurse-labs RBAC seed attack refused at the tool layer (`error_code: rbac_refusal`). |
| 2026-05-12 | `run-3fcb420ddc96` | deterministic + `gpt-5-nano` (fallback unused) | 4 | 4 (1 approved, 1 auto-approved, 2 needs\_more\_evidence) | $0.00 | Covered attachment injection, prompt-state injection, tool/patient-scope tampering, and cost/DoS. Human review caught two deterministic-judge false positives, demonstrating the judge / approval boundary. |
| **Total** |  |  | **5** | **4** | **$0.00** | Five categories exercised across two deployed campaigns. |

## Budget Halt Policy

The Orchestrator should halt before target execution when projected campaign spend exceeds the configured cap. The halt artifact should record:

- Campaign ID.
- Budget cap.
- Projected cost.
- Model/provider.
- Attack category.
- Number of cases skipped.
- Whether any target calls were made.

## Cost Risks

| Risk | Mitigation |
| --- | --- |
| Red-team model refusal causes retry loops | Track refusals and cap retries |
| Tool/cost DoS attack burns target calls | Budget before target execution |
| LLM judge overuse | Deterministic checks first |
| High-severity or ambiguous finding is wrong | Require human approval before final report or regression promotion |
| Langfuse receives sensitive transcript content | Send metadata-only traces by default; store raw evidence as controlled artifacts |
| Provider pricing changes | Store pricing source and retrieval date in final analysis |
| Local runs confused with deployed evidence | Label local runs as development-only and exclude from final spend evidence |
