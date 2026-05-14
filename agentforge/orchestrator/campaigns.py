from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from agentforge.attacks.budget import BudgetLedger, estimate_redteam_cost
from agentforge.attacks.catalog import AttackCatalog
from agentforge.config import AgentForgeSettings
from agentforge.judge.deterministic import DeterministicJudge
from agentforge.judge.llm_judge import LlmJudge
from agentforge.models.campaign import CampaignPlan, CampaignStartRequest
from agentforge.models.finding import Finding, Verdict
from agentforge.models.run_artifact import RunArtifact
from agentforge.observability.events import build_run_event, log_agentforge_event
from agentforge.observability.langfuse_client import LangfuseRecorder
from agentforge.orchestrator.coverage import build_coverage_summary
from agentforge.orchestrator.priority import recommend_next_cases
from agentforge.redteam.providers import create_redteam_provider
from agentforge.reporting.vulnerability_report import (
    build_regression_case,
    render_vulnerability_report,
)
from agentforge.storage.artifact_store import ArtifactStore
from agentforge.targets.allowlist import TargetAllowlist
from agentforge.targets.clinical_copilot import ClinicalCoPilotClient

_LOG = logging.getLogger(__name__)


class CampaignExecutor:
    def __init__(
        self,
        *,
        settings: AgentForgeSettings,
        catalog: AttackCatalog,
        store: ArtifactStore,
        allowlist: TargetAllowlist,
        target_client: ClinicalCoPilotClient | None = None,
        langfuse: LangfuseRecorder | None = None,
    ) -> None:
        self.settings = settings
        self.catalog = catalog
        self.store = store
        self.allowlist = allowlist
        self.target_client = target_client or ClinicalCoPilotClient(settings, allowlist)
        self.redteam = create_redteam_provider(settings)
        self.deterministic_judge = DeterministicJudge()
        self.llm_judge = LlmJudge(settings)
        self.langfuse = langfuse or LangfuseRecorder(settings)

    def build_plan(self, request: CampaignStartRequest) -> CampaignPlan:
        self.allowlist.require_any()
        target_alias = request.target_alias or self.settings.default_target_alias
        if target_alias is None:
            raise ValueError("target alias is required")
        self.allowlist.resolve(target_alias)
        max_cases = (
            request.max_cases
            if request.max_cases is not None
            else self.settings.max_cases_per_campaign
        )
        budget_usd = (
            request.budget_usd
            if request.budget_usd is not None
            else self.settings.budget_usd
        )
        selection_reasons = []
        if request.category or request.case_ids:
            cases = self.catalog.select(
                category=request.category,
                case_ids=request.case_ids,
                max_cases=max_cases,
            )
            selection_reasons = [
                {
                    "case_id": case.id,
                    "category": case.category,
                    "title": case.title,
                    "reason": "operator_requested",
                    "weak_surface_score": None,
                    "tested_case_count": None,
                    "available_case_count": None,
                }
                for case in cases
            ]
        else:
            all_cases = self.catalog.load_cases()
            coverage_summary = build_coverage_summary(
                all_cases,
                self.store.list_runs(
                    evidence_environment=self.settings.evidence_environment
                ),
                self.store.list_findings(),
                evidence_environment=self.settings.evidence_environment,
            )
            selection_reasons = recommend_next_cases(
                all_cases,
                coverage_summary,
                max_cases=max_cases,
            )
            selected_ids = [item["case_id"] for item in selection_reasons]
            selected_id_set = set(selected_ids)
            selected_by_id = {case.id: case for case in all_cases if case.id in selected_id_set}
            cases = [selected_by_id[case_id] for case_id in selected_ids if case_id in selected_by_id]
        return CampaignPlan(
            target_alias=target_alias,
            category=request.category,
            case_ids=request.case_ids,
            max_cases=max_cases,
            budget_usd=budget_usd,
            cases=cases,
            selection_reasons=selection_reasons,
        )

    def run(self, request: CampaignStartRequest) -> RunArtifact:
        plan = self.build_plan(request)
        ledger = BudgetLedger(plan.budget_usd)
        run = RunArtifact(
            campaign_id=plan.campaign_id,
            target_alias=plan.target_alias,
            evidence_environment=self.settings.evidence_environment,
            budget_usd=plan.budget_usd,
            model_provider=getattr(self.redteam, "provider", "deterministic"),
            model_name=getattr(self.redteam, "model", "deterministic"),
            judge_model_provider=self.settings.judge_provider,
            judge_model_name=self.settings.judge_model,
            orchestrator_recommendations=plan.selection_reasons,
        )

        for case in plan.cases:
            projected = estimate_redteam_cost(case)
            if not ledger.can_spend(projected):
                ledger.skip()
                continue
            provider_result = self.redteam.mutate(case)
            ledger.spend(provider_result.estimated_cost_usd)
            if provider_result.refusal:
                run.refusal_count += 1
            exchange = self.target_client.run_case(
                provider_result.case,
                plan.target_alias,
            )
            run.exchanges.append(exchange)
            judge_result = self.deterministic_judge.evaluate(provider_result.case, exchange)
            if judge_result.verdict == Verdict.INCONCLUSIVE:
                judge_result = self.llm_judge.evaluate(provider_result.case, exchange)
            if judge_result.verdict != Verdict.SAFE:
                finding = Finding(
                    run_id=run.run_id,
                    case_id=provider_result.case.id,
                    title=provider_result.case.title,
                    category=provider_result.case.category,
                    framework_refs=provider_result.case.framework_refs,
                    verdict=judge_result.verdict,
                    severity=judge_result.severity,
                    confidence=judge_result.confidence,
                    judge_mode=judge_result.judge_mode,
                    rationale=judge_result.rationale,
                    evidence=judge_result.evidence
                    | {
                        "expected_safe_behavior": provider_result.case.expected_safe_behavior,
                        "target_role": provider_result.case.target_role,
                        "attack_tags": provider_result.case.tags,
                    },
                ).with_default_status()
                run.findings.append(finding)
                self.store.save_finding(finding)
                self.store.save_report(
                    finding.finding_id,
                    render_vulnerability_report(finding, run),
                )
                if not finding.requires_human_approval():
                    self.store.save_regression_case(
                        finding.finding_id,
                        build_regression_case(finding),
                    )

        if ledger.skipped_count and not run.exchanges:
            run.status = "budget_halted"
        run.estimated_cost_usd = round(ledger.spent_usd, 6)
        run.skipped_count = ledger.skipped_count
        run.finish()
        langfuse_payload = self.langfuse.record_run(run)
        run.langfuse_trace_id = str(langfuse_payload.get("trace_id", run.run_id))
        self.store.save_run(run)
        log_agentforge_event(_LOG, "campaign_completed", fields=build_run_event(run))
        return run

    def replay_regressions(
        self,
        *,
        finding_ids: list[str] | None = None,
        target_change_id: str | None = None,
    ) -> dict[str, Any]:
        self.allowlist.require_any()
        target_alias = self.settings.default_target_alias
        if target_alias is None:
            raise ValueError("target alias is required")
        self.allowlist.resolve(target_alias)

        cases_by_id = {case.id: case for case in self.catalog.load_cases()}
        regression_cases = self.store.list_regression_cases(finding_ids)
        validation = {
            "validation_id": f"regval-{uuid4().hex[:12]}",
            "target_alias": target_alias,
            "evidence_environment": self.settings.evidence_environment,
            "target_change_id": target_change_id,
            "created_at": datetime.now(UTC).isoformat(),
            "requested_finding_ids": finding_ids or [],
            "results": [],
            "summary": {
                "total": 0,
                "resolved": 0,
                "reappeared": 0,
                "needs_review": 0,
                "missing_case": 0,
            },
        }

        for regression_case in regression_cases:
            validation["summary"]["total"] += 1
            case_id = regression_case.get("case_id", "")
            finding_id = regression_case.get("finding_id", "")
            case = cases_by_id.get(case_id)
            if case is None:
                validation["summary"]["missing_case"] += 1
                validation["results"].append(
                    {
                        "finding_id": finding_id,
                        "case_id": case_id,
                        "category": regression_case.get("category"),
                        "prior_verdict": regression_case.get("verdict"),
                        "current_verdict": None,
                        "status": "missing_case",
                        "rationale": "Regression case references an attack case that is not in the current catalog.",
                    }
                )
                continue

            exchange = self.target_client.run_case(case, target_alias)
            judge_result = self.deterministic_judge.evaluate(case, exchange)
            if judge_result.verdict == Verdict.INCONCLUSIVE:
                judge_result = self.llm_judge.evaluate(case, exchange)

            if judge_result.verdict == Verdict.SAFE:
                status = "resolved"
            elif judge_result.verdict == Verdict.INCONCLUSIVE:
                status = "needs_review"
            else:
                status = "reappeared"
            validation["summary"][status] += 1
            validation["results"].append(
                {
                    "finding_id": finding_id,
                    "case_id": case_id,
                    "category": case.category,
                    "prior_verdict": regression_case.get("verdict"),
                    "current_verdict": judge_result.verdict.value,
                    "status": status,
                    "severity": judge_result.severity,
                    "confidence": judge_result.confidence,
                    "judge_mode": judge_result.judge_mode,
                    "rationale": judge_result.rationale,
                    "exchange": exchange.model_dump(mode="json"),
                    "evidence": judge_result.evidence,
                }
            )

        self.store.save_regression_validation(validation)
        log_agentforge_event(
            _LOG,
            "regression_replay_completed",
            fields={
                "validation_id": validation["validation_id"],
                "target_alias": target_alias,
                "evidence_environment": self.settings.evidence_environment,
                **validation["summary"],
            },
        )
        return validation
