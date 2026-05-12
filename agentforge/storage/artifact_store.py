from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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
        self.goldens_dir = self.root / "goldens"
        self.ensure()

    def ensure(self) -> None:
        for directory in [
            self.root,
            self.results_dir,
            self.findings_dir,
            self.reports_dir,
            self.regression_dir,
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

    def save_finding(self, finding: Finding) -> Path:
        return self._write_json(
            self.findings_dir / f"{finding.finding_id}.json",
            finding.model_dump(mode="json"),
        )

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
        path.write_text(content, encoding="utf-8")
        return path

    def save_regression_case(self, finding_id: str, data: dict[str, Any]) -> Path:
        return self._write_json(self.regression_dir / f"{finding_id}.json", data)

    def safe_artifact_path(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        root = self.root.resolve()
        if root not in candidate.parents and candidate != root:
            raise ValueError("artifact path escapes artifact root")
        return candidate
