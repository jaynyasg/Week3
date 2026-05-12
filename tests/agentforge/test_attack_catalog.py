from __future__ import annotations

from agentforge.attacks.catalog import AttackCatalog


def test_attack_catalog_loads_seed_cases():
    cases = AttackCatalog().load_cases()

    ids = {case.id for case in cases}
    assert "rbac-nurse-labs-001" in ids
    assert "attachment-injection-001" in ids
    assert all(case.expected_safe_behavior for case in cases)
    assert all(case.framework_refs for case in cases)


def test_attack_catalog_filters_by_category_and_limit():
    cases = AttackCatalog().select(category="rbac_phi_exfiltration", max_cases=1)

    assert len(cases) == 1
    assert cases[0].category == "rbac_phi_exfiltration"
