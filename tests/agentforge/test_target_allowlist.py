from __future__ import annotations

import pytest

from agentforge.targets.allowlist import TargetAllowlist


def test_allowlist_builds_target_path():
    allowlist = TargetAllowlist({"clinical": "https://target.example/base"})

    assert (
        allowlist.build_url("clinical", "/agent/chat")
        == "https://target.example/base/agent/chat"
    )


def test_allowlist_rejects_unknown_alias():
    allowlist = TargetAllowlist({"clinical": "https://target.example"})

    with pytest.raises(ValueError, match="not allowlisted"):
        allowlist.resolve("evil")


def test_allowlist_rejects_target_override_outside_origin():
    allowlist = TargetAllowlist({"clinical": "https://target.example/base"})

    with pytest.raises(ValueError, match="outside the allowlist"):
        allowlist.validate_url("clinical", "https://attacker.example/base/agent/chat")


def test_allowlist_rejects_target_override_outside_path_prefix():
    allowlist = TargetAllowlist({"clinical": "https://target.example/base"})

    with pytest.raises(ValueError, match="outside the allowlisted prefix"):
        allowlist.validate_url("clinical", "https://target.example/other/agent/chat")
