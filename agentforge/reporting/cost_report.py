from __future__ import annotations

from agentforge.attacks.budget import (
    estimate_documentation_cost,
    estimate_llm_judge_cost,
)

REDTEAM_PER_RUN = 0.000090
JUDGE_RATE = 0.20
DOCS_RATE = 0.10
BUFFER_RATE = 1.10


def estimated_llm_cost_per_run() -> float:
    return (
        REDTEAM_PER_RUN
        + JUDGE_RATE * estimate_llm_judge_cost()
        + DOCS_RATE * estimate_documentation_cost()
    ) * BUFFER_RATE


def build_cost_projection(run_counts: list[int] | None = None) -> list[dict[str, str]]:
    counts = run_counts or [100, 1000, 10000, 100000]
    per_run = estimated_llm_cost_per_run()
    return [
        {
            "runs": str(count),
            "llm_estimate_usd": f"{count * per_run:.2f}",
            "basis": "Groq red team, deterministic-first judge, gpt-5-nano fallback/docs",
        }
        for count in counts
    ]
