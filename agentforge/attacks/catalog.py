from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yaml

from agentforge.models.campaign import AttackCase


class AttackCatalog:
    def __init__(self, case_dir: Path | str = "evals/cases") -> None:
        self.case_dir = Path(case_dir)

    def load_cases(self) -> list[AttackCase]:
        cases: list[AttackCase] = []
        for path in sorted(self.case_dir.glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            if "cases" in data:
                cases.extend(AttackCase.model_validate(item) for item in data["cases"])
            else:
                cases.append(AttackCase.model_validate(data))
        return cases

    def select(
        self,
        *,
        category: str | None = None,
        case_ids: Iterable[str] | None = None,
        max_cases: int = 5,
    ) -> list[AttackCase]:
        case_id_set = set(case_ids or [])
        selected: list[AttackCase] = []
        for case in self.load_cases():
            if category and case.category != category:
                continue
            if case_id_set and case.id not in case_id_set:
                continue
            selected.append(case)
            if len(selected) >= max_cases:
                break
        return selected
