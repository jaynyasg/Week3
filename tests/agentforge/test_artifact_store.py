from __future__ import annotations

import pytest

from agentforge.models.finding import Finding, FindingStatus, Verdict
from agentforge.models.run_artifact import RunArtifact
from agentforge.storage.artifact_store import ArtifactStore


def test_artifact_store_persists_runs_and_findings(tmp_path):
    store = ArtifactStore(tmp_path / "evals")
    finding = Finding(
        run_id="run-1",
        case_id="case-1",
        title="Test finding",
        category="rbac",
        verdict=Verdict.VULNERABLE,
        severity="high",
        rationale="unsafe",
    ).with_default_status()
    run = RunArtifact(campaign_id="camp-1", target_alias="clinical", findings=[finding])

    store.save_run(run)

    assert store.get_run(run.run_id).run_id == run.run_id
    assert store.get_finding(finding.finding_id).status.value == "needs_approval"
    assert len(store.list_findings()) == 1


def test_artifact_store_updates_embedded_run_finding(tmp_path):
    store = ArtifactStore(tmp_path / "evals")
    finding = Finding(
        run_id="run-1",
        case_id="case-1",
        title="Test finding",
        category="rbac",
        verdict=Verdict.VULNERABLE,
        severity="high",
        rationale="unsafe",
    ).with_default_status()
    run = RunArtifact(
        run_id="run-1",
        campaign_id="camp-1",
        target_alias="clinical",
        findings=[finding],
    )
    store.save_run(run)

    finding.status = FindingStatus.REGRESSION_QUEUED
    store.update_run_finding(finding)

    updated = store.get_run("run-1")
    assert updated.findings[0].status == FindingStatus.REGRESSION_QUEUED


def test_artifact_store_can_delete_stale_regression_case(tmp_path):
    store = ArtifactStore(tmp_path / "evals")
    store.save_regression_case("find-1", {"finding_id": "find-1"})

    assert store.delete_regression_case("find-1") is True
    assert store.delete_regression_case("find-1") is False
    assert not (store.regression_dir / "find-1.json").exists()


def test_artifact_store_blocks_path_escape(tmp_path):
    store = ArtifactStore(tmp_path / "evals")

    with pytest.raises(ValueError, match="escapes"):
        store.safe_artifact_path("../secret.txt")
