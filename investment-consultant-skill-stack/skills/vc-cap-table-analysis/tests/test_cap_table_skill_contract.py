from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
REFS = ROOT / "references"


def read(path):
    return path.read_text(encoding="utf-8")


def test_frontmatter_has_discoverable_trigger_only_description():
    content = read(SKILL)
    assert content.startswith("---\n")
    assert "name: vc-cap-table-analysis" in content
    description = next(line for line in content.splitlines() if line.startswith("description:"))
    assert "Use when" in description


def test_skill_explicitly_separates_economic_model_from_legal_interpretation():
    content = read(SKILL).lower()
    assert "economic model" in content
    assert "legal interpretation" in content
    assert "legal" in content


def test_skill_requires_reconciliation_and_explicit_pre_post_money_and_safe_type():
    content = (read(SKILL) + read(REFS / "round-mechanics.md") + read(REFS / "convertibles.md")).lower()
    assert "reconcile" in content
    assert "100%" in content
    assert "pre-money" in content
    assert "post-money" in content
    assert "safe type" in content or "safe_type" in content


def test_skill_references_all_methodology_files_and_tested_engine():
    content = read(SKILL)
    for rel in [
        "references/round-mechanics.md",
        "references/convertibles.md",
        "references/anti-dilution-and-waterfalls.md",
        "scripts/cap_table.py",
    ]:
        assert rel in content
        assert (ROOT / rel).exists()


def test_integration_contract_fields_are_documented():
    content = (read(SKILL) + read(REFS / "round-mechanics.md")).lower()
    for field in [
        "pre_money_valuation",
        "new_primary_investment",
        "post_money_valuation",
        "pre_round_fd_ownership",
        "post_round_fd_ownership",
        "founder_dilution_pct_points",
        "new_investor_ownership",
        "validation_status",
    ]:
        assert field in content
