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


def assert_close(actual, expected, tol=D("0.0000001")):
    assert abs(actual - expected) <= tol


def test_full_ratchet_resets_conversion_price_to_lower_new_issue_price():
    cap = load_module()
    assert cap.full_ratchet_price(D("10"), D("4")) == D("4")
    assert cap.full_ratchet_price(D("10"), D("12")) == D("10")


def test_broad_based_weighted_average_uses_standard_economic_formula():
    cap = load_module()
    adjusted = cap.broad_based_weighted_average_price(
        original_conversion_price=D("10"),
        fully_diluted_shares_before=D("1000000"),
        new_money=D("1000000"),
        new_shares_issued=D("200000"),
    )
    assert_close(adjusted, D("9.166666666666666666666666667"))


def test_non_participating_preferred_takes_preference_at_low_exit_and_converts_above_crossover():
    cap = load_module()
    preferred = [{
        "name": "Series Seed",
        "invested_capital": D("1000000"),
        "preference_multiple": D("1"),
        "as_converted_ownership": D("0.20"),
    }]
    common = {"Founders": D("1.0")}

    low = cap.non_participating_waterfall(D("2000000"), preferred, common)
    assert low["elections"]["Series Seed"] == "preference"
    assert low["proceeds"]["Series Seed"] == D("1000000")
    assert low["proceeds"]["Founders"] == D("1000000")
    assert sum(low["proceeds"].values()) == D("2000000")

    high = cap.non_participating_waterfall(D("10000000"), preferred, common)
    assert high["elections"]["Series Seed"] == "convert"
    assert high["proceeds"]["Series Seed"] == D("2000000.00")
    assert high["proceeds"]["Founders"] == D("8000000.00")
    assert sum(high["proceeds"].values()) == D("10000000.00")
