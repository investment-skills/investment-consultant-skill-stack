# VC Cap Table Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable `vc-cap-table-analysis` skill plus deterministic calculation engine for early-stage ownership, dilution, convertible instruments, pro-rata, anti-dilution illustrations, and equity exit waterfalls.

**Architecture:** Keep legal/judgment guidance in `SKILL.md` and references, while implementing arithmetic in a dependency-free Python module using `Decimal` for high precision. Expose small pure functions for priced rounds, pool top-ups, conversions, pro-rata, anti-dilution, reconciliation, and waterfalls so each financing mechanic can be tested independently.

**Tech Stack:** Markdown Agent Skill package, Python 3 standard library (`decimal`, `dataclasses`), pytest.

**Spec:** `docs/superpowers/specs/2026-09-03-vc-cap-table-analysis-design.md`

## Global Constraints

- Cap tables must reconcile to 100% within a documented tolerance before definitive transaction modeling.
- Security terms are economic inputs, not legal interpretations.
- Never mix pre-money and post-money mechanics silently.
- Option-pool timing and SAFE type must be explicit.
- Use high-precision internal arithmetic and round only for display.
- Multiple SAFEs/notes with different terms must remain separate.
- Anti-dilution is modeled only from supplied contractual variables or an explicitly selected illustration.
- Exit proceeds must reconcile to total distributable equity value.
- V1 excludes tax/legal enforceability opinions, 409A/QSBS, tender offers, public-company structures, and credit waterfalls.

---

### Task 1: Baseline Cap Table and Priced-Round Math

**Files:**
- Create: `skills/vc-cap-table-analysis/scripts/cap_table.py`
- Create: `skills/vc-cap-table-analysis/tests/test_priced_round.py`

**Interfaces:**
- Produces: `reconcile_ownership()`, `priced_round()`, and `price_per_share()` using Decimal-safe inputs/outputs.

- [ ] **Step 1: Write failing tests** for Fixture A simple priced round and Fixture H broken cap table, including exact ownership reconciliation and Gate 1 failure.
- [ ] **Step 2: Run `pytest skills/vc-cap-table-analysis/tests/test_priced_round.py -v`** and verify module-not-found failure.
- [ ] **Step 3: Implement minimal baseline and priced-round functions** with tolerance validation.
- [ ] **Step 4: Run tests and verify pass.**

### Task 2: Option Pool, SAFE, Note, and Pro-Rata Mechanics

**Files:**
- Modify: `skills/vc-cap-table-analysis/scripts/cap_table.py`
- Create: `skills/vc-cap-table-analysis/tests/test_convertibles_and_pool.py`

**Interfaces:**
- Produces: `pre_money_pool_topup()`, `post_money_pool_topup()`, `convert_safe()`, `convert_note()`, and `pro_rata_investment()`.

- [ ] **Step 1: Write failing tests** for Fixture B pre-money pool top-up, Fixture C multiple SAFEs with separate terms, Fixture D convertible note with accrued interest and cap/discount alternatives, and Fixture E full pro-rata.
- [ ] **Step 2: Run the new tests** and verify failure because functions are missing.
- [ ] **Step 3: Implement the minimal functions** with explicit assumptions and no legal inference.
- [ ] **Step 4: Run all cap-table tests** and verify pass.
- [ ] **Step 5: Refactor shared Decimal/validation utilities** while remaining green.

### Task 3: Anti-Dilution and Exit Waterfall

**Files:**
- Modify: `skills/vc-cap-table-analysis/scripts/cap_table.py`
- Create: `skills/vc-cap-table-analysis/tests/test_antidilution_and_waterfall.py`

**Interfaces:**
- Produces: `full_ratchet_price()`, `broad_based_weighted_average_price()`, and `non_participating_waterfall()` for V1 economics.

- [ ] **Step 1: Write failing tests** for Fixture F full-ratchet down round and Fixture G 1x non-participating preferred crossover behavior.
- [ ] **Step 2: Run tests** and verify missing-function failures.
- [ ] **Step 3: Implement minimal anti-dilution and waterfall functions** and reconcile total proceeds.
- [ ] **Step 4: Run the full cap-table test suite** and verify pass.

### Task 4: Structured Summary Contract

**Files:**
- Modify: `skills/vc-cap-table-analysis/scripts/cap_table.py`
- Create: `skills/vc-cap-table-analysis/tests/test_summary_contract.py`

**Interfaces:**
- Produces: `build_summary(...) -> dict` with spec fields: `pre_money_valuation`, `new_primary_investment`, `post_money_valuation`, `pre_round_fd_ownership`, `post_round_fd_ownership`, `founder_dilution_pct_points`, `new_investor_ownership`, `option_pool_post_round`, `convertible_conversion_summary`, `pro_rata_summary`, `exit_waterfall_summary`, `material_ambiguities`, `validation_status`.

- [ ] **Step 1: Write failing summary-contract test** requiring all integration fields and rejecting reliance when validation fails.
- [ ] **Step 2: Run test** and verify failure because `build_summary` is missing.
- [ ] **Step 3: Implement `build_summary`** without recomputing mechanics already provided by pure functions.
- [ ] **Step 4: Run all cap-table tests** and verify pass.

### Task 5: Skill Authoring and Methodology References

**Files:**
- Create: `skills/vc-cap-table-analysis/SKILL.md`
- Create: `skills/vc-cap-table-analysis/references/round-mechanics.md`
- Create: `skills/vc-cap-table-analysis/references/convertibles.md`
- Create: `skills/vc-cap-table-analysis/references/anti-dilution-and-waterfalls.md`
- Create: `skills/vc-cap-table-analysis/tests/test_skill_contract.py`

**Interfaces:**
- Consumes: the approved design spec and tested calculation module.
- Produces: discoverable skill guidance that points agents to tested mechanics and explicitly separates economic modeling from legal interpretation.

- [ ] **Step 1: Write failing skill-contract tests** for frontmatter, trigger description, legal disclaimer, explicit pre/post-money distinction, SAFE-type requirement, ownership reconciliation gate, and integration output contract.
- [ ] **Step 2: Run contract test** and verify failure because skill files do not exist.
- [ ] **Step 3: Write concise `SKILL.md`** and split heavy formulas/explanations into the three reference files.
- [ ] **Step 4: Run all skill and arithmetic tests** and verify pass.
- [ ] **Step 5: Check `wc -w skills/vc-cap-table-analysis/SKILL.md`** and keep it under 650 words.
