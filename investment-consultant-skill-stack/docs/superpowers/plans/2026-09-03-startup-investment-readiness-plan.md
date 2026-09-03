# Startup Investment Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable `startup-investment-readiness` agent skill that routes startup investment engagements through stage-aware analysis, enforces evidence and quality gates, and produces separate founder-facing and investor-facing outputs.

**Architecture:** Keep `SKILL.md` concise and discovery-focused, with heavy methodology in references. Implement deterministic routing and gate evaluation in a dependency-free Python helper so mechanical decisions are testable; the skill body remains responsible for judgment, specialist-skill invocation, and narrative synthesis.

**Tech Stack:** Markdown Agent Skill package, Python 3 standard library, pytest.

**Spec:** `docs/superpowers/specs/2026-09-03-startup-investment-readiness-design.md`

## Global Constraints

- Optimize for Seed to Series A while supporting pre-revenue and later-stage companies through methodology switching.
- Never fabricate missing diligence evidence or silently resolve conflicting inputs.
- Separate startup operating logic from accounting integration.
- Enforce three gates: minimum analyzability, economic coherence, and model reliability.
- Treat DCF as conditional and avoid false precision for very early-stage/pre-revenue companies.
- Keep founder-facing outputs separate from confidential investor-facing decision language.
- Invoke `vc-cap-table-analysis` whenever ownership, dilution, SAFE conversion, option-pool top-up, or investor ownership is material.
- V1 excludes legal opinions, tax structuring, securities-law advice, investor outreach, portfolio monitoring, and fund-level portfolio construction.

---

### Task 1: Routing Engine and Scenario Fixtures

**Files:**
- Create: `skills/startup-investment-readiness/scripts/readiness_router.py`
- Create: `skills/startup-investment-readiness/tests/test_readiness_router.py`
- Create: `skills/startup-investment-readiness/tests/fixtures/pre_revenue_saas.json`
- Create: `skills/startup-investment-readiness/tests/fixtures/early_revenue_saas.json`
- Create: `skills/startup-investment-readiness/tests/fixtures/marketplace.json`
- Create: `skills/startup-investment-readiness/tests/fixtures/services.json`
- Create: `skills/startup-investment-readiness/tests/fixtures/conflicting_data.json`

**Interfaces:**
- Consumes: normalized engagement inputs with `stage`, `business_model`, `analysis_intent`, `available_evidence`, and materiality flags.
- Produces: `route_engagement(payload: dict) -> dict` with `required_skills`, `skipped_methods`, `gates`, `blocked_outputs`, and `warnings`.

- [ ] **Step 1: Write failing routing tests** covering the five fixtures and asserting: pre-revenue SaaS skips authoritative DCF; early-revenue SaaS requests metrics/model/comps/cap-table when material; marketplace requests marketplace metrics and distinguishes GMV/revenue; services avoids SaaS-specific methods; conflicting material evidence blocks final IC recommendation.
- [ ] **Step 2: Run `pytest skills/startup-investment-readiness/tests/test_readiness_router.py -v`** and verify failures occur because `readiness_router` does not exist.
- [ ] **Step 3: Implement minimal `route_engagement()`** with stage/model/intent routing and three gate states using only Python standard library.
- [ ] **Step 4: Run the routing tests** and verify all pass.
- [ ] **Step 5: Refactor constants and validation helpers** while keeping tests green.

### Task 2: Skill Authoring and Reference Contracts

**Files:**
- Create: `skills/startup-investment-readiness/SKILL.md`
- Create: `skills/startup-investment-readiness/references/orchestration.md`
- Create: `skills/startup-investment-readiness/references/evidence-gates.md`
- Create: `skills/startup-investment-readiness/references/output-contracts.md`
- Create: `skills/startup-investment-readiness/tests/test_skill_contract.py`

**Interfaces:**
- Consumes: the approved design spec plus routing-engine outputs.
- Produces: an Agent Skills-compatible package whose `SKILL.md` has valid frontmatter and links to references/scripts by relative path.

- [ ] **Step 1: Write failing contract tests** for required frontmatter, description beginning `Use when`, reference-file existence, explicit quality-gate language, founder/investor separation, dependency-unavailable behavior, and cap-table materiality trigger.
- [ ] **Step 2: Run `pytest skills/startup-investment-readiness/tests/test_skill_contract.py -v`** and verify failure because the skill files do not exist.
- [ ] **Step 3: Write concise `SKILL.md`** containing triggers, core principles, routing entrypoint, specialist dependency rules, and required outputs without duplicating heavy methodology.
- [ ] **Step 4: Write the three references** containing the 13-stage orchestration flow, evidence classifications/gates/red flags, and output/scoring schemas.
- [ ] **Step 5: Run skill-contract and routing tests** and verify all pass.
- [ ] **Step 6: Check `wc -w skills/startup-investment-readiness/SKILL.md`** and keep it under 650 words while preserving discoverability.

### Task 3: Package-Level Verification

**Files:**
- Create: `tests/test_skill_packages.py`
- Create: `README.md`

**Interfaces:**
- Consumes: both custom skill package roots once the cap-table skill exists.
- Produces: repository-level verification that required package files exist and both skills are cross-referenced correctly.

- [ ] **Step 1: Write a repository-level failing test** that expects both skill package directories, required `SKILL.md` files, and the master skill's dependency on `vc-cap-table-analysis`.
- [ ] **Step 2: Run `pytest tests/test_skill_packages.py -v`** and verify it fails until both packages are complete.
- [ ] **Step 3: Add `README.md`** documenting purpose, package layout, how to run tests, and recommended installation/copy workflow without claiming automatic installation occurred.
- [ ] **Step 4: Run the entire test suite with `pytest -q`** and verify clean output.
