# Investment Consultant Skill Stack

Two custom Agent Skills for startup investment-readiness and VC transaction analysis.

## Packages

### `startup-investment-readiness`

Master orchestration skill for startup screening, market/metrics analysis, unit economics, financial modeling, valuation, model audit, diligence, returns analysis, and IC recommendation. It routes to specialist skills when available and enforces evidence/quality gates before final outputs.

### `vc-cap-table-analysis`

Specialist skill plus tested Decimal-based calculation engine for fully diluted ownership, priced rounds, pre/post-money option-pool top-ups, SAFEs, convertible notes, pro-rata, anti-dilution illustrations, seniority, participating/non-participating liquidation preferences, participation caps, and exit waterfalls.

## Local installation

Cross-runtime Agent Skills location:

```bash
mkdir -p ~/.agents/skills
cp -R skills/startup-investment-readiness ~/.agents/skills/
cp -R skills/vc-cap-table-analysis ~/.agents/skills/
```

Claude Code can alternatively use `~/.claude/skills/`.

These custom skills reference external specialist skills such as `market-sizing-analysis`, `startup-financial-modeling`, `comps-analysis`, `audit-xls`, `dd-checklist`, `returns-analysis`, and `ic-memo`. The master skill is designed to identify unavailable dependencies rather than pretend they ran.

## Verification

From the repository root:

```bash
pytest -q
python -m compileall -q skills
```

The tests cover stage/business-model routing, all quality gates, ownership reconciliation, priced rounds, option-pool timing, multiple SAFE mechanics, convertible notes, pro-rata, anti-dilution, participating and non-participating waterfalls, participation caps, senior/junior priority, and package contracts.

## Package layout

```text
skills/
  startup-investment-readiness/
    SKILL.md
    references/
    scripts/readiness_router.py
    tests/
  vc-cap-table-analysis/
    SKILL.md
    references/
    scripts/cap_table.py
    tests/
```

## Important scope boundary

`vc-cap-table-analysis` is an economic modeling skill. It does not provide jurisdiction-specific legal, tax, securities-law, 409A, or enforceability opinions. Contract definitions that materially alter economics must be supplied or modeled as explicit scenarios.
