---
name: startup-investment-readiness
description: Use when assessing a startup for investment readiness, investor screening, valuation, due diligence, financial-model rebuild, round economics, or an investment committee recommendation.
---

# Startup Investment Readiness

## Overview

Orchestrate startup investment analysis without collapsing commercial, financial, ownership, diligence, and decision work into one undifferentiated review. Evidence quality and stage determine which methods are valid.

## Start Here

Normalize the engagement into: company stage, business model, analysis intent, available evidence, ownership materiality, spreadsheet-model availability, long-term cash-flow evidence, and known evidence conflicts.

For structured inputs, use `scripts/readiness_router.py` to generate the mechanical route. Then apply judgment using `references/orchestration.md`.

## Required Principles

- Evidence before conclusion. Missing evidence is a gap, not a fact.
- Do not choose silently between conflicting sources. Show the conflict, working assumption if one is necessary, and the reconciliation question.
- Separate operating drivers from accounting integration: startup model first, 3-statement model second.
- Avoid false precision. DCF is conditional, especially for pre-revenue and very early-stage companies.
- Audit spreadsheet models before relying on them for valuation or returns.
- Keep founder-facing remediation separate from investor-facing confidential recommendation language.

## Specialist Dependencies

Prefer these skills when installed:

- Commercial: `market-sizing-analysis`, `startup-metrics-framework`, `unit-economics`, `startup-financial-modeling`
- Financial/valuation: `3-statement-model`, `dcf-model`, `comps-analysis`, `audit-xls`
- Diligence/decision: `datapack-builder`, `dd-checklist`, `dd-meeting-prep`, `returns-analysis`, `ic-memo`
- Ownership: `vc-cap-table-analysis`

If a required dependency is unavailable, state which capability is unavailable and which downstream output is blocked. Use a documented fallback only where one is defined. Never claim a specialist skill ran when it did not.

Whenever ownership, dilution, SAFE/note conversion, option-pool top-up, investor ownership, or exit ownership economics are material, require `vc-cap-table-analysis` before relying on round economics.

## Quality Gates

The workflow has three mandatory gates:

1. **Minimum analyzability** — stage, business model, revenue logic, and capital ask are sufficiently known.
2. **Economic coherence** — unit economics are viable, conditionally viable, need improvement, or are inconsistent/insufficient.
3. **Model reliability** — spreadsheet model passed, passed with non-material warnings, or failed.

A material evidence conflict creates an additional reconciliation failure and can block `ic-memo`.

Read `references/evidence-gates.md` before making a final recommendation.

## Routing and Outputs

Use `references/orchestration.md` for the stage-by-stage sequence and methodology switching. Use `references/output-contracts.md` for readiness scoring, founder-facing outputs, investor-facing outputs, decision states, and final report structure.

Decision states are: `INVEST`, `INVEST WITH CONDITIONS`, `PASS`, or `INSUFFICIENT EVIDENCE`. Do not convert insufficient evidence into pass unless the missing evidence is itself a material diligence failure.
