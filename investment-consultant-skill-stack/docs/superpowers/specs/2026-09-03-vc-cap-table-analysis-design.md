# VC Cap Table Analysis — Design Specification

**Date:** 2026-09-03
**Status:** Approved / Implemented
**Skill name:** `vc-cap-table-analysis`

## 1. Purpose

Build a specialist VC cap-table and financing-round analysis skill that converts ownership, securities, and round terms into transparent pre-money and post-money ownership outcomes. It must support common early-stage financing mechanics without presenting legal conclusions.

Core analytical flow:

`Current Cap Table → Fully Diluted Baseline → Convertible/SAFE Conversion → Option Pool Top-Up → New Money → Post-Round Ownership → Dilution → Pro-Rata → Down-Round Adjustments → Exit Waterfall`

## 2. Primary Use Cases

- Analyze founder dilution before a financing round
- Calculate investor ownership from pre-money/post-money valuation
- Model option-pool top-ups
- Convert SAFEs and convertible notes
- Compare financing scenarios
- Analyze pro-rata rights economically
- Model broad-based weighted-average or full-ratchet anti-dilution when explicitly supplied
- Build exit proceeds waterfalls including liquidation preferences
- Feed ownership/returns outputs into `startup-investment-readiness` and `returns-analysis`

## 3. Principles

1. **Cap table must balance to 100%.**
2. **Security terms are inputs, not legal interpretations.**
3. **Pre-money and post-money mechanics must never be mixed silently.**
4. **Option-pool timing must be explicit because it changes who bears dilution.**
5. **SAFE method must be identified explicitly.**
6. **Conversion sequencing must be documented.**
7. **Rounding must not create ownership drift.** Internal calculations use high precision; displayed percentages may be rounded.
8. **Every scenario must show both shares/units and percentages when share counts are available.**

## 4. Input Schema

### 4.1 Existing holders
For each holder:
- Name / holder ID
- Holder type: founder / employee / investor / advisor / ESOP
- Security type
- Issued shares or units
- Vested shares if relevant
- Unvested shares if relevant

### 4.2 Existing option pool
- Authorized pool
- Granted options
- Unallocated options
- Whether included in fully diluted pre-money capitalization

### 4.3 SAFEs
For each SAFE:
- Investment amount
- Valuation cap
- Discount rate
- SAFE type: pre-money / post-money
- MFN flag if economically relevant
- Pro-rata side letter if provided

### 4.4 Convertible notes
For each note:
- Principal
- Accrued interest or interest rate + conversion date
- Valuation cap
- Discount
- Maturity treatment if relevant

### 4.5 New round
- New investment amount
- Pre-money valuation or post-money valuation
- Price per share if directly specified
- Target investor ownership if specified
- Option-pool target after financing
- Primary vs secondary allocation

### 4.6 Rights affecting economics
- Pro-rata
- Liquidation preference multiple
- Participating / non-participating
- Participation cap if any
- Seniority / pari passu
- Anti-dilution type and required variables

## 5. Baseline Normalization

Before any transaction calculations:

1. List all issued securities.
2. Convert the current cap table into a common fully diluted basis.
3. Separate:
   - Issued common
   - Preferred as-converted
   - Granted options
   - Unallocated pool
   - Convertible instruments not yet converted
4. Report any mismatch against management’s stated ownership.

**Gate 1 — Ownership reconciliation**
If the supplied percentages and share counts cannot reconcile to the same capitalization, stop transaction modeling until a working assumption is explicitly selected.

## 6. Standard Equity Round

Given:
- Pre-money equity value = `V_pre`
- New primary investment = `I`

Then:
- Post-money equity value = `V_post = V_pre + I`
- New investor ownership before simultaneous pool adjustments = `I / V_post`

When share count is available:
- Pre-money fully diluted shares = `S_pre`
- Price per share = `V_pre / S_pre`
- New shares issued = `I / price_per_share`

The skill must show whether any option-pool increase is included inside `S_pre` before computing the financing price.

## 7. Option Pool Top-Up

Support two explicit conventions:

### 7.1 Pre-money pool top-up
The new/expanded unallocated pool is included in pre-money fully diluted capitalization. Existing holders bear the dilution before new money enters.

### 7.2 Post-money pool creation
The pool is created after the financing and dilution is shared according to post-financing ownership.

The skill must calculate the required additional pool shares iteratively/algebraically so that the **unallocated pool** equals the requested target percentage after the relevant transaction step.

Required output:
- Existing pool
- Granted options
- Unallocated pool before round
- Additional pool required
- Founder dilution attributable to pool top-up
- Investor dilution attributable to pool top-up if post-money

## 8. SAFE Conversion

### 8.1 Pre-money SAFE
For each pre-money SAFE, calculate the conversion price under the governing economic terms supplied:
- Valuation-cap price
- Discount price
- Applicable conversion price according to the instrument terms provided

The denominator must reflect the capitalization definition provided in the SAFE. If the definition is not supplied and materially changes the result, mark the output as scenario-based rather than definitive.

### 8.2 Post-money SAFE
Model the SAFE so the holder’s ownership before the new priced-round money reflects the post-money SAFE mechanics implied by the supplied cap/terms.

When multiple SAFEs exist, show:
- SAFE amount
- Effective conversion price
- Shares issued
- Ownership immediately after conversion
- Ownership after new financing

Do not collapse multiple SAFEs into one blended instrument when terms differ.

## 9. Convertible Note Conversion

Calculate:
- Principal at conversion
- Accrued interest if applicable
- Cap-based price
- Discount-based price
- Applicable conversion price based on supplied note terms
- Conversion shares

