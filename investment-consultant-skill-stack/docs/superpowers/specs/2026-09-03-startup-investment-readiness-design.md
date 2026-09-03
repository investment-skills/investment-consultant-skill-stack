# Startup Investment Readiness — Design Specification

**Date:** 2026-09-03
**Status:** Approved / Implemented
**Skill name:** `startup-investment-readiness`

## 1. Purpose

Build a master orchestration skill for startup investment-readiness and VC-style diligence. The skill does not replace specialist analytical skills. Its job is to classify the company and transaction, decide which specialist skill to invoke, enforce evidence and quality gates, reconcile conflicting outputs, and produce an investment-ready conclusion.

The intended end-to-end decision flow is:

`Deal Intake → Screening → Market → Metrics → Unit Economics → Financial Model → Valuation → Model Audit → Data Pack → Due Diligence → Management Questions → Returns → IC Memo → Invest / Conditional / Pass`

## 2. Primary Users

- Investment consultants and advisors
- VC / CVC analysts and associates
- Accelerator or venture-studio investment teams
- Founders preparing for institutional capital

The skill is optimized for Seed to Series A startups, but supports pre-revenue and later-stage companies by switching methodologies rather than forcing irrelevant metrics.

## 3. Design Principles

1. **Evidence before conclusion.** Never produce an investment recommendation from a pitch deck alone when supporting files are available or required.
2. **Stage-aware analysis.** Pre-revenue startups are not assessed using the same KPI expectations as scaling SaaS companies.
3. **Methodology transparency.** Every major output states the source data, methodology, assumptions, and unresolved gaps.
4. **No silent hardcoding.** Forecast assumptions must be explicitly classified as historical-derived, founder-provided, external benchmark, or analyst assumption.
5. **Separate business logic from accounting logic.** Startup operating drivers are modeled before 3-statement accounting integration.
6. **Audit before reliance.** No model is treated as final until integrity checks pass.
7. **Investment decision ≠ fundraising advice.** Founder-facing readiness outputs are separated from investor-facing decision outputs.
8. **No fabricated diligence.** Missing evidence is reported as a gap, not inferred as fact.

## 4. Specialist Skill Dependencies

The orchestrator should prefer the following specialist skills when installed:

### Startup / Commercial
- `market-sizing-analysis`
- `startup-metrics-framework`
- `unit-economics`
- `startup-financial-modeling`

### Financial / Valuation
- `3-statement-model`
- `dcf-model`
- `comps-analysis`
- `audit-xls`

### Due Diligence / Decision
- `datapack-builder`
- `dd-checklist`
- `dd-meeting-prep`
- `returns-analysis`
- `ic-memo`

### Supporting
- `fundraising`
- `general-counsel-advisor`
- `vc-cap-table-analysis` (custom companion skill defined separately)

If a dependency is unavailable, the orchestrator must state the missing capability and either use a documented fallback methodology or stop that branch of analysis rather than pretending the specialist result exists.

## 5. Input Contract

The skill accepts any subset of the following, then builds a coverage map:

### Company data
- Company name
- Sector / business model
- Geography
- Stage
- Founding date
- Team
- Product status

### Commercial data
- Revenue history
- Customer count
- Pricing
- Sales pipeline
- Cohort / retention data
- Acquisition channels
- CAC / marketing spend
- Usage / transaction volume

### Financial data
- Historical P&L
- Balance sheet
- Cash flow
- Bank/cash balance
- Debt
- Payroll
- CapEx
- Existing financial model

### Fundraising / ownership data
- Current cap table
- Prior rounds
- SAFEs / convertible notes
- Option pool
- Current round ask
- Proposed valuation
- Target ownership / dilution

### Diligence materials
- Pitch deck
- Data room index
- Material contracts
- IP evidence
- Customer concentration
- Legal / regulatory documents
- Market studies

## 6. Intake Classification

The orchestrator first classifies four dimensions:

### 6.1 Company stage
- Idea / pre-launch
- Launched / pre-revenue
- Early revenue
- Scaling
- Mature / growth stage

### 6.2 Business model
- SaaS / subscription
- Marketplace
- Transactional
- E-commerce
- Services
- Hardware / asset-heavy
- Hybrid

### 6.3 Analysis intent
- Founder investment readiness
- Investor screening
- Full due diligence
- Valuation only
- Financial-model rebuild
- IC recommendation

### 6.4 Evidence quality
- A: Audited / independently verifiable
- B: Management reporting with source support
- C: Founder-provided unsupported data
- D: Analyst assumption / external benchmark

Every material metric in the final analysis should carry an evidence class when practical.

## 7. Orchestration Flow

### Stage 1 — Deal Intake and Screening

