# AgentForge AI Cost Analysis

**Status:** Planning baseline for Week 3. Recheck vendor prices before final submission.

## Cost Principles

- Deployed campaigns use hosted models. Local-only models may help development but do not produce final evidence.
- Red-team generation should use low-cost models.
- Deterministic judging handles clear failures before any LLM judge call.
- Premium models are escalation tools, not the default path.
- Every deployed run should record model/provider, estimated input/output tokens, refusal count, retry count, and cost bucket.

## Model Roles

| Role | Default posture | Cost control |
| --- | --- | --- |
| Red Team Agent | Cheap hosted model for mutation | Cap mutations per case and track refusal rate |
| Judge Agent | Deterministic rules first, small LLM for gray areas | Use LLM judge only when deterministic result is inconclusive |
| Documentation Agent | Small model or template-based report drafting | Generate only for confirmed/partial findings |
| Orchestrator Agent | Mostly deterministic planning | No LLM call required for simple coverage/budget decisions |

## Pricing Sources To Recheck

- OpenAI pricing: `https://developers.openai.com/api/docs/pricing`
- Gemini pricing: `https://ai.google.dev/gemini-api/docs/pricing`
- Groq pricing: `https://groq.com/pricing`
- Claude pricing: `https://platform.claude.com/docs/en/about-claude/pricing`
- Render pricing: `https://render.com/pricing`

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
| Documentation calls | Confirmed/partial findings only |
| Retry/refusal overhead | 10 percent planning buffer |

## Required Projection Table

Fill this table with current provider rates once the first deployed provider is selected.

| Runs | Architecture note | LLM estimate | Infrastructure estimate | Notes |
| ---: | --- | ---: | ---: | --- |
| 100 | Single deployed AgentForge service, persistent artifact storage | TBD | TBD | MVP demo scale |
| 1,000 | Same service, stricter budget caps and batch scheduling | TBD | TBD | Week-scale campaign |
| 10,000 | Queueing, provider rate-limit handling, artifact lifecycle policy | TBD | TBD | Larger regression suite |
| 100,000 | Batch jobs, reserved capacity or negotiated pricing, stronger storage lifecycle | TBD | TBD | Production-scale only |

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
| Provider pricing changes | Store pricing source and retrieval date in final analysis |
| Local runs confused with deployed evidence | Label local runs as development-only and exclude from final spend evidence |
