# Phase 5.5.1 — Prompt Test Harness (Design Specification)

## Purpose

Phase 5.5.1 introduces a **Prompt Test Harness** to systematically evaluate
LLM behavior **before any user-facing exposure**.

This harness exists to:
- Stress-test prompts under strict guardrails
- Detect hallucination, inference drift, and tone violations
- Compare deterministic outputs vs. LLM-generated phrasing
- Make prompt failure modes visible and inspectable
- Enable iteration without changing product behavior

This is an **engineering safety tool**, not a product feature.

---

## Core Invariants (Design Lock)

The following invariants must always hold:

1. **No user-facing output**
   - Harness output is for developers only.
   - Nothing flows into CLI output, markdown feeds, or UI.

2. **No persistence of LLM responses**
   - Generated text is not stored as state, memory, or artifacts.
   - Optional temporary files must be explicitly gitignored.

3. **No behavioral influence**
   - Harness results do not modify rankings, gap detection, or evidence classification.

4. **Deterministic system remains authoritative**
   - Deterministic logic always runs first and defines truth.
   - The harness only observes and compares.

5. **Explicit invocation**
   - Harness runs only when explicitly invoked (e.g. `--test-prompts`).
   - Default system behavior is unchanged.

---

## What the Harness Tests

The harness evaluates **prompt behavior**, not user readiness.

It may test:

- Gap rephrasing prompts
- Evidence wording prompts
- Neutral language compliance
- Constraint-following under ambiguity
- Resistance to inference and evaluation
- Behavior under malformed or edge-case inputs

---

## Inputs

The harness operates on **fixed, explicit inputs**:

- Job posting text (static fixtures)
- Resume text (static fixtures)
- Deterministic gap outputs
- Deterministic evidence classifications
- Prompt templates under test

Inputs must be:
- Human-readable
- Version-controlled
- Explicitly scoped

No live scraping or user data is allowed.

---

## Prompt Execution Model

Each test case runs as:

## Test Case
Test Case
├─ Deterministic Output (source of truth)
├─ Prompt Template
├─ Guardrail Constraints
└─ LLM Invocation (Shadow Mode)


### 1. Deterministic Output (Source of Truth)

This is the **authoritative, non-LLM-generated output** produced by the system’s rule-based logic.

Characteristics:
- Generated without any LLM involvement
- Fully explainable
- Used as the baseline for comparison
- Stored as static test data

Example:
- Identified skill gaps
- Explicit resume-to-job mismatches
- Evidence categories derived from rules

---

### 2. Prompt Template

The exact prompt text passed to the LLM.

Requirements:
- Fully versioned
- Stored as plain text
- No inline logic
- No conditional branching inside the prompt
- Explicitly references the deterministic output

The prompt may:
- Rephrase
- Summarize
- Clarify

The prompt may **not**:
- Introduce new conclusions
- Re-rank items
- Invent missing evidence

---

### 3. Guardrail Constraints

A machine-readable specification of what the LLM is allowed to do.

Examples:
- Allowed verbs (e.g., “rephrase”, “group”, “label”)
- Forbidden behaviors (e.g., “recommend”, “judge”, “predict”)
- Tone constraints (non-evaluative, non-prescriptive)
- Output format constraints

Guardrails are evaluated **outside** the model.

If guardrails fail, output is discarded.

---

### 4. LLM Invocation (Shadow Mode)

The LLM is invoked in **Shadow Mode** only.

Properties:
- Output is not shown to the user
- Output is not persisted as state
- Output is compared against deterministic output
- Differences are logged for inspection

Shadow Mode exists solely for:
- Prompt evaluation
- Drift detection
- Confidence building

---

## Comparison & Evaluation

The harness compares:

- Deterministic Output vs LLM Output
- Structural alignment
- Constraint adherence
- Language compliance (Phase 5.3)

Results are categorized as:
- ✅ Aligned
- ⚠️ Divergent but acceptable
- ❌ Violation (discarded)

No automatic promotion to production is allowed.

---

## Explicit Non-Goals

This phase does **not** include:
- Model selection
- Prompt optimization
- Automatic prompt tuning
- User-facing LLM output
- Performance benchmarking

---

## Exit Criteria

Phase 5.5.1 is complete when:

- Prompt test cases can be run deterministically
- Prompt changes require explicit review
- Shadow Mode output is inspectable
- Guardrail violations are detectable
- No LLM output influences user-visible behavior

---

## Phase Boundary

> **After Phase 5.5.1, LLM prompts are eligible for controlled exposure — but only with explicit consent and invariant enforcement.**

Anything beyond this requires a new phase lock.

