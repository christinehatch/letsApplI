# Phase 5.5 — LLM Shadow Mode (Design Specification)

## Purpose

Phase 5.5 introduces **LLM Shadow Mode**, a strictly non-user-visible execution path where an LLM is allowed to run **in parallel** with deterministic logic, but **its output is never surfaced, persisted, or acted upon**.

This phase exists to:
- Validate prompt structure and constraint compliance
- Test language guardrails under real LLM behavior
- Measure divergence between deterministic logic and LLM suggestions
- Surface failure modes safely, before any user exposure

Shadow Mode is a **diagnostic phase**, not a feature.

---

## Core Invariants (Design Lock)

The following invariants must hold at all times:

1. **No user-visible output**
   - LLM responses must never appear in CLI output, markdown, UI, or logs intended for users.

2. **No persistence**
   - LLM outputs are not written to disk, state, memory, cache, or analytics stores.

3. **No authority**
   - LLM output cannot influence ranking, classification, gap detection, or recommendations.

4. **No autonomy**
   - LLMs do not make decisions, only generate candidate language.

5. **No silent fallback**
   - If the LLM fails, times out, or violates constraints, the system continues deterministically.

6. **Explicit execution**
   - Shadow Mode must be enabled via an explicit flag (e.g. `--shadow-llm`).
   - Default behavior is **LLM off**.

---

## Position in the System

LLM Shadow Mode runs **after** deterministic processing and **before** output generation.

Job + Resume Input
        ↓
Deterministic Gap Surfacing (Phase 5.1)
        ↓
Evidence Classification (Phase 5.2)
        ↓
Language Guardrails Applied (Phase 5.3)
        ↓
──────── Shadow Mode Boundary ────────
        ↓
LLM Generates Candidate Wording (discarded)
        ↓
──────── End Shadow Mode ─────────────
        ↓
Deterministic Output Rendered


At no point does LLM output cross back over the boundary.

---

## What the LLM Is Allowed to Do

In Shadow Mode, the LLM **may**:

- Rephrase already-identified gaps using constrained language
- Attempt to summarize job requirements using provided text only
- Generate example phrasing for evidence descriptions
- Reveal where prompts are ambiguous or unsafe
- Surface hallucination tendencies under constraint pressure

---

## What the LLM Is Explicitly Not Allowed to Do

The LLM **must not**:

- Introduce new gaps or skills
- Infer user ability, seniority, or readiness
- Recommend jobs or career paths
- Suggest actions (apply, study, pivot, etc.)
- Store or recall any user data
- Override deterministic classifications

---

## Prompt Constraints (Hard Rules)

All Shadow Mode prompts must:

- Be fully self-contained (no memory, no context carryover)
- Use only user-provided job and resume text
- Include explicit prohibitions against inference
- Avoid evaluative language (“good fit”, “qualified”, “strong candidate”)

**Illustrative constraint block:**

> You may only rephrase content already present.  
> Do not infer missing skills.  
> Do not assess readiness or suitability.  
> Output is discarded and for system evaluation only.

---

## Outputs (Internal Only)

Allowed internal uses of LLM output:

- Manual inspection during development
- Diffing against deterministic phrasing
- Identifying unsafe language patterns
- Prompt refinement

Disallowed uses:

- Logging to user-accessible files
- Storing in versioned artifacts
- Feeding into later system stages

---

## Failure Handling

If the LLM:
- Times out
- Returns malformed output
- Violates guardrails
- Hallucinates content

Then:
- The output is discarded
- The system proceeds normally
- No retry logic is required
- No error is surfaced to the user

Shadow Mode failures are **non-events** from the user’s perspective.

---

## Relationship to Phase 6 (Explicitly Deferred)

Phase 5.5 does **not**:
- Introduce user-visible AI output
- Add consent flows
- Add memory
- Enable recommendations

Those concerns belong to **Phase 6+**, which must be explicitly designed and locked before any exposure.

---

## Completion Criteria

Phase 5.5 is considered complete when:

- Shadow Mode can be toggled on/off explicitly
- LLM executes without affecting output
- Guardrail violations are observable during development
- Deterministic behavior is unchanged with Shadow Mode enabled
- No new persistence paths are introduced

---

## Status

**Design-only phase. No user-facing code implied.**