Create a concise deal snapshot:
- Stage
- Sector
- Geography
- Business model
- Traction
- Capital raised
- Current raise
- Use of funds
- Current valuation expectation
- Major known red flags

**Gate 1 — Minimum analyzability**
Proceed only if enough information exists to identify the business model, stage, core revenue logic, and capital ask. Missing items become explicit diligence requests.

### Stage 2 — Market and Commercial Validation

Invoke `market-sizing-analysis` when market sizing materially affects the investment case.

Required output:
- TAM
- SAM
- SOM
- Methodology per layer
- Key assumptions
- Market growth / structural drivers
- Competitive framing

Reject unsupported “X% of a huge market” logic as a valid SOM methodology.

### Stage 3 — Startup Metrics

Invoke `startup-metrics-framework` using stage-appropriate metrics.

Examples:
- SaaS: ARR/MRR, growth, logo churn, revenue churn, NRR, CAC, LTV, payback, burn multiple
- Marketplace: GMV, take rate, liquidity, repeat rate, contribution margin, buyer/seller retention
- Services: utilization, gross margin, revenue per delivery FTE, repeat revenue, pipeline conversion

The orchestrator must distinguish reported metrics from independently recomputed metrics.

### Stage 4 — Unit Economics

Invoke `unit-economics`.

Required outputs when applicable:
- Revenue per customer/order/unit
- Variable cost per customer/order/unit
- Contribution margin
- CAC
- LTV
- LTV/CAC
- CAC payback
- Retention/churn linkage

**Gate 2 — Economic coherence**
Classify unit economics as:
- Viable
- Viable with scaling dependency
- Needs improvement
- Economically inconsistent / insufficient data

### Stage 5 — Startup Financial Model

Invoke `startup-financial-modeling` before 3-statement modeling.

Forecast hierarchy:
1. Operational drivers
2. Customer / cohort / volume build
3. Pricing / monetization
4. Revenue
5. Direct costs
6. Operating expenses
7. Headcount
8. CapEx / working capital drivers
9. Cash and runway
10. Scenarios

Scenarios must include at least Base and Downside; Upside is optional when unsupported.

### Stage 6 — 3-Statement Integration

Invoke `3-statement-model` when accounting statements are required.

Required model integrity:
- IS → BS → CF linkages
- Cash roll-forward
- Debt roll-forward if relevant
- Fixed asset / depreciation roll-forward if relevant
- Working capital logic
- Balance sheet balances

### Stage 7 — Valuation

Use valuation methods conditionally:

#### Comps
Invoke `comps-analysis` when a defensible peer set exists.

#### DCF
Invoke `dcf-model` only when long-term cash-flow assumptions are sufficiently meaningful. For very early-stage/pre-revenue companies, DCF must not be presented as inherently precise.

#### Cap-table / round economics
Invoke `vc-cap-table-analysis` whenever ownership, dilution, SAFE conversion, option-pool top-up, or investor ownership is material.

Required final output:
- Valuation methods used
- Why each method is or is not appropriate
- Implied ranges
- Key sensitivities
- Defensible reference range rather than false point precision

### Stage 8 — Model Audit

Invoke `audit-xls` for spreadsheet-based models.

**Gate 3 — Model reliability**
A model may be marked:
- Passed
- Passed with non-material warnings
- Failed — remediation required

A failed model cannot be used as the primary basis for valuation or IC returns without explicit caveat and remediation.

### Stage 9 — Data Pack Normalization

Invoke `datapack-builder` when multiple files or fragmented sources exist.

Create a single normalized evidence pack containing:
- Historical financials
- Forecast
- KPI history
- Capital structure
- Ownership
- Market data
- Diligence status
- Source references

### Stage 10 — Due Diligence

Invoke `dd-checklist`.

Coverage:
- Commercial
- Financial
- Product / technology
- Legal / corporate
- Team / HR
- Regulatory
- Tax where relevant
- Cyber / data where relevant

Each diligence item has status:
- Verified
- Satisfactory but unverified
- Open
- Red flag
- Not applicable

### Stage 11 — Management Meeting Prep

Invoke `dd-meeting-prep` after preliminary analysis so questions are evidence-driven.

Question priority:
1. Contradictions between files
2. Metrics that fail recomputation
3. Unsupported forecast assumptions
4. Concentration / dependency risks
5. Legal / ownership ambiguity
6. Downside resilience

### Stage 12 — Returns Analysis

Invoke `returns-analysis` for investor-side engagements.

Required inputs:
- Entry valuation
- Investment amount
- Ownership
- Future dilution assumption
- Exit timing
- Exit operating case
- Exit multiple / valuation method

