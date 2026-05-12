# AgentForge AI Cost Analysis

**Status:** Planning baseline for Week 3. Prices checked 2026-05-12; recheck vendor prices before final submission.

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
| 100 | Single deployed AgentForge service, persistent artifact storage | ~$0.02 | TBD | MVP demo scale |
| 1,000 | Same service, stricter budget caps and batch scheduling | ~$0.19 | TBD | Week-scale campaign |
| 10,000 | Queueing, provider rate-limit handling, artifact lifecycle policy | ~$1.88 | TBD | Larger regression suite |
| 100,000 | Batch jobs, reserved capacity or negotiated pricing, stronger storage lifecycle | ~$18.81 | TBD | Production-scale only |

Calculation basis per run:

```text
red_team = (1,000 * 0.05 + 500 * 0.08) / 1,000,000 = $0.000090
judge = 20% * ((1,500 * 0.05 + 300 * 0.40) / 1,000,000) = $0.000039
docs = 10% * ((2,000 * 0.05 + 800 * 0.40) / 1,000,000) = $0.000042
buffered_run_cost = (red_team + judge + docs) * 1.10 = $0.0001881
```

## Actual Spend Log

| Date | Provider | Purpose | Cost | Notes |
| --- | --- | --- | ---: | --- |
| TBD | TBD | First deployed campaign | TBD | Record after deployed evidence run |

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