If maturity treatment, interest conversion, or cap table definition is ambiguous, create explicit scenarios rather than infer legal treatment.

## 10. Pro-Rata Analysis

For an existing investor with ownership `p` before a new financing, calculate the primary investment required to maintain ownership under the defined basis.

Outputs:
- Current ownership
- Ownership without participation
- Required pro-rata investment
- Ownership with full pro-rata
- Optional partial-pro-rata scenarios

The basis must specify whether ownership is measured before or after SAFE conversion and option-pool adjustment.

## 11. Anti-Dilution Modeling

Only model anti-dilution when the contractual formula/definitions are provided or the user explicitly selects a standard scenario for illustration.

Supported V1 scenarios:
- Full ratchet
- Broad-based weighted average

Required output:
- Original conversion price
- New issuance price
- Adjusted conversion price
- Incremental as-converted shares
- Ownership shift by stakeholder class

The skill must label this as an **economic model**, not legal interpretation.

## 12. Exit Waterfall

Support:
- Common shareholders
- Non-participating preferred
- Participating preferred
- Participation caps
- Multiple liquidation preferences
- Senior / junior / pari passu stacks when supplied

For each exit value:
1. Calculate preference entitlement.
2. Calculate as-converted common value.
3. For non-participating preferred, select the economically superior of preference vs conversion.
4. For participating preferred, allocate preference then participation according to supplied terms and cap.
5. Allocate residual value.

Required scenario table:
- Low exit
- Base exit
- High exit
- User-specified breakpoints

Outputs by investor / class:
- Cash proceeds
- Ownership reference
- MOIC when invested capital is supplied
- Conversion election where applicable

## 13. Scenario Comparison

The skill must support side-by-side scenarios such as:

- $4M pre-money vs $5M pre-money
- 10% vs 15% post-round option pool
- SAFE conversion vs no SAFE
- Investor takes pro-rata vs does not
- Different round sizes
- Different exit values

Each scenario reports:
- Founder ownership
- Employee / pool ownership
- Existing investor ownership
- SAFE/note holder ownership
- New investor ownership
- Total dilution
- Ownership delta vs baseline

## 14. Validation Rules

Hard validations:
- Ownership totals equal 100% within tolerance
- Share totals reconcile across transaction steps
- No negative share count
- No negative ownership
- Investment amount and valuation are not contradictory
- Pre-money + primary investment = post-money when using standard equity financing
- Exit proceeds equal total equity value distributed

Warnings:
- Percentages supplied without share counts
- Missing capitalization definition for SAFE/note
- Option-pool target ambiguous as granted vs total vs unallocated
- Secondary proceeds incorrectly included as company primary capital
- Valuation labeled “post-money” but ownership math implies pre-money

## 15. Output Schema

### 15.1 Executive transaction summary
- Round size
- Pre-money
- Post-money
- Price per share
- New investor ownership
- Founder ownership before / after
- Total founder dilution

### 15.2 Cap tables
- Current issued
- Current fully diluted
- Post-conversion
- Post-pool adjustment
- Post-financing fully diluted

### 15.3 Instrument conversion schedule
- SAFE/note-by-note details

### 15.4 Dilution bridge
Show the ownership impact from:
1. Existing pool
2. New pool top-up
3. Convertible conversion
4. New money
5. Other adjustments

### 15.5 Exit waterfall
Stakeholder proceeds across exit scenarios.

### 15.6 Risks / ambiguities
List every contractual definition that materially affects the math.

## 16. Integration Contract with Master Skill

The skill returns a structured summary containing at minimum:
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

The master `startup-investment-readiness` skill may rely on cap-table outputs only when `validation_status = passed` or `passed_with_explicit_assumptions`.

## 17. Testing Strategy

### Fixture A — Simple priced round
Founders 80%, ESOP 10%, investor 10%; new round at known pre-money valuation.
Expected: exact post-money ownership reconciliation.

### Fixture B — Pre-money option-pool top-up
Pool increased to a target unallocated percentage before financing.
Expected: dilution is borne by pre-money holders.

### Fixture C — Multiple SAFEs
Two SAFEs with different caps/discounts.
Expected: separate conversion prices and ownership outcomes.

### Fixture D — Convertible note
Principal + accrued interest, cap and discount.
Expected: correct economically applicable conversion scenario from supplied terms.

### Fixture E — Pro-rata
Existing investor exercises full pro-rata.
Expected: ownership maintained on the explicitly defined basis.

### Fixture F — Full ratchet down round
Expected: adjusted conversion ratio and incremental preferred as-converted ownership.

### Fixture G — Exit waterfall
One non-participating 1x preferred class plus common.
Expected: preference at low exits and conversion above crossover point.

### Fixture H — Broken cap table
Supplied percentages do not match share counts.
Expected: Gate 1 failure; no definitive financing result.

## 18. Acceptance Criteria

The skill is acceptable when it can:
- Reconcile a fully diluted cap table to 100%
- Model standard priced equity rounds
- Model pre-money and post-money option-pool effects distinctly
- Model multiple SAFEs/notes without blending unlike terms
- Quantify founder dilution by source
- Compute pro-rata economics on an explicit basis
- Model selected anti-dilution scenarios without presenting legal advice
- Produce a balanced exit waterfall
- Return machine-readable summary fields for downstream returns/IC analysis

## 19. Out of Scope for V1

- Jurisdiction-specific legal enforceability
- Tax treatment
- QSBS or equivalent tax eligibility
- Employee vesting administration
- 409A / formal fair-market-value opinions
- Complex tender offers
- SPAC / public-company capital structures
- Waterfalls involving debt covenants or structured credit beyond equity-linked instruments
