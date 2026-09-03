# SAFEs and Convertible Notes

## General rule

Instrument terms are supplied inputs, not inferred legal conclusions. Keep each SAFE/note separate when terms differ.

## Pre-money SAFE

Require: investment, valuation cap if applicable, discount if applicable, priced-round price/share, and the SAFE capitalization definition.

Typical economic comparison:

- Cap price = valuation cap / defined capitalization
- Discount price = priced-round price × (1 − discount)
- Use the economically applicable price under the supplied terms
- Conversion shares = investment / applicable price

If the denominator definition is missing and material, model explicit alternatives.

## Post-money SAFE

SAFE type must be explicit. For a simple post-money valuation-cap illustration, ownership immediately after SAFE conversion is based on the investment relative to the post-money cap under the instrument's capitalization mechanics. Multiple post-money SAFEs can interact; do not claim definitive ownership if the actual instrument definition is unavailable.

The tested helper `convert_safe()` supports a simplified cap/discount economic illustration and returns the method used.

## Convertible notes

Include principal plus accrued interest if the note terms convert interest. Compare cap-based and discount-based prices under the supplied terms and convert using the economically applicable result.

If maturity treatment, interest conversion, or capitalization definition is ambiguous, create scenarios rather than infer legal treatment.

## Required schedule

For each instrument show amount, cap, discount, SAFE/note type, capitalization basis, effective conversion price, shares issued, ownership immediately after conversion, and ownership after new financing where available.
