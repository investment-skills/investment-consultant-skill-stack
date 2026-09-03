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


def test_participating_preferred_takes_preference_then_pro_rata_residual():
    cap = load_module()
    result = cap.participating_waterfall(
        exit_value=D("10000000"),
        preferred_classes=[{
            "name": "Series A",
            "invested_capital": D("1000000"),
            "preference_multiple": D("1"),
            "as_converted_ownership": D("0.20"),
            "participation_cap_multiple": None,
        }],
        common_holders={"Founders": D("1.0")},
    )
    assert result["proceeds"]["Series A"] == D("2800000.0")
    assert result["proceeds"]["Founders"] == D("7200000.0")
    assert sum(result["proceeds"].values()) == D("10000000.0")


def test_participation_cap_limits_preferred_total_proceeds():
    cap = load_module()
    result = cap.participating_waterfall(
        exit_value=D("20000000"),
        preferred_classes=[{
            "name": "Series A",
            "invested_capital": D("1000000"),
            "preference_multiple": D("1"),
            "as_converted_ownership": D("0.20"),
            "participation_cap_multiple": D("3"),
        }],
        common_holders={"Founders": D("1.0")},
    )
    assert result["proceeds"]["Series A"] == D("3000000")
    assert result["proceeds"]["Founders"] == D("17000000")
    assert result["cap_applied"]["Series A"] is True
