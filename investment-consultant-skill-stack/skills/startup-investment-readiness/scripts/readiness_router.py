"""Deterministic routing helpers for the startup-investment-readiness skill.

The module handles mechanical routing and gate state only. It does not replace
specialist analysis or investment judgment.
"""

from __future__ import annotations

from typing import Any


VALID_STAGES = {
    "idea_pre_launch",
    "launched_pre_revenue",
    "early_revenue",
    "scaling",
    "mature_growth",
}

VALID_MODELS = {
    "saas",
    "subscription",
    "marketplace",
    "transactional",
    "ecommerce",
    "services",
    "hardware",
    "asset_heavy",
    "hybrid",
}


def _add(items: list[str], *values: str) -> None:
    for value in values:
        if value not in items:
            items.append(value)


def _material_conflicts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [c for c in payload.get("evidence_conflicts", []) if c.get("material")]


def route_engagement(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a mechanical analysis route from normalized engagement inputs."""

    stage = payload.get("stage")
    model = payload.get("business_model")
    intent = payload.get("analysis_intent")

    required: list[str] = []
    skipped: list[str] = []
    blocked: list[str] = []
    notes: list[str] = []
    warnings: list[str] = []

    minimum_ok = bool(
        stage in VALID_STAGES
        and model in VALID_MODELS
        and payload.get("revenue_logic_known")
        and payload.get("capital_ask_known")
    )

    waivers = set(payload.get("explicit_gate_waivers", []))

    economic_input = payload.get("economic_coherence_status")
    economic_map = {
        None: "not_assessed",
        "viable": "passed",
        "viable_with_scaling_dependency": "passed_with_conditions",
        "needs_improvement": "passed_with_conditions",
        "inconsistent": "failed",
        "insufficient_data": "failed",
    }
    if economic_input not in economic_map:
        raise ValueError(f"Unsupported economic_coherence_status: {economic_input}")

    model_input = payload.get("model_reliability_status")
    model_map = {
        None: "not_assessed",
        "passed": "passed",
        "passed_with_non_material_warnings": "passed_with_warnings",
        "passed_with_warnings": "passed_with_warnings",
        "failed": "failed",
    }
    if model_input not in model_map:
        raise ValueError(f"Unsupported model_reliability_status: {model_input}")

    gates = {
        "minimum_analyzability": "passed" if minimum_ok else "failed",
        "economic_coherence": economic_map[economic_input],
        "model_reliability": model_map[model_input],
        "evidence_reconciliation": "passed",
        "diligence_coverage": "not_required" if intent != "ic_recommendation" else "not_assessed",
    }

    if not minimum_ok:
        _add(blocked, "valuation", "returns-analysis", "ic-memo")
        warnings.append(
            "Minimum analyzability failed: stage, business model, revenue logic, and capital ask must be known."
        )

    _add(required, "market-sizing-analysis", "startup-metrics-framework")

    if model in {"saas", "subscription"}:
        if stage in {"idea_pre_launch", "launched_pre_revenue"}:
            notes.append(
                "For pre-revenue SaaS, retention metrics are not yet meaningful; focus on pricing logic, runway, product evidence, and milestone financing."
            )
        else:
            notes.append(
                "Use ARR/MRR, churn, NRR, CAC, LTV, payback, gross margin, and burn efficiency where source data permits recomputation."
            )
            _add(required, "unit-economics", "startup-financial-modeling")

    elif model == "marketplace":
        notes.append(
            "Distinguish GMV from revenue explicitly and analyze take rate, liquidity, repeat rate, retention, and contribution margin."
        )
        _add(required, "unit-economics", "startup-financial-modeling")

    elif model == "services":
        notes.append(
            "Use utilization, gross margin, revenue per delivery FTE, repeat revenue, pipeline conversion, and delivery capacity; do not apply SaaS logic mechanically."
        )
        _add(skipped, "saas-specific-multiples")
        if stage not in {"idea_pre_launch", "launched_pre_revenue"}:
            _add(required, "startup-financial-modeling")

    else:
        if stage not in {"idea_pre_launch", "launched_pre_revenue"}:
            _add(required, "unit-economics", "startup-financial-modeling")

    # Financial model and valuation routing.
    if stage not in {"idea_pre_launch", "launched_pre_revenue"}:
        _add(required, "comps-analysis")

    if payload.get("long_term_cash_flow_evidence"):
        _add(required, "dcf-model")
    else:
        _add(skipped, "dcf-model")
        notes.append(
            "DCF is not relied upon without sufficiently meaningful long-term cash-flow evidence; avoid false precision."
        )

    if payload.get("has_spreadsheet_model"):
        _add(required, "3-statement-model", "audit-xls")

    if payload.get("ownership_material"):
        _add(required, "vc-cap-table-analysis")

    if intent in {"full_due_diligence", "ic_recommendation"}:
        _add(required, "datapack-builder", "dd-checklist", "dd-meeting-prep")

    if intent == "ic_recommendation":
        _add(required, "returns-analysis", "ic-memo")

    # Enforce assessed quality gates. Explicit waivers are visible states, not silent bypasses.
    if gates["economic_coherence"] == "failed":
        if "economic_coherence" in waivers:
            gates["economic_coherence"] = "waived"
            warnings.append("Economic coherence gate was explicitly waived; retain the underlying economic risk in the recommendation.")
        else:
            _add(blocked, "ic-memo")
            warnings.append("Economic coherence gate failed; final IC recommendation is blocked until resolved or explicitly waived.")

    if gates["model_reliability"] == "failed":
        _add(blocked, "primary-model-reliance")
        if "model_reliability" in waivers:
            gates["model_reliability"] = "waived"
            warnings.append("Model reliability gate was explicitly waived; the failed model cannot be treated as the primary analytical basis.")
        else:
            _add(blocked, "returns-analysis", "ic-memo")
            warnings.append("Model reliability gate failed; primary model reliance, returns analysis, and final IC recommendation are blocked.")

    if intent == "ic_recommendation":
        coverage_complete = bool(payload.get("diligence_material_coverage_complete"))
        if coverage_complete:
            gates["diligence_coverage"] = "passed"
        elif "diligence_coverage" in waivers:
            gates["diligence_coverage"] = "waived"
            warnings.append("Material diligence coverage was explicitly waived; disclose the waiver and open diligence items in the IC materials.")
        else:
            gates["diligence_coverage"] = "failed"
            _add(blocked, "ic-memo")
            warnings.append("Material diligence coverage is incomplete; final IC recommendation is blocked unless explicitly waived.")

    conflicts = _material_conflicts(payload)
    if conflicts:
        gates["evidence_reconciliation"] = "failed"
        _add(blocked, "ic-memo")
        fields = ", ".join(sorted({str(c.get("field", "unknown")) for c in conflicts}))
        warnings.append(
            f"Material evidence conflict requires reconciliation before final IC recommendation: {fields}."
        )

    return {
        "required_skills": required,
        "skipped_methods": skipped,
        "gates": gates,
        "blocked_outputs": blocked,
        "methodology_notes": notes,
        "warnings": warnings,
    }
