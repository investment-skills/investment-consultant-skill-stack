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


def test_senior_preference_is_paid_before_junior_tier():
    cap = load_module()
    result = cap.allocate_preference_stack(
        D("2500000"),
        [
            {"name": "Series B", "preference": D("2000000"), "seniority": 1},
            {"name": "Series A", "preference": D("1000000"), "seniority": 2},
        ],
    )
    assert result["payments"]["Series B"] == D("2000000")
    assert result["payments"]["Series A"] == D("500000")
    assert result["remaining_value"] == D("0")


def test_same_seniority_tier_is_pari_passu_when_value_is_insufficient():
    cap = load_module()
    result = cap.allocate_preference_stack(
        D("1500000"),
        [
            {"name": "A", "preference": D("1000000"), "seniority": 1},
            {"name": "B", "preference": D("2000000"), "seniority": 1},
        ],
    )
    assert result["payments"]["A"] == D("500000")
    assert result["payments"]["B"] == D("1000000")


def test_non_participating_waterfall_respects_seniority_before_common_residual():
    cap = load_module()
    result = cap.non_participating_waterfall(
        D("2500000"),
        [
            {
                "name": "Series B",
                "invested_capital": D("2000000"),
                "preference_multiple": D("1"),
                "as_converted_ownership": D("0.20"),
                "seniority": 1,
            },
            {
                "name": "Series A",
                "invested_capital": D("1000000"),
                "preference_multiple": D("1"),
                "as_converted_ownership": D("0.20"),
                "seniority": 2,
            },
        ],
        {"Founders": D("1.0")},
    )
    assert result["elections"]["Series B"] == "preference"
    assert result["elections"]["Series A"] == "preference"
    assert result["proceeds"]["Series B"] == D("2000000")
    assert result["proceeds"]["Series A"] == D("500000")
    assert result["proceeds"]["Founders"] == D("0")


def test_participating_waterfall_respects_seniority_when_exit_cannot_cover_preferences():
    cap = load_module()
    result = cap.participating_waterfall(
        D("2500000"),
        [
            {
                "name": "Series B",
                "invested_capital": D("2000000"),
                "preference_multiple": D("1"),
                "as_converted_ownership": D("0.20"),
                "seniority": 1,
                "participation_cap_multiple": None,
            },
            {
                "name": "Series A",
                "invested_capital": D("1000000"),
                "preference_multiple": D("1"),
                "as_converted_ownership": D("0.20"),
                "seniority": 2,
                "participation_cap_multiple": None,
            },
        ],
        {"Founders": D("1.0")},
    )
    assert result["proceeds"]["Series B"] == D("2000000")
    assert result["proceeds"]["Series A"] == D("500000")
    assert result["proceeds"]["Founders"] == D("0")
