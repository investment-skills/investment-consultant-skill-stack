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


def test_pre_money_pool_topup_hits_target_unallocated_pool_after_financing():
    cap = load_module()
    result = cap.pre_money_pool_topup(
        pre_money_fd_shares=D("1000000"),
        current_unallocated_pool=D("50000"),
        target_unallocated_post_round=D("0.10"),
        pre_money_valuation=D("8000000"),
        new_primary_investment=D("2000000"),
    )
    assert_close(result["additional_pool_shares"], D("85714.2857142857142857142857"))
    assert_close(result["unallocated_pool_post_round_pct"], D("0.10"))
    assert result["dilution_borne_by"] == "pre_money_holders"


def test_post_money_pool_topup_shares_dilution_with_new_investor():
    cap = load_module()
    result = cap.post_money_pool_topup(
        pre_money_fd_shares=D("1000000"),
        current_unallocated_pool=D("50000"),
        target_unallocated_post_round=D("0.10"),
        pre_money_valuation=D("8000000"),
        new_primary_investment=D("2000000"),
    )
    assert_close(result["additional_pool_shares"], D("83333.3333333333333333333333"))
    assert_close(result["unallocated_pool_post_round_pct"], D("0.10"))
    assert result["dilution_borne_by"] == "post_money_holders"


def test_multiple_safes_keep_distinct_terms_and_conversion_mechanics():
    cap = load_module()
    pre_safe = cap.convert_safe(
        investment=D("250000"),
        valuation_cap=D("4000000"),
        discount_rate=D("0.20"),
        round_price_per_share=D("5"),
        capitalization=D("1000000"),
        safe_type="pre_money",
    )
    post_safe = cap.convert_safe(
        investment=D("500000"),
        valuation_cap=D("5000000"),
        discount_rate=D("0"),
        round_price_per_share=D("5"),
        capitalization=D("1000000"),
        safe_type="post_money",
    )
    assert pre_safe["shares_issued"] == D("62500")
    assert pre_safe["effective_price"] == D("4")
    assert_close(post_safe["ownership_immediately_after_conversion"], D("0.10"))
    assert_close(post_safe["shares_issued"], D("111111.1111111111111111111111"))
    assert pre_safe["safe_type"] != post_safe["safe_type"]


def test_convertible_note_uses_principal_plus_interest_and_best_economic_price():
    cap = load_module()
    result = cap.convert_note(
        principal=D("200000"),
        accrued_interest=D("20000"),
        valuation_cap=D("4000000"),
        discount_rate=D("0.20"),
        round_price_per_share=D("5"),
        capitalization=D("1000000"),
    )
    assert result["conversion_amount"] == D("220000")
    assert result["effective_price"] == D("4")
    assert result["shares_issued"] == D("55000")


def test_full_pro_rata_investment_maintains_ownership_on_defined_basis():
    cap = load_module()
    result = cap.pro_rata_investment(current_ownership=D("0.10"), other_new_money=D("1800000"))
    assert result["required_investment"] == D("200000")
    assert result["basis"] == "other_new_money"
