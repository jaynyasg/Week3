from __future__ import annotations

import base64
import json

import httpx

from agentforge.attacks.catalog import AttackCatalog
from agentforge.targets.allowlist import TargetAllowlist
from agentforge.targets.clinical_copilot import ClinicalCoPilotClient


def test_target_runner_posts_to_allowlisted_deployed_target(settings):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["role"] = request.headers.get("X-Agent-Demo-Role")
        seen["body"] = request.read().decode("utf-8")
        return httpx.Response(200, json={"assistant_message": "Access denied."})

    case = AttackCatalog().select(case_ids=["rbac-nurse-labs-001"], max_cases=1)[0]
    allowlist = TargetAllowlist(settings.target_urls)
    client = ClinicalCoPilotClient(
        settings,
        allowlist,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    exchange = client.run_case(case, "clinical-copilot")

    assert seen["url"] == "https://target.example/agent/chat"
    assert seen["role"] == "NURSE"
    assert exchange.response_status == 200
    assert exchange.error is None
    assert exchange.response_summary["assistant_message"] == "Access denied."
    assert exchange.response_summary["assistant_messages"] == []
    assert exchange.response_summary["user_messages"] == []


def test_target_runner_converts_text_attachments_to_target_schema(settings):
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = json.loads(request.read().decode("utf-8"))
        return httpx.Response(200, json={"assistant_message": "Reviewed."})

    case = AttackCatalog().select(case_ids=["attachment-injection-001"], max_cases=1)[0]
    allowlist = TargetAllowlist(settings.target_urls)
    client = ClinicalCoPilotClient(
        settings,
        allowlist,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    exchange = client.run_case(case, "clinical-copilot")

    attachment = seen["body"]["attachments"][0]
    assert exchange.response_status == 200
    assert attachment["doc_type"] == "intake_form"
    assert attachment["filename"] == "malicious-lab-note.pdf"
    assert set(attachment) == {"doc_type", "filename", "content_base64"}
    assert base64.b64decode(attachment["content_base64"]).startswith(b"%PDF-1.4")


def test_target_runner_preserves_structured_response_sections(settings):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "assistant_message": "I can only use the active patient.",
                "messages": [
                    {"role": "user", "content": "Use Patient__other-001."},
                    {
                        "role": "assistant",
                        "content": "I can only use the active patient.",
                    },
                ],
                "tool_result_keys": ["patient_id"],
                "tool_execution_summary": {"calls": 1},
                "evidence_citations": [{"id": "demo"}],
            },
        )

    case = AttackCatalog().select(case_ids=["cross-patient-history-001"], max_cases=1)[0]
    allowlist = TargetAllowlist(settings.target_urls)
    client = ClinicalCoPilotClient(
        settings,
        allowlist,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    exchange = client.run_case(case, "clinical-copilot")

    assert exchange.response_summary["assistant_message"] == (
        "I can only use the active patient."
    )
    assert exchange.response_summary["assistant_messages"] == [
        "I can only use the active patient."
    ]
    assert exchange.response_summary["user_messages"] == ["Use Patient__other-001."]
    assert exchange.response_summary["tool_result_keys"] == ["patient_id"]
    assert exchange.response_summary["evidence_citations_count"] == 1
