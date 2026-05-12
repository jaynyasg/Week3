from __future__ import annotations

import json
from pathlib import Path

from agentforge.attacks.catalog import AttackCatalog
from agentforge.judge.deterministic import DeterministicJudge
from agentforge.models.run_artifact import TargetExchange


def test_deterministic_judge_matches_goldens():
    cases = {case.id: case for case in AttackCatalog().load_cases()}
    goldens = json.loads(Path("evals/goldens/judge_cases.json").read_text())
    judge = DeterministicJudge()

    for golden in goldens:
        case = cases[golden["case_id"]]
        exchange = TargetExchange(
            case_id=case.id,
            target_alias="clinical",
            target_url="https://target.example/agent/chat",
            response_status=golden["response_status"],
            response_summary={"text_excerpt": golden["response_text"]},
        )
        result = judge.evaluate(case, exchange)
        assert result.verdict.value == golden["expected_verdict"]
