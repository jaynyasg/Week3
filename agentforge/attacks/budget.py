from __future__ import annotations

from dataclasses import dataclass

from agentforge.models.campaign import AttackCase


GROQ_LLAMA_31_8B_INPUT_PER_1M = 0.05
GROQ_LLAMA_31_8B_OUTPUT_PER_1M = 0.08
OPENAI_GPT_5_NANO_INPUT_PER_1M = 0.05
OPENAI_GPT_5_NANO_OUTPUT_PER_1M = 0.40


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def estimate_case_tokens(case: AttackCase) -> tuple[int, int]:
    prompt = "\n".join(
        [
            case.title,
            case.category,
            case.expected_safe_behavior,
            case.user_message,
            " ".join(case.framework_refs),
        ]
    )
    return estimate_tokens(prompt), max(128, estimate_tokens(case.user_message))


def estimate_redteam_cost(case: AttackCase) -> float:
    input_tokens, output_tokens = estimate_case_tokens(case)
    return (
        input_tokens * GROQ_LLAMA_31_8B_INPUT_PER_1M
        + output_tokens * GROQ_LLAMA_31_8B_OUTPUT_PER_1M
    ) / 1_000_000


def estimate_llm_judge_cost(input_tokens: int = 1500, output_tokens: int = 300) -> float:
    return (
        input_tokens * OPENAI_GPT_5_NANO_INPUT_PER_1M
        + output_tokens * OPENAI_GPT_5_NANO_OUTPUT_PER_1M
    ) / 1_000_000


def estimate_documentation_cost(input_tokens: int = 2000, output_tokens: int = 800) -> float:
    return (
        input_tokens * OPENAI_GPT_5_NANO_INPUT_PER_1M
        + output_tokens * OPENAI_GPT_5_NANO_OUTPUT_PER_1M
    ) / 1_000_000


@dataclass
class BudgetLedger:
    cap_usd: float
    spent_usd: float = 0.0
    skipped_count: int = 0

    def can_spend(self, projected_cost: float) -> bool:
        return self.spent_usd + projected_cost <= self.cap_usd

    def spend(self, amount: float) -> None:
        self.spent_usd += amount

    def skip(self) -> None:
        self.skipped_count += 1
