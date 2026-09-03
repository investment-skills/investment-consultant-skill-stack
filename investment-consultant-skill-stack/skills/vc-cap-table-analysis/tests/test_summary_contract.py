import importlib.util
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "cap_table.py"


def load_module():
    spec = importlib.util.spec_from_file_location("cap_table", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def D(value):
    return Decimal(str(value))


def test_build_summary_returns_master_skill_integration_contract():
    cap = load_module()
    result = cap.build_summary(
        pre_money_valuation=D("8000000"),
        new_primary_investment=D("2000000"),
        pre_round_fd_ownership={"Founders": D("0.80"), "ESOP": D("0.10"), "Seed": D("0.10")},
        post_round_fd_ownership={"Founders": D("0.64"), "ESOP": D("0.08"), "Seed": D("0.08"), "New Investor": D("0.20")},
        founder_names=["Founders"],
        new_investor_name="New Investor",
        option_pool_post_round=D("0.08"),
        convertible_conversion_summary=[{"instrument": "SAFE A", "shares": D("62500")}],
        pro_rata_summary={"required_investment": D("200000")},
        exit_waterfall_summary={"base_exit": D("10000000")},
        material_ambiguities=[],
        validation_status="passed",
    )
    required = {
        "pre_money_valuation",
        "new_primary_investment",
        "post_money_valuation",
        "pre_round_fd_ownership",
        "post_round_fd_ownership",
        "founder_dilution_pct_points",
        "new_investor_ownership",
        "option_pool_post_round",
        "convertible_conversion_summary",
        "pro_rata_summary",
        "exit_waterfall_summary",
        "material_ambiguities",
        "validation_status",
    }
    assert required <= set(result)
    assert result["post_money_valuation"] == D("10000000")
    assert result["founder_dilution_pct_points"] == D("0.16")
    assert result["new_investor_ownership"] == D("0.20")


def test_build_summary_rejects_reliance_status_when_ownership_does_not_reconcile():
    cap = load_module()
    try:
        cap.build_summary(
            pre_money_valuation=D("8000000"),
            new_primary_investment=D("2000000"),
            pre_round_fd_ownership={"Founders": D("0.90")},
            post_round_fd_ownership={"Founders": D("0.70"), "New Investor": D("0.20")},
            founder_names=["Founders"],
            new_investor_name="New Investor",
            validation_status="passed",
        )
    except ValueError as exc:
        assert "100%" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unreconciled ownership")
