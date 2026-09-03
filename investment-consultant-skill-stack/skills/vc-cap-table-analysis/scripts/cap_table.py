"""High-precision economic calculations for VC cap-table analysis.

This module models arithmetic only. It does not interpret legal documents.
All percentages are represented as Decimal fractions, e.g. Decimal('0.20').
"""

from __future__ import annotations

from decimal import Decimal, getcontext
from typing import Any, Mapping

getcontext().prec = 40

TOLERANCE = Decimal("0.000001")
ONE = Decimal("1")
ZERO = Decimal("0")


def _d(value: Any) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _validate_nonnegative(name: str, value: Decimal) -> None:
    if value < ZERO:
        raise ValueError(f"{name} cannot be negative")


def reconcile_ownership(holders: list[dict[str, Any]], tolerance: Decimal = TOLERANCE) -> dict[str, Any]:
    """Reconcile supplied ownership percentages to share-derived ownership."""
    if not holders:
        return {
            "validation_status": "failed",
            "share_total": ZERO,
            "ownership_total": ZERO,
            "mismatches": [{"reason": "empty cap table"}],
        }

    shares = [_d(h.get("shares", ZERO)) for h in holders]
    supplied = [_d(h.get("ownership", ZERO)) for h in holders]
    if any(s < ZERO for s in shares) or any(p < ZERO for p in supplied):
        raise ValueError("shares and ownership cannot be negative")

    share_total = sum(shares, ZERO)
    ownership_total = sum(supplied, ZERO)
    mismatches: list[dict[str, Any]] = []

    if share_total <= ZERO:
        mismatches.append({"reason": "non-positive share total"})
    else:
        for holder, share_count, stated in zip(holders, shares, supplied):
            derived = share_count / share_total
            if abs(derived - stated) > tolerance:
                mismatches.append(
                    {
                        "name": holder.get("name"),
                        "stated_ownership": stated,
                        "share_derived_ownership": derived,
                    }
                )

    if abs(ownership_total - ONE) > tolerance:
        mismatches.append(
            {"reason": "ownership does not total 100%", "ownership_total": ownership_total}
        )

    return {
        "validation_status": "passed" if not mismatches else "failed",
        "share_total": share_total,
        "ownership_total": ownership_total,
        "mismatches": mismatches,
    }


def price_per_share(pre_money_valuation: Any, pre_money_fd_shares: Any) -> Decimal:
    valuation = _d(pre_money_valuation)
    shares = _d(pre_money_fd_shares)
    _validate_nonnegative("pre_money_valuation", valuation)
    if shares <= ZERO:
        raise ValueError("pre_money_fd_shares must be positive")
    return valuation / shares


