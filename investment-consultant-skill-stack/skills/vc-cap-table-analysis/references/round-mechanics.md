# Round Mechanics and Integration Contract

## Baseline normalization

List issued common, preferred as-converted, granted options, unallocated option pool, and unconverted instruments separately. Reconcile share counts and stated ownership to 100%. A mismatch is Gate 1 failure.

## Standard priced round

For pre-money equity value `V_pre` and new primary investment `I`:

- `V_post = V_pre + I`
- New investor ownership before simultaneous pool changes: `I / V_post`
- If pre-money fully diluted shares are `S_pre`, price/share = `V_pre / S_pre`
- New shares = `I / price_per_share`

Secondary proceeds do not increase company primary capital.

## Option-pool top-up

### Pre-money top-up

Expanded unallocated pool is included in pre-money fully diluted capitalization. Existing pre-money holders bear the dilution before new money. If the target is stated as a post-round unallocated percentage, solve the circular share-price effect explicitly; `pre_money_pool_topup()` implements the tested algebra.

### Post-money top-up

Create/top up the pool after the financing. Dilution is shared by post-money holders. `post_money_pool_topup()` solves the target percentage directly.

Always state whether the target refers to unallocated pool, total authorized pool, or granted + unallocated pool.

## Pro-rata

Define the ownership measurement basis: before/after SAFE conversion and before/after pool adjustment. For ownership `p` and other investors contributing `O`, the investment required to maintain ownership on that basis is `p × O / (1-p)`.

## Validation

Hard failures include ownership not totaling 100%, negative shares/ownership, contradictory valuation/round inputs, broken share roll-forwards, or exit proceeds not reconciling to distributable equity value.

Warnings include percentages without share counts, ambiguous SAFE capitalization, ambiguous pool target, secondary proceeds treated as primary, and pre/post-money labeling inconsistent with ownership math.

## Master-skill summary contract

Return at minimum:

- `pre_money_valuation`
- `new_primary_investment`
- `post_money_valuation`
- `pre_round_fd_ownership`
- `post_round_fd_ownership`
- `founder_dilution_pct_points`
- `new_investor_ownership`
- `option_pool_post_round`
- `convertible_conversion_summary`
- `pro_rata_summary`
- `exit_waterfall_summary`
- `material_ambiguities`
- `validation_status`

Allowed reliance states: `passed`, `passed_with_explicit_assumptions`, `failed`.
