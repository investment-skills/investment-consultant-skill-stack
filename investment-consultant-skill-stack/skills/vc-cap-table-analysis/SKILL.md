---
name: vc-cap-table-analysis
description: Use when modeling startup ownership, dilution, priced rounds, option-pool changes, SAFE or convertible-note conversion, pro-rata, anti-dilution, or equity exit waterfalls.
---

# VC Cap Table Analysis

## Overview

Model startup financing economics transparently on a fully diluted basis. This skill produces an **economic model**, not a legal interpretation. Security definitions and contractual terms are inputs; ambiguous legal language must be escalated or modeled as explicit scenarios.

## First Gate: Reconcile the Baseline

Before transaction modeling, reconcile issued shares, preferred as-converted shares, granted options, unallocated pool, and supplied ownership. Share-derived and stated ownership must reconcile to 100% within tolerance.

If they do not reconcile, stop definitive round modeling. List the mismatch and required assumption. Use `scripts/cap_table.py` for tested arithmetic helpers.

## Round Mechanics

Read `references/round-mechanics.md` for priced rounds, pre-money vs post-money pool top-ups, dilution bridges, pro-rata, validation rules, and the master-skill integration contract.

Never mix pre-money and post-money mechanics silently. State whether the option-pool target is granted, total, or unallocated and whether the adjustment occurs before or after new money.

## SAFEs and Notes

Read `references/convertibles.md` before conversion analysis. Every SAFE must have an explicit **SAFE type**: pre-money or post-money. Preserve unlike SAFEs/notes separately; do not blend different caps, discounts, or capitalization definitions.

When a capitalization definition or conversion term materially changes the result and is missing, return scenarios or `passed_with_explicit_assumptions`, not false precision.

## Anti-Dilution and Waterfalls

Read `references/anti-dilution-and-waterfalls.md` for full-ratchet and broad-based weighted-average illustrations, liquidation preferences, participating/non-participating preferred, participation caps, senior/junior tiers, and pari passu treatment.

Only model anti-dilution from supplied contractual variables or an explicitly selected standard illustration. Label the result economic, not legal advice.

## Required Outputs

For a full financing analysis, provide:

- Executive transaction summary: round size, pre-money, post-money, price/share, new investor ownership, founder ownership before/after.
- Current issued and fully diluted cap tables.
- Post-conversion, post-pool, and post-financing cap tables.
- Instrument-by-instrument conversion schedule.
- Dilution bridge: existing pool → top-up → convertibles → new money → other adjustments.
- Pro-rata economics where relevant.
- Exit waterfall across low/base/high and material breakpoints.
- Material ambiguities and validation status.

The machine-readable summary must include `pre_money_valuation`, `new_primary_investment`, `post_money_valuation`, `pre_round_fd_ownership`, `post_round_fd_ownership`, `founder_dilution_pct_points`, `new_investor_ownership`, `option_pool_post_round`, `convertible_conversion_summary`, `pro_rata_summary`, `exit_waterfall_summary`, `material_ambiguities`, and `validation_status`.

The master `startup-investment-readiness` skill may rely on results only when `validation_status` is `passed` or `passed_with_explicit_assumptions`.
