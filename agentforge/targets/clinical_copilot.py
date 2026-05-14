from __future__ import annotations

import time
from typing import Any

import httpx
from pydantic import BaseModel, Field

from agentforge.config import AgentForgeSettings
from agentforge.models.campaign import AttackCase
from agentforge.models.run_artifact import TargetExchange
from agentforge.targets.allowlist import TargetAllowlist


class TargetResponse(BaseModel):
    status_code: int | None
    body: dict[str, Any] = Field(default_factory=dict)
    text: str = ""
    latency_ms: float | None = None
    error: str | None = None


class ClinicalCoPilotClient:
    def __init__(
        self,
        settings: AgentForgeSettings,
        allowlist: TargetAllowlist,
        *,
        client: httpx.Client | None = None,
    ) -> None:
        self.settings = settings
        self.allowlist = allowlist
        self.client = client or httpx.Client(timeout=30, follow_redirects=True)

    def _headers_for(self, case: AttackCase) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.settings.target_demo_bypass:
            headers["X-Agent-Demo-Role"] = case.target_role
        if self.settings.target_authorization:
            headers["Authorization"] = self.settings.target_authorization
        if self.settings.target_cookie:
            headers["Cookie"] = self.settings.target_cookie
        return headers

    def run_case(self, case: AttackCase, target_alias: str) -> TargetExchange:
        url = self.allowlist.build_url(target_alias, self.settings.target_chat_path)
        self.allowlist.validate_url(target_alias, url)
        payload = {
            "patient_id": case.patient_id,
            "messages": case.messages,
            "user_message": case.user_message,
            "attachments": case.attachments,
        }
        started = time.perf_counter()
        try:
            response = self.client.post(
                url,
                json=payload,
                headers=self._headers_for(case),
            )
            latency_ms = (time.perf_counter() - started) * 1000
            body = self._safe_json(response)
            text = response.text
            response_summary = {
                "text_excerpt": text[:2000],
                "json_keys": sorted(body.keys()),
            }
            response_summary.update(self._structured_summary(body))
            return TargetExchange(
                case_id=case.id,
                target_alias=target_alias,
                target_url=url,
                request_summary={
                    "patient_id": case.patient_id,
                    "role": case.target_role,
                    "message_length": len(case.user_message),
                    "attachment_count": len(case.attachments),
                },
                response_status=response.status_code,
                response_summary=response_summary,
                latency_ms=latency_ms,
            )
        except Exception as exc:
            latency_ms = (time.perf_counter() - started) * 1000
            return TargetExchange(
                case_id=case.id,
                target_alias=target_alias,
                target_url=url,
                request_summary={
                    "patient_id": case.patient_id,
                    "role": case.target_role,
                    "message_length": len(case.user_message),
                    "attachment_count": len(case.attachments),
                },
                latency_ms=latency_ms,
                error=str(exc),
            )

    @staticmethod
    def _safe_json(response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError:
            return {}
        return payload if isinstance(payload, dict) else {"value": payload}

    @staticmethod
    def _structured_summary(body: dict[str, Any]) -> dict[str, Any]:
        messages = body.get("messages")
        assistant_messages: list[str] = []
        user_messages: list[str] = []
        if isinstance(messages, list):
            for message in messages:
                if not isinstance(message, dict):
                    continue
                content = message.get("content")
                if not isinstance(content, str):
                    continue
                if message.get("role") == "assistant":
                    assistant_messages.append(content[:1000])
                elif message.get("role") == "user":
                    user_messages.append(content[:1000])

        summary: dict[str, Any] = {
            "assistant_messages": assistant_messages,
            "user_messages": user_messages,
        }

        assistant_message = body.get("assistant_message")
        if isinstance(assistant_message, str):
            summary["assistant_message"] = assistant_message[:1000]

        tool_result_keys = body.get("tool_result_keys")
        if isinstance(tool_result_keys, list):
            summary["tool_result_keys"] = [
                str(key)[:200] for key in tool_result_keys
            ]

        for key in ("tool_execution_summary", "retrieval_trace"):
            value = body.get(key)
            if value:
                summary[f"{key}_excerpt"] = str(value)[:1000]

        for key in ("extraction_summaries", "evidence_citations"):
            value = body.get(key)
            if isinstance(value, list):
                summary[f"{key}_count"] = len(value)
                if value:
                    summary[f"{key}_excerpt"] = str(value[:3])[:1000]

        return summary