Required outputs:
- Investor proceeds
- MOIC
- IRR
- Bear / Base / Bull scenarios
- Key return sensitivities

### Stage 13 — IC Memo / Recommendation

Invoke `ic-memo` only after the material gates above are complete or explicitly waived.

Decision states:
- INVEST
- INVEST WITH CONDITIONS
- PASS
- INSUFFICIENT EVIDENCE

The orchestrator may not convert “insufficient evidence” into “pass” unless the missing evidence itself is a material diligence failure.

## 8. Founder-Facing vs Investor-Facing Outputs

### Founder-facing
- Investment Readiness Diagnostic
- Readiness score by workstream
- Financial model gap analysis
- Data room gap list
- Valuation preparedness
- Prioritized remediation roadmap

### Investor-facing
- Deal screen
- Diligence tracker
- Investment thesis
- Risk register
- Valuation analysis
- Returns analysis
- IC memo

Do not disclose internal investor scoring or recommendation language in founder-facing deliverables unless explicitly requested.

## 9. Scoring Framework

Optional readiness score out of 100:

- Market & positioning: 15
- Traction & commercial quality: 15
- Unit economics: 15
- Financial quality & forecast: 20
- Ownership / round structure: 10
- Data room / diligence readiness: 15
- Team / governance / execution: 10

Scores must not substitute for narrative reasoning. Any red-flag override can cap the overall status regardless of arithmetic score.

## 10. Red-Flag Overrides

Examples that can override an otherwise strong score:
- Unreconciled ownership
- Material undisclosed liabilities
- Fabricated or irreconcilable customer/revenue metrics
- Critical IP ownership gap
- Severe customer concentration with no mitigation
- Model cash balance inconsistent with actual liquidity
- Regulatory prohibition or unresolved licensing dependency
- Founder-provided financials materially inconsistent across documents

## 11. Error Handling

### Missing inputs
Return:
- What is missing
- Why it matters
- Which downstream analyses are blocked
- Minimum acceptable substitute data

### Conflicting inputs
Do not choose silently. Show:
- Source A
- Source B
- Difference
- Current working assumption
- Required reconciliation question

### Unsupported specialist skill
State that the specialist capability is unavailable and use only the fallback explicitly defined in the orchestrator. Never claim the specialist ran.

### Non-applicable methodology
Explicitly skip it with rationale. Example: “DCF not relied upon due to pre-revenue status and insufficient evidence for long-range cash-flow assumptions.”

## 12. Output Schema

Every full engagement should be able to produce:

1. Executive Summary
2. Company & Deal Snapshot
3. Evidence Coverage Map
4. Market Assessment
5. Traction & KPI Analysis
6. Unit Economics
7. Historical Financial Analysis
8. Forecast & Scenario Analysis
9. Valuation
10. Ownership / Round Impact
11. Due Diligence Findings
12. Risk Register
13. Returns Analysis (investor-side)
14. Recommendation
15. Conditions / Required Actions
16. Appendices / Source Map

## 13. Testing Strategy

The skill must be tested using scenario fixtures rather than only prose review.

### Fixture A — Pre-revenue SaaS
Expected behavior:
- Avoid false precision in DCF
- Focus on runway, pricing logic, market, product evidence, milestone financing
- Mark missing retention metrics as not yet meaningful rather than “bad”

### Fixture B — Early-revenue SaaS
Expected behavior:
- Recompute CAC/LTV where source data permits
- Build cohort-based revenue forecast
- Perform comps and round-dilution analysis

### Fixture C — Marketplace
Expected behavior:
- Distinguish GMV from revenue
- Analyze take rate, repeat rate, liquidity and contribution margin

### Fixture D — Services business
Expected behavior:
- Avoid applying SaaS multiples/metrics mechanically
- Use utilization, gross margin, pipeline, repeat revenue and delivery capacity

### Fixture E — Conflicting founder data
Expected behavior:
- Identify contradictions
- Block final IC recommendation until material issues are reconciled or explicitly risk-rated

## 14. Acceptance Criteria

The skill is acceptable when it can:
- Route at least five startup archetypes to different analytical paths
- Distinguish missing data from negative performance
- Enforce all three quality gates
- Prevent inappropriate valuation methods from appearing authoritative
- Reconcile conflicting evidence explicitly
- Produce founder-facing and investor-facing outputs without mixing confidential decision language
- Invoke cap-table analysis whenever ownership economics are material
- Produce an IC recommendation only after material diligence coverage or explicit waiver

## 15. Out of Scope for V1

- Automated legal opinions
- Tax structuring opinions
- Securities-law compliance advice
- Automated investor outreach
- Portfolio monitoring after investment
- Fund-level portfolio construction

These can be added as separate skills later.
