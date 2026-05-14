from __future__ import annotations

import pytest

from agentforge.models.finding import Finding, FindingStatus, Verdict
from agentforge.models.run_artifact import RunArtifact, TargetExchange
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


def test_artifact_store_lists_regression_cases_and_saves_validations(tmp_path):
    store = ArtifactStore(tmp_path / "evals")
    store.save_regression_case(
        "find-1",
        {
            "finding_id": "find-1",
            "case_id": "rbac-nurse-labs-001",
            "category": "rbac_phi_exfiltration",
            "verdict": "vulnerable",
        },
    )
    store.save_regression_case(
        "find-2",
        {
            "finding_id": "find-2",
            "case_id": "attachment-injection-001",
            "category": "attachment_prompt_injection",
            "verdict": "vulnerable",
        },
    )

    cases = store.list_regression_cases(["find-2"])
    path = store.save_regression_validation(
        {
            "validation_id": "regval-test",
            "summary": {"total": 1, "resolved": 1},
            "results": [],
        }
    )

    assert [case["finding_id"] for case in cases] == ["find-2"]
    assert path == store.regression_validations_dir / "regval-test.json"
    assert path.exists()
    assert store.list_regression_validations()[0]["validation_id"] == "regval-test"


def test_artifact_store_lists_runs_by_environment(tmp_path):
    store = ArtifactStore(tmp_path / "evals")
    deployed = RunArtifact(
        campaign_id="camp-deployed",
        target_alias="clinical-copilot",
        evidence_environment="deployed",
        exchanges=[
            TargetExchange(
                case_id="rbac-nurse-labs-001",
                target_alias="clinical-copilot",
                target_url="https://target.example",
            )
        ],
    ).finish()
    local = RunArtifact(
        campaign_id="camp-local",
        target_alias="clinical-copilot",
        evidence_environment="development",
    ).finish()
    store.save_run(local)
    store.save_run(deployed)

    runs = store.list_runs(evidence_environment="deployed")

    assert [run.run_id for run in runs] == [deployed.run_id]


def test_artifact_store_blocks_path_escape(tmp_path):
    store = ArtifactStore(tmp_path / "evals")

    with pytest.raises(ValueError, match="escapes"):
        store.safe_artifact_path("../secret.txt")
