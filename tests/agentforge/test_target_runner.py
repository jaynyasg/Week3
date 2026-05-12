from __future__ import annotations

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
