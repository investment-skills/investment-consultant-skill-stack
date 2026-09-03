import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "readiness_router.py"
FIXTURES = Path(__file__).parent / "fixtures"


def load_router():
    spec = importlib.util.spec_from_file_location("readiness_router", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixture(name):
    return json.loads((FIXTURES / name).read_text())


def test_pre_revenue_saas_avoids_authoritative_dcf_and_uses_stage_appropriate_analysis():
    result = load_router().route_engagement(fixture("pre_revenue_saas.json"))
    assert "market-sizing-analysis" in result["required_skills"]
    assert "startup-metrics-framework" in result["required_skills"]
    assert "dcf-model" in result["skipped_methods"]
    assert "retention metrics are not yet meaningful" in " ".join(result["methodology_notes"]).lower()
    assert result["gates"]["minimum_analyzability"] == "passed"


def test_early_revenue_saas_routes_to_metrics_model_comps_audit_and_cap_table():
    result = load_router().route_engagement(fixture("early_revenue_saas.json"))
    for skill in [
        "startup-metrics-framework",
        "unit-economics",
        "startup-financial-modeling",
        "comps-analysis",
        "audit-xls",
        "vc-cap-table-analysis",
        "dd-checklist",
        "dd-meeting-prep",
    ]:
        assert skill in result["required_skills"]
    assert "dcf-model" in result["skipped_methods"]


def test_marketplace_explicitly_distinguishes_gmv_from_revenue():
    result = load_router().route_engagement(fixture("marketplace.json"))
    notes = " ".join(result["methodology_notes"]).lower()
    assert "gmv" in notes and "revenue" in notes
    assert "take rate" in notes
    assert "unit-economics" in result["required_skills"]


def test_services_business_uses_services_metrics_and_avoids_mechanical_saas_logic():
    result = load_router().route_engagement(fixture("services.json"))
    notes = " ".join(result["methodology_notes"]).lower()
    assert "utilization" in notes
    assert "delivery capacity" in notes
    assert "saas-specific-multiples" in result["skipped_methods"]


def test_material_conflicting_evidence_blocks_ic_recommendation():
    result = load_router().route_engagement(fixture("conflicting_data.json"))
    assert "ic-memo" in result["blocked_outputs"]
    assert result["gates"]["evidence_reconciliation"] == "failed"
    assert any("conflict" in warning.lower() for warning in result["warnings"])


def test_failed_economic_coherence_blocks_final_ic_recommendation():
    payload = fixture("conflicting_data.json")
    payload["evidence_conflicts"] = []
    payload["economic_coherence_status"] = "inconsistent"
    payload["diligence_material_coverage_complete"] = True
    result = load_router().route_engagement(payload)
    assert result["gates"]["economic_coherence"] == "failed"
    assert "ic-memo" in result["blocked_outputs"]


def test_failed_model_reliability_blocks_primary_valuation_returns_and_ic_without_waiver():
    payload = fixture("conflicting_data.json")
    payload["evidence_conflicts"] = []
    payload["economic_coherence_status"] = "viable"
    payload["model_reliability_status"] = "failed"
    payload["diligence_material_coverage_complete"] = True
    result = load_router().route_engagement(payload)
    assert result["gates"]["model_reliability"] == "failed"
    assert "primary-model-reliance" in result["blocked_outputs"]
    assert "returns-analysis" in result["blocked_outputs"]
    assert "ic-memo" in result["blocked_outputs"]


def test_ic_requires_material_diligence_coverage_or_explicit_waiver():
    payload = fixture("conflicting_data.json")
    payload["evidence_conflicts"] = []
    payload["economic_coherence_status"] = "viable"
    payload["model_reliability_status"] = "passed"
    payload["diligence_material_coverage_complete"] = False
    result = load_router().route_engagement(payload)
    assert result["gates"]["diligence_coverage"] == "failed"
    assert "ic-memo" in result["blocked_outputs"]

    payload["explicit_gate_waivers"] = ["diligence_coverage"]
    waived = load_router().route_engagement(payload)
    assert waived["gates"]["diligence_coverage"] == "waived"
    assert "ic-memo" not in waived["blocked_outputs"]
    assert any("waiv" in warning.lower() for warning in waived["warnings"])
