# Orchestration Reference

## Intake dimensions

Classify:

- Stage: idea/pre-launch; launched/pre-revenue; early revenue; scaling; mature/growth.
- Business model: SaaS/subscription; marketplace; transactional; e-commerce; services; hardware/asset-heavy; hybrid.
- Intent: founder readiness; investor screening; full DD; valuation only; model rebuild; IC recommendation.
- Evidence quality: A audited/verifiable; B management reporting with support; C unsupported founder-provided; D analyst assumption/external benchmark.

## Sequence

### 1. Deal intake and screening
Create stage, sector, geography, model, traction, capital raised, current raise, use of funds, valuation expectation, and known red flags. Gate: minimum analyzability.

### 2. Market and commercial
Use `market-sizing-analysis` when market size matters. Require TAM/SAM/SOM with methodology, assumptions, growth drivers, and competitive framing. Reject unsupported “small percentage of a huge market” SOM logic.

### 3. Startup metrics
Use `startup-metrics-framework` with business-model-specific metrics. SaaS: ARR/MRR, churn, NRR, CAC/LTV/payback, gross margin, burn multiple. Marketplace: GMV, revenue, take rate, liquidity, repeat, contribution margin. Services: utilization, gross margin, revenue/FTE, repeat revenue, pipeline conversion, delivery capacity.

### 4. Unit economics
Use `unit-economics` when applicable. Recompute metrics from source data where possible and distinguish reported from recomputed values. Gate: economic coherence.

### 5. Startup financial model
Use `startup-financial-modeling` before accounting integration. Forecast hierarchy: operating drivers → customers/cohorts/volume → pricing → revenue → direct costs → opex → headcount → capex/NWC → cash/runway → scenarios. Base and Downside are required; Upside requires evidence.

### 6. 3-statement integration
Use `3-statement-model` when formal statements are required. Check IS/BS/CF links, cash roll-forward, debt, fixed assets/depreciation, working capital, and balance-sheet balance.

### 7. Valuation and round economics
Use `comps-analysis` when a defensible peer set exists. Use `dcf-model` only when long-range cash flows are meaningful; state low reliability for early-stage forecasts. Use `vc-cap-table-analysis` whenever ownership economics are material. Prefer a defensible range and sensitivities over false point precision.

### 8. Model audit
Use `audit-xls`. Gate: model reliability. A failed model cannot be the primary basis for valuation or IC returns without explicit remediation/caveat.

### 9. Data normalization
Use `datapack-builder` when evidence is fragmented. Normalize historical financials, forecast, KPIs, capital structure, ownership, market data, DD status, and source references.

### 10. Due diligence
Use `dd-checklist`: commercial, financial, product/technology, legal/corporate, team/HR, regulatory, tax/cyber/data where relevant. Status each item Verified, Satisfactory but unverified, Open, Red flag, or N/A.

### 11. Management meeting
Use `dd-meeting-prep` after preliminary analysis. Prioritize contradictions, failed metric recomputations, unsupported forecast assumptions, concentration/dependency, ownership/legal ambiguity, and downside resilience.

### 12. Returns
For investor-side work use `returns-analysis`: entry valuation, investment amount, ownership, future dilution, exit timing, exit case, exit multiple/method. Output investor proceeds, MOIC, IRR, Bear/Base/Bull, and sensitivities.

### 13. IC memo
Use `ic-memo` only after material gates are complete or explicitly waived. Final state: INVEST, INVEST WITH CONDITIONS, PASS, or INSUFFICIENT EVIDENCE.

## Methodology cautions

- Pre-revenue: retention/churn may be not yet meaningful rather than bad.
- Marketplace: GMV is not revenue; take rate links the two.
- Services: do not import SaaS multiples or metrics mechanically.
- DCF: absence of reliable long-term cash-flow evidence is a reason to skip or de-emphasize it, not to manufacture assumptions.
