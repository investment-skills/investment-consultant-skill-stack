from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
REFS = ROOT / "references"


def text(path):
    return path.read_text(encoding="utf-8")


def test_frontmatter_and_trigger_description_are_agent_skill_compatible():
    content = text(SKILL)
    assert content.startswith("---\n")
    assert "name: startup-investment-readiness" in content
    description_line = next(line for line in content.splitlines() if line.startswith("description:"))
    assert "Use when" in description_line


def test_references_exist_and_are_linked_from_skill():
    content = text(SKILL)
    for name in ["orchestration.md", "evidence-gates.md", "output-contracts.md"]:
        path = REFS / name
        assert path.exists()
        assert f"references/{name}" in content


def test_skill_enforces_quality_gates_and_conflict_handling():
    content = (text(SKILL) + text(REFS / "evidence-gates.md")).lower()
    assert "minimum analyzability" in content
    assert "economic coherence" in content
    assert "model reliability" in content
    assert "conflicting" in content or "conflict" in content
    assert "do not choose silently" in content


def test_skill_separates_founder_and_investor_outputs():
    content = (text(SKILL) + text(REFS / "output-contracts.md")).lower()
    assert "founder-facing" in content
    assert "investor-facing" in content
    assert "confidential" in content


def test_skill_requires_cap_table_analysis_when_ownership_is_material():
    content = text(SKILL).lower()
    assert "vc-cap-table-analysis" in content
    assert "ownership" in content and "material" in content


def test_skill_handles_missing_specialist_dependencies_explicitly():
    content = text(SKILL).lower()
    assert "dependency" in content
    assert "unavailable" in content
    assert "never claim" in content
