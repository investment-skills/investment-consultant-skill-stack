from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_repository_contains_both_cross_referenced_skill_packages():
    master = ROOT / "skills" / "startup-investment-readiness" / "SKILL.md"
    cap = ROOT / "skills" / "vc-cap-table-analysis" / "SKILL.md"
    assert master.exists()
    assert cap.exists()
    assert "vc-cap-table-analysis" in master.read_text(encoding="utf-8")
    assert "startup-investment-readiness" in cap.read_text(encoding="utf-8")


def test_tested_mechanical_helpers_are_packaged():
    assert (ROOT / "skills" / "startup-investment-readiness" / "scripts" / "readiness_router.py").exists()
    assert (ROOT / "skills" / "vc-cap-table-analysis" / "scripts" / "cap_table.py").exists()


def test_release_readme_exists_with_install_and_test_instructions():
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    assert "startup-investment-readiness" in readme
    assert "vc-cap-table-analysis" in readme
    assert "pytest" in readme
    assert "~/.agents/skills" in readme


def test_approved_specs_are_no_longer_marked_proposed():
    for spec in (ROOT / "docs" / "superpowers" / "specs").glob("*.md"):
        content = spec.read_text(encoding="utf-8")
        assert "Status:** Proposed" not in content
        assert "Status:** Approved / Implemented" in content
