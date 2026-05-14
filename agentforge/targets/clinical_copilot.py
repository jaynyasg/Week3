from __future__ import annotations

import base64
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
            "attachments": self._target_attachments(case.attachments),
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
    def _target_attachments(attachments: list[dict[str, Any]]) -> list[dict[str, str]]:
        return [
            ClinicalCoPilotClient._target_attachment(attachment)
            for attachment in attachments
        ]

    @staticmethod
    def _target_attachment(attachment: dict[str, Any]) -> dict[str, str]:
        if {
            "doc_type",
            "filename",
            "content_base64",
        }.issubset(attachment.keys()):
            return {
                "doc_type": ClinicalCoPilotClient._doc_type(attachment.get("doc_type")),
                "filename": str(attachment["filename"]),
                "content_base64": str(attachment["content_base64"]).strip(),
            }

        filename = str(
            attachment.get("filename")
            or attachment.get("name")
            or "agentforge-attachment.pdf"
        )
        doc_type = ClinicalCoPilotClient._doc_type(attachment.get("doc_type"))
        text = str(attachment.get("text") or "")
        content_base64 = str(attachment.get("content_base64") or "").strip()
        if not content_base64:
            pdf_bytes = ClinicalCoPilotClient._text_pdf_bytes(
                text or f"Attachment: {filename}"
            )
            content_base64 = base64.b64encode(pdf_bytes).decode("ascii")

        return {
            "doc_type": doc_type,
            "filename": ClinicalCoPilotClient._pdf_filename(filename),
            "content_base64": content_base64,
        }

    @staticmethod
    def _doc_type(value: Any) -> str:
        return str(value) if value in {"lab_pdf", "intake_form"} else "intake_form"

    @staticmethod
    def _pdf_filename(filename: str) -> str:
        if filename.lower().endswith(".pdf"):
            return filename
        stem = filename.rsplit(".", 1)[0] if "." in filename else filename
        return f"{stem}.pdf"

    @staticmethod
    def _text_pdf_bytes(text: str) -> bytes:
        def escape_pdf_text(value: str) -> str:
            return (
                value.replace("\\", "\\\\")
                .replace("(", "\\(")
                .replace(")", "\\)")
            )

        words = text.split()
        lines: list[str] = []
        current: list[str] = []
        for word in words:
            candidate = " ".join([*current, word])
            if len(candidate) > 84 and current:
                lines.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            lines.append(" ".join(current))
        if not lines:
            lines = ["AgentForge attachment"]

        commands = ["BT", "/F1 11 Tf", "72 720 Td"]
        for line in lines[:40]:
            commands.append(f"({escape_pdf_text(line)}) Tj")
            commands.append("0 -16 Td")
        commands.append("ET")
        stream = "\n".join(commands).encode("latin-1", errors="replace")

        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            (
                b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
            ),
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream",
        ]

        pdf = b"%PDF-1.4\n"
        offsets: list[int] = []
        for index, obj in enumerate(objects, start=1):
            offsets.append(len(pdf))
            pdf += f"{index} 0 obj\n".encode("ascii") + obj + b"\nendobj\n"

        xref_offset = len(pdf)
        pdf += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
        pdf += b"0000000000 65535 f \n"
        for offset in offsets:
            pdf += f"{offset:010d} 00000 n \n".encode("ascii")
        pdf += (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
        return pdf

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
