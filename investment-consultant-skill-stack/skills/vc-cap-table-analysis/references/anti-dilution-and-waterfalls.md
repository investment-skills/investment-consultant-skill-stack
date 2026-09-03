# Anti-Dilution and Exit Waterfalls

## Anti-dilution

Only run when contractual variables are supplied or the user explicitly asks for a standard economic illustration.

### Full ratchet

Economic illustration: adjusted conversion price becomes the lower new issuance price when the triggering conditions are assumed satisfied. Show original price, new issuance price, adjusted price, incremental as-converted shares, and ownership shift.

### Broad-based weighted average

Standard illustration:

`CP2 = CP1 × (A + B) / (A + C)`

where `CP1` is original conversion price, `A` is the defined broad-based fully diluted shares before issuance, `B` is consideration received divided by CP1, and `C` is new shares issued. Contract definitions can alter A/B/C.

## Liquidation preferences

Model the economics of supplied terms:

- Preference multiple
- Participating vs non-participating
- Participation cap
- As-converted ownership
- Seniority tier
- Pari passu treatment within a tier

Convention in `scripts/cap_table.py`: `seniority=1` is most senior; larger integers are junior.

### Non-participating preferred

At each exit value, compare preference proceeds to conversion proceeds. The tested solver enumerates preference/conversion elections and selects an internally consistent set. Preference payments respect seniority; classes in the same tier are pari passu.

### Participating preferred

Pay liquidation preference by seniority first, then allocate residual value on an as-converted basis. If a participation cap applies, stop that class at the cap and reallocate remaining residual to uncapped participants/common.

## Exit scenarios

Show low/base/high exits plus user-specified or economically meaningful crossover points. For each holder/class report cash proceeds, election where applicable, invested capital, and MOIC when investment cost is known.

Every scenario must reconcile total proceeds to total distributable equity value.

These outputs are economic models, not legal opinions on enforceability, drafting, or jurisdiction-specific interpretation.