def priced_round(
    pre_money_valuation: Any,
    new_primary_investment: Any,
    pre_round_ownership: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Model a standard primary priced round without simultaneous pool changes."""
    pre = _d(pre_money_valuation)
    investment = _d(new_primary_investment)
    if pre <= ZERO:
        raise ValueError("pre_money_valuation must be positive")
    _validate_nonnegative("new_primary_investment", investment)

    post = pre + investment
    new_investor_ownership = investment / post
    existing_factor = pre / post

    post_ownership: dict[str, Decimal] = {}
    if pre_round_ownership is not None:
        normalized = {name: _d(value) for name, value in pre_round_ownership.items()}
        total = sum(normalized.values(), ZERO)
        if abs(total - ONE) > TOLERANCE:
            raise ValueError("pre_round_ownership must total 100%")
        if any(value < ZERO for value in normalized.values()):
            raise ValueError("ownership cannot be negative")
        post_ownership = {name: value * existing_factor for name, value in normalized.items()}

    return {
        "pre_money_valuation": pre,
        "new_primary_investment": investment,
        "post_money_valuation": post,
        "new_investor_ownership": new_investor_ownership,
        "post_round_ownership": post_ownership,
    }


def _validate_target_pct(name: str, value: Decimal) -> None:
    if value < ZERO or value >= ONE:
        raise ValueError(f"{name} must be >= 0 and < 1")


def pre_money_pool_topup(
    pre_money_fd_shares: Any,
    current_unallocated_pool: Any,
    target_unallocated_post_round: Any,
    pre_money_valuation: Any,
    new_primary_investment: Any,
) -> dict[str, Any]:
    """Top up the unallocated pool pre-money to a target post-round percentage."""
    shares = _d(pre_money_fd_shares)
    current_pool = _d(current_unallocated_pool)
    target = _d(target_unallocated_post_round)
    pre = _d(pre_money_valuation)
    investment = _d(new_primary_investment)
    if shares <= ZERO or pre <= ZERO:
        raise ValueError("pre-money shares and valuation must be positive")
    _validate_nonnegative("current_unallocated_pool", current_pool)
    _validate_nonnegative("new_primary_investment", investment)
    _validate_target_pct("target_unallocated_post_round", target)

    investment_ratio = investment / pre
    denominator = ONE - target * (ONE + investment_ratio)
    if denominator <= ZERO:
        raise ValueError("target pool is infeasible for the supplied financing")
    additional = (target * (ONE + investment_ratio) * shares - current_pool) / denominator
    if additional < ZERO:
        additional = ZERO

    pre_round_after_pool = shares + additional
    pps = pre / pre_round_after_pool
    new_shares = investment / pps if investment else ZERO
    post_total = pre_round_after_pool + new_shares
    pool_post = current_pool + additional

    return {
        "additional_pool_shares": additional,
        "pre_round_fd_shares_after_topup": pre_round_after_pool,
        "new_investor_shares": new_shares,
        "post_round_fd_shares": post_total,
        "unallocated_pool_post_round": pool_post,
        "unallocated_pool_post_round_pct": pool_post / post_total,
        "dilution_borne_by": "pre_money_holders",
    }


def post_money_pool_topup(
    pre_money_fd_shares: Any,
    current_unallocated_pool: Any,
    target_unallocated_post_round: Any,
    pre_money_valuation: Any,
    new_primary_investment: Any,
) -> dict[str, Any]:
    """Create/top up the unallocated pool after the priced financing."""
    shares = _d(pre_money_fd_shares)
    current_pool = _d(current_unallocated_pool)
    target = _d(target_unallocated_post_round)
    pre = _d(pre_money_valuation)
    investment = _d(new_primary_investment)
    if shares <= ZERO or pre <= ZERO:
        raise ValueError("pre-money shares and valuation must be positive")
    _validate_nonnegative("current_unallocated_pool", current_pool)
    _validate_nonnegative("new_primary_investment", investment)
    _validate_target_pct("target_unallocated_post_round", target)

    pps = pre / shares
    new_shares = investment / pps if investment else ZERO
    post_before_pool = shares + new_shares
    additional = (target * post_before_pool - current_pool) / (ONE - target)
    if additional < ZERO:
        additional = ZERO
    post_total = post_before_pool + additional
    pool_post = current_pool + additional

    return {
        "additional_pool_shares": additional,
        "new_investor_shares": new_shares,
        "post_round_fd_shares": post_total,
        "unallocated_pool_post_round": pool_post,
        "unallocated_pool_post_round_pct": pool_post / post_total,
        "dilution_borne_by": "post_money_holders",
    }


def _discount_price(round_price_per_share: Decimal, discount_rate: Decimal) -> Decimal:
    if discount_rate < ZERO or discount_rate >= ONE:
        raise ValueError("discount_rate must be >= 0 and < 1")
    return round_price_per_share * (ONE - discount_rate)


def convert_safe(
    investment: Any,
    valuation_cap: Any,
    discount_rate: Any,
    round_price_per_share: Any,
    capitalization: Any,
    safe_type: str,
) -> dict[str, Any]:
    """Model supplied SAFE economics without interpreting legal definitions."""
    amount = _d(investment)
    cap_value = _d(valuation_cap)
    discount = _d(discount_rate)
    round_price = _d(round_price_per_share)
    cap_shares = _d(capitalization)
    if amount <= ZERO or cap_value <= ZERO or round_price <= ZERO or cap_shares <= ZERO:
        raise ValueError("SAFE inputs must be positive except discount")
    if safe_type not in {"pre_money", "post_money"}:
        raise ValueError("safe_type must be pre_money or post_money")

    discount_price = _discount_price(round_price, discount)

    if safe_type == "pre_money":
        cap_price = cap_value / cap_shares
        effective = min(cap_price, discount_price)
        shares_issued = amount / effective
        method = "cap" if cap_price < discount_price else "discount" if discount_price < cap_price else "cap_or_discount_equal"
        ownership = shares_issued / (cap_shares + shares_issued)
    else:
        target_ownership = amount / cap_value
        if target_ownership <= ZERO or target_ownership >= ONE:
            raise ValueError("post-money SAFE cap implies invalid ownership")
        cap_route_shares = target_ownership * cap_shares / (ONE - target_ownership)
        discount_route_shares = amount / discount_price
        if cap_route_shares >= discount_route_shares:
            shares_issued = cap_route_shares
            effective = amount / shares_issued
            method = "post_money_cap"
        else:
            shares_issued = discount_route_shares
            effective = discount_price
            method = "discount"
        ownership = shares_issued / (cap_shares + shares_issued)

    return {
        "safe_type": safe_type,
        "investment": amount,
        "effective_price": effective,
        "shares_issued": shares_issued,
        "ownership_immediately_after_conversion": ownership,
        "effective_method": method,
    }


def convert_note(
    principal: Any,
    accrued_interest: Any,
    valuation_cap: Any,
    discount_rate: Any,
    round_price_per_share: Any,
    capitalization: Any,
) -> dict[str, Any]:
    """Convert a note using the economically more favorable supplied cap/discount price."""
    principal_d = _d(principal)
    interest = _d(accrued_interest)
    cap_value = _d(valuation_cap)
    discount = _d(discount_rate)
    round_price = _d(round_price_per_share)
    cap_shares = _d(capitalization)
    if principal_d <= ZERO or cap_value <= ZERO or round_price <= ZERO or cap_shares <= ZERO:
        raise ValueError("note inputs must be positive except interest/discount")
    _validate_nonnegative("accrued_interest", interest)

    amount = principal_d + interest
    cap_price = cap_value / cap_shares
    discount_price = _discount_price(round_price, discount)
    effective = min(cap_price, discount_price)
    method = "cap" if cap_price < discount_price else "discount" if discount_price < cap_price else "cap_or_discount_equal"
    return {
        "conversion_amount": amount,
        "cap_price": cap_price,
        "discount_price": discount_price,
        "effective_price": effective,
        "shares_issued": amount / effective,
        "effective_method": method,
    }


def pro_rata_investment(current_ownership: Any, other_new_money: Any) -> dict[str, Any]:
    """Return investment required to preserve ownership when other investors invest a known amount."""
    ownership = _d(current_ownership)
    other = _d(other_new_money)
    if ownership < ZERO or ownership >= ONE:
        raise ValueError("current_ownership must be >= 0 and < 1")
    _validate_nonnegative("other_new_money", other)
    required = ownership * other / (ONE - ownership)
    return {
        "current_ownership": ownership,
        "other_new_money": other,
        "required_investment": required,
        "basis": "other_new_money",
    }


def full_ratchet_price(original_conversion_price: Any, new_issue_price: Any) -> Decimal:
    """Economic illustration of full-ratchet anti-dilution."""
    original = _d(original_conversion_price)
    new_price = _d(new_issue_price)
    if original <= ZERO or new_price <= ZERO:
        raise ValueError("conversion prices must be positive")
    return min(original, new_price)


def broad_based_weighted_average_price(
    original_conversion_price: Any,
    fully_diluted_shares_before: Any,
    new_money: Any,
    new_shares_issued: Any,
) -> Decimal:
    """Broad-based weighted-average illustration: CP2 = CP1*(A+B)/(A+C)."""
    cp1 = _d(original_conversion_price)
    a = _d(fully_diluted_shares_before)
    money = _d(new_money)
    c = _d(new_shares_issued)
    if cp1 <= ZERO or a <= ZERO or c < ZERO or money < ZERO:
        raise ValueError("anti-dilution inputs are invalid")
    b = money / cp1
    return cp1 * (a + b) / (a + c)


def _waterfall_for_elections(
    exit_value: Decimal,
    preferred_classes: list[dict[str, Any]],
    common_holders: Mapping[str, Any],
    preference_names: set[str],
) -> dict[str, Any]:
    preferred: list[dict[str, Any]] = []
    total_pref_as_converted = ZERO
    for item in preferred_classes:
        name = str(item["name"])
        invested = _d(item["invested_capital"])
        multiple = _d(item.get("preference_multiple", ONE))
        ownership = _d(item["as_converted_ownership"])
        seniority = int(item.get("seniority", 1))
        if invested < ZERO or multiple < ZERO or ownership < ZERO or seniority < 1:
            raise ValueError("preferred inputs are invalid")
        preferred.append(
            {
                "name": name,
                "preference": invested * multiple,
                "ownership": ownership,
                "seniority": seniority,
            }
        )
        total_pref_as_converted += ownership

    if total_pref_as_converted > ONE + TOLERANCE:
        raise ValueError("preferred as-converted ownership exceeds 100%")

    common_weights = {str(k): _d(v) for k, v in common_holders.items()}
    common_weight_total = sum(common_weights.values(), ZERO)
    if common_weights and abs(common_weight_total - ONE) > TOLERANCE:
        raise ValueError("common_holders weights must total 100%")
    if any(v < ZERO for v in common_weights.values()):
        raise ValueError("common holder weights cannot be negative")

    pref_electors = [item for item in preferred if item["name"] in preference_names]
    convert_electors = [item for item in preferred if item["name"] not in preference_names]

    proceeds: dict[str, Decimal] = {item["name"]: ZERO for item in preferred}
    proceeds.update({name: ZERO for name in common_weights})

    stack = allocate_preference_stack(
        exit_value,
        [
            {
                "name": item["name"],
                "preference": item["preference"],
                "seniority": item["seniority"],
            }
            for item in pref_electors
        ],
    )
    for name, payment in stack["payments"].items():
        proceeds[name] = payment

    residual = stack["remaining_value"]
    removed_ownership = sum((item["ownership"] for item in pref_electors), ZERO)
    residual_denominator = ONE - removed_ownership
    if residual_denominator <= ZERO or residual <= ZERO:
        return {"proceeds": proceeds}

    for item in convert_electors:
        proceeds[item["name"]] = residual * item["ownership"] / residual_denominator

    common_as_converted = ONE - total_pref_as_converted
    common_residual = residual * common_as_converted / residual_denominator
    for name, weight in common_weights.items():
        proceeds[name] = common_residual * weight

    return {"proceeds": proceeds}


def non_participating_waterfall(
    exit_value: Any,
    preferred_classes: list[dict[str, Any]],
    common_holders: Mapping[str, Any],
) -> dict[str, Any]:
    """Solve non-participating preference-vs-conversion elections for pari passu classes.

    `common_holders` are weights within the non-preferred common pool, not fully
    diluted ownership percentages.
    """
    exit_d = _d(exit_value)
    if exit_d < ZERO:
        raise ValueError("exit_value cannot be negative")

    names = [str(item["name"]) for item in preferred_classes]
    if len(set(names)) != len(names):
        raise ValueError("preferred class names must be unique")
    if len(names) > 12:
        raise ValueError("too many preferred classes for exhaustive V1 election solver")

    scenarios: dict[frozenset[str], dict[str, Any]] = {}
    for mask in range(1 << len(names)):
        preference_names = frozenset(
            names[i] for i in range(len(names)) if mask & (1 << i)
        )
        scenarios[preference_names] = _waterfall_for_elections(
            exit_d, preferred_classes, common_holders, set(preference_names)
        )

    stable: list[tuple[frozenset[str], dict[str, Any]]] = []
    for choices, result in scenarios.items():
        is_stable = True
        for name in names:
            flipped = set(choices)
            if name in flipped:
                flipped.remove(name)
            else:
                flipped.add(name)
            current_payoff = result["proceeds"][name]
            alternate_payoff = scenarios[frozenset(flipped)]["proceeds"][name]
            if alternate_payoff > current_payoff + TOLERANCE:
                is_stable = False
                break
        if is_stable:
            stable.append((choices, result))

    if not stable:
        raise ValueError("no internally consistent preference/conversion election found")

    # Deterministic tie-break: choose the stable scenario with the highest total
    # preferred proceeds, then fewer preference elections.
    def score(item: tuple[frozenset[str], dict[str, Any]]) -> tuple[Decimal, int]:
        choices, result = item
        pref_total = sum((result["proceeds"][name] for name in names), ZERO)
        return pref_total, -len(choices)

    choices, selected = max(stable, key=score)
    elections = {name: ("preference" if name in choices else "convert") for name in names}
    total_distributed = sum(selected["proceeds"].values(), ZERO)
    if abs(total_distributed - exit_d) > TOLERANCE:
        raise ValueError("waterfall proceeds do not reconcile to exit value")

    return {
        "exit_value": exit_d,
        "elections": elections,
        "proceeds": selected["proceeds"],
        "validation_status": "passed",
    }


def _normalize_ownership_map(values: Mapping[str, Any]) -> dict[str, Decimal]:
    normalized = {str(name): _d(value) for name, value in values.items()}
    if any(value < ZERO for value in normalized.values()):
        raise ValueError("ownership cannot be negative")
    total = sum(normalized.values(), ZERO)
    if abs(total - ONE) > TOLERANCE:
        raise ValueError("ownership must total 100%")
    return normalized


def build_summary(
    *,
    pre_money_valuation: Any,
    new_primary_investment: Any,
    pre_round_fd_ownership: Mapping[str, Any],
    post_round_fd_ownership: Mapping[str, Any],
    founder_names: list[str],
    new_investor_name: str,
    option_pool_post_round: Any | None = None,
    convertible_conversion_summary: list[dict[str, Any]] | None = None,
    pro_rata_summary: dict[str, Any] | None = None,
    exit_waterfall_summary: dict[str, Any] | None = None,
    material_ambiguities: list[str] | None = None,
    validation_status: str = "passed",
) -> dict[str, Any]:
    """Build the machine-readable integration contract for the master skill."""
    pre = _d(pre_money_valuation)
    investment = _d(new_primary_investment)
    if pre <= ZERO or investment < ZERO:
        raise ValueError("valuation must be positive and investment non-negative")
    pre_own = _normalize_ownership_map(pre_round_fd_ownership)
    post_own = _normalize_ownership_map(post_round_fd_ownership)

    founder_pre = sum((pre_own.get(name, ZERO) for name in founder_names), ZERO)
    founder_post = sum((post_own.get(name, ZERO) for name in founder_names), ZERO)
    if founder_post > founder_pre + TOLERANCE:
        raise ValueError("founder ownership increased unexpectedly; review transaction inputs")

    new_investor_ownership = post_own.get(new_investor_name)
    if new_investor_ownership is None:
        raise ValueError("new investor is missing from post-round ownership")

    if validation_status not in {"passed", "passed_with_explicit_assumptions", "failed"}:
        raise ValueError("invalid validation_status")

    return {
        "pre_money_valuation": pre,
        "new_primary_investment": investment,
        "post_money_valuation": pre + investment,
        "pre_round_fd_ownership": pre_own,
        "post_round_fd_ownership": post_own,
        "founder_dilution_pct_points": founder_pre - founder_post,
        "new_investor_ownership": new_investor_ownership,
        "option_pool_post_round": ZERO if option_pool_post_round is None else _d(option_pool_post_round),
        "convertible_conversion_summary": convertible_conversion_summary or [],
        "pro_rata_summary": pro_rata_summary or {},
        "exit_waterfall_summary": exit_waterfall_summary or {},
        "material_ambiguities": material_ambiguities or [],
        "validation_status": validation_status,
    }


def participating_waterfall(
    exit_value: Any,
    preferred_classes: list[dict[str, Any]],
    common_holders: Mapping[str, Any],
) -> dict[str, Any]:
    """Model pari-passu participating preferred with optional participation caps.

    Preferred classes receive their liquidation preference first, then
    participate in residual value on an as-converted basis. A participation cap
    limits total proceeds for that preferred class. This is an economic model,
    not a legal interpretation of priority language.
    """
    exit_d = _d(exit_value)
    if exit_d < ZERO:
        raise ValueError("exit_value cannot be negative")

    common_weights = {str(k): _d(v) for k, v in common_holders.items()}
    if common_weights:
        total_common_weight = sum(common_weights.values(), ZERO)
        if abs(total_common_weight - ONE) > TOLERANCE:
            raise ValueError("common_holders weights must total 100%")
        if any(v < ZERO for v in common_weights.values()):
            raise ValueError("common holder weights cannot be negative")

    parsed: list[dict[str, Any]] = []
    total_pref_ownership = ZERO
    for item in preferred_classes:
        name = str(item["name"])
        invested = _d(item["invested_capital"])
        pref_multiple = _d(item.get("preference_multiple", ONE))
        ownership = _d(item["as_converted_ownership"])
        cap_multiple_raw = item.get("participation_cap_multiple")
        cap_multiple = None if cap_multiple_raw is None else _d(cap_multiple_raw)
        if invested < ZERO or pref_multiple < ZERO or ownership < ZERO:
            raise ValueError("preferred inputs cannot be negative")
        if cap_multiple is not None and cap_multiple < pref_multiple:
            raise ValueError("participation cap multiple cannot be below liquidation preference multiple")
        seniority = int(item.get("seniority", 1))
        if seniority < 1:
            raise ValueError("seniority must be >= 1")
        parsed.append(
            {
                "name": name,
                "invested": invested,
                "preference": invested * pref_multiple,
                "ownership": ownership,
                "cap_total": None if cap_multiple is None else invested * cap_multiple,
                "seniority": seniority,
            }
        )
        total_pref_ownership += ownership

    if total_pref_ownership > ONE + TOLERANCE:
        raise ValueError("preferred as-converted ownership exceeds 100%")

    proceeds: dict[str, Decimal] = {item["name"]: ZERO for item in parsed}
    proceeds.update({name: ZERO for name in common_weights})
    cap_applied = {item["name"]: False for item in parsed}

    stack = allocate_preference_stack(
        exit_d,
        [
            {
                "name": item["name"],
                "preference": item["preference"],
                "seniority": item["seniority"],
            }
            for item in parsed
        ],
    )
    for name, payment in stack["payments"].items():
        proceeds[name] = payment

    residual = stack["remaining_value"]
    if residual <= ZERO:
        return {
            "exit_value": exit_d,
            "proceeds": proceeds,
            "cap_applied": cap_applied,
            "validation_status": "passed",
        }

    common_as_converted = ONE - total_pref_ownership

    # Allocate residual by as-converted weights, re-running the allocation when
    # a capped preferred class reaches its remaining participation capacity.
    active = {
        item["name"]: {
            "weight": item["ownership"],
            "capacity": None
            if item["cap_total"] is None
            else item["cap_total"] - item["preference"],
        }
        for item in parsed
        if item["ownership"] > ZERO
    }
    if common_as_converted > ZERO:
        active["__common__"] = {"weight": common_as_converted, "capacity": None}

    common_residual = ZERO
    remaining = residual
    while remaining > TOLERANCE and active:
        total_weight = sum((entry["weight"] for entry in active.values()), ZERO)
        if total_weight <= ZERO:
            break

        tentative = {
            name: remaining * entry["weight"] / total_weight for name, entry in active.items()
        }
        binding = [
            name
            for name, allocation in tentative.items()
            if name != "__common__"
            and active[name]["capacity"] is not None
            and allocation > active[name]["capacity"] + TOLERANCE
        ]

        if not binding:
            for name, allocation in tentative.items():
                if name == "__common__":
                    common_residual += allocation
                else:
                    proceeds[name] += allocation
            remaining = ZERO
            break

        for name in binding:
            capacity = active[name]["capacity"]
            if capacity is None:
                continue
            proceeds[name] += capacity
            remaining -= capacity
            cap_applied[name] = True
            del active[name]

    if remaining > TOLERANCE:
        common_residual += remaining
        remaining = ZERO

    for name, weight in common_weights.items():
        proceeds[name] += common_residual * weight

    total_distributed = sum(proceeds.values(), ZERO)
    if abs(total_distributed - exit_d) > TOLERANCE:
        raise ValueError("waterfall proceeds do not reconcile to exit value")

    return {
        "exit_value": exit_d,
        "proceeds": proceeds,
        "cap_applied": cap_applied,
        "validation_status": "passed",
    }


def allocate_preference_stack(exit_value: Any, preference_classes: list[dict[str, Any]]) -> dict[str, Any]:
    """Allocate liquidation preferences by seniority tier, pari passu within a tier.

    `seniority=1` is the most senior tier; larger integers are junior. Classes
    with the same seniority rank share insufficient value pro rata to their
    preference entitlements.
    """
    remaining = _d(exit_value)
    if remaining < ZERO:
        raise ValueError("exit_value cannot be negative")

    parsed: list[dict[str, Any]] = []
    names: set[str] = set()
    for item in preference_classes:
        name = str(item["name"])
        if name in names:
            raise ValueError("preference class names must be unique")
        names.add(name)
        preference = _d(item["preference"])
        seniority = int(item.get("seniority", 1))
        if preference < ZERO or seniority < 1:
            raise ValueError("preference must be non-negative and seniority >= 1")
        parsed.append({"name": name, "preference": preference, "seniority": seniority})

    payments = {item["name"]: ZERO for item in parsed}
    for rank in sorted({item["seniority"] for item in parsed}):
        tier = [item for item in parsed if item["seniority"] == rank]
        tier_total = sum((item["preference"] for item in tier), ZERO)
        if tier_total <= ZERO:
            continue
        if remaining >= tier_total:
            for item in tier:
                payments[item["name"]] = item["preference"]
            remaining -= tier_total
        else:
            for item in tier:
                payments[item["name"]] = remaining * item["preference"] / tier_total
            remaining = ZERO
            break

    return {"payments": payments, "remaining_value": remaining}
