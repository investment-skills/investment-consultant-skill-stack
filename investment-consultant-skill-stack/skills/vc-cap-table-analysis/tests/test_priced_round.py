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


def test_simple_priced_round_reconciles_post_money_ownership():
    cap = load_module()
    pre = {"Founders": D("0.80"), "ESOP": D("0.10"), "Seed Investor": D("0.10")}
    result = cap.priced_round(D("8000000"), D("2000000"), pre)
    assert result["post_money_valuation"] == D("10000000")
    assert result["new_investor_ownership"] == D("0.20")
    assert result["post_round_ownership"]["Founders"] == D("0.64")
    assert result["post_round_ownership"]["ESOP"] == D("0.08")
    assert result["post_round_ownership"]["Seed Investor"] == D("0.08")
    assert sum(result["post_round_ownership"].values()) + result["new_investor_ownership"] == D("1")


def test_reconcile_ownership_fails_when_supplied_percentages_conflict_with_share_counts():
    cap = load_module()
    holders = [
        {"name": "Founder", "shares": D("800"), "ownership": D("0.70")},
        {"name": "Investor", "shares": D("200"), "ownership": D("0.30")},
    ]
    result = cap.reconcile_ownership(holders)
    assert result["validation_status"] == "failed"
    assert result["share_total"] == D("1000")
    assert result["ownership_total"] == D("1.00")
    assert result["mismatches"]
