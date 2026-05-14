from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from agentforge.models.finding import Finding, FindingStatus
from agentforge.models.run_artifact import RunArtifact


def _json_default(value: Any) -> str:
    return str(value)


class ArtifactStore:
    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.results_dir = self.root / "results"
        self.findings_dir = self.results_dir / "findings"
        self.reports_dir = self.root / "reports"
        self.regression_dir = self.root / "regression"
        self.regression_validations_dir = self.regression_dir / "validations"
        self.goldens_dir = self.root / "goldens"
        self.ensure()

    def ensure(self) -> None:
        for directory in [
            self.root,
            self.results_dir,
            self.findings_dir,
            self.reports_dir,
            self.regression_dir,
            self.regression_validations_dir,
            self.goldens_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def _write_json(self, path: Path, data: dict[str, Any]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, indent=2, sort_keys=True, default=_json_default) + "\n",
            encoding="utf-8",
        )
        return path

    def append_jsonl(self, path: Path, data: dict[str, Any]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(data, sort_keys=True, default=_json_default) + "\n")
        return path

    def save_run(self, run: RunArtifact) -> Path:
        data = run.model_dump(mode="json")
        path = self.results_dir / f"{run.run_id}.json"
        self._write_json(path, data)
        self.append_jsonl(self.results_dir / "runs.jsonl", data)
        for finding in run.findings:
            self.save_finding(finding)
        return path

    def get_run(self, run_id: str) -> RunArtifact:
        path = self.results_dir / f"{run_id}.json"
        if not path.exists():
            raise FileNotFoundError(run_id)
        return RunArtifact.model_validate_json(path.read_text(encoding="utf-8"))

    def list_runs(self, evidence_environment: str | None = None) -> list[RunArtifact]:
        runs: list[RunArtifact] = []
        for path in sorted(self.results_dir.glob("run-*.json")):
            run = RunArtifact.model_validate_json(path.read_text(encoding="utf-8"))
            if (
                evidence_environment is None
                or run.evidence_environment == evidence_environment
            ):
                runs.append(run)
        return sorted(runs, key=lambda run: run.completed_at or run.created_at)

    def save_finding(self, finding: Finding) -> Path:
        return self._write_json(
            self.findings_dir / f"{finding.finding_id}.json",
            finding.model_dump(mode="json"),
        )

    def update_run_finding(self, finding: Finding) -> Path | None:
        path = self.results_dir / f"{finding.run_id}.json"
        if not path.exists():
            return None
        run = RunArtifact.model_validate_json(path.read_text(encoding="utf-8"))
        for index, existing in enumerate(run.findings):
            if existing.finding_id == finding.finding_id:
                run.findings[index] = finding
                break
        else:
            run.findings.append(finding)
        return self._write_json(path, run.model_dump(mode="json"))

    def get_finding(self, finding_id: str) -> Finding:
        path = self.findings_dir / f"{finding_id}.json"
        if not path.exists():
            raise FileNotFoundError(finding_id)
        return Finding.model_validate_json(path.read_text(encoding="utf-8"))

    def list_findings(self, status: FindingStatus | None = None) -> list[Finding]:
        findings: list[Finding] = []
        for path in sorted(self.findings_dir.glob("*.json")):
            finding = Finding.model_validate_json(path.read_text(encoding="utf-8"))
            if status is None or finding.status == status:
                findings.append(finding)
        return findings

    def save_report(self, finding_id: str, content: str) -> Path:
        path = self.reports_dir / f"{finding_id}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        return path

    def save_regression_case(self, finding_id: str, data: dict[str, Any]) -> Path:
        return self._write_json(self.regression_dir / f"{finding_id}.json", data)

    def list_regression_cases(
        self,
        finding_ids: Iterable[str] | None = None,
    ) -> list[dict[str, Any]]:
        requested = set(finding_ids or [])
        cases: list[dict[str, Any]] = []
        for path in sorted(self.regression_dir.glob("*.json")):
            if requested and path.stem not in requested:
                continue
            cases.append(json.loads(path.read_text(encoding="utf-8")))
        return cases

    def save_regression_validation(self, data: dict[str, Any]) -> Path:
        validation_id = data.get("validation_id")
        if not validation_id:
            raise ValueError("validation_id is required")
        return self._write_json(
            self.regression_validations_dir / f"{validation_id}.json",
            data,
        )

    def list_regression_validations(self) -> list[dict[str, Any]]:
        validations: list[dict[str, Any]] = []
        for path in sorted(self.regression_validations_dir.glob("*.json")):
            validations.append(json.loads(path.read_text(encoding="utf-8")))
        return validations

    def delete_regression_case(self, finding_id: str) -> bool:
        path = self.regression_dir / f"{finding_id}.json"
        if not path.exists():
            return False
        path.unlink()
        return True

    def safe_artifact_path(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        root = self.root.resolve()
        if root not in candidate.parents and candidate != root:
            raise ValueError("artifact path escapes artifact root")
        return candidate
