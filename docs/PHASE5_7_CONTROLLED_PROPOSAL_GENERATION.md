# Phase 5.7 — Controlled Proposal Generation (Design Spec)

## Status

**Spec only.**
No implementation is permitted until this document is reviewed and design-locked.

---

## Purpose

Phase 5.7 defines **when and how AI-generated proposals may be created** for the first time.

It introduces proposal generation **without violating** the guarantees established in Phases 5.1–5.6:

* Determinism-first output
* Human-in-the-loop mediation
* No hidden inference
* No persistence or learning
* No authority transfer to AI

This phase governs **generation only**.
Approval and application remain governed by **Phase 5.6**.

---

## Scope (What This Phase Enables)

Phase 5.7 allows the system to:

* Generate **optional, descriptive proposals** in response to **explicit user requests**
* Use an LLM **only after deterministic output is shown**
* Produce proposals that are:

  * inspectable
  * discardable
  * non-authoritative

All generated content must pass through the **unchanged Phase 5.6 Human Approval Gate**.

---

## Explicit Non-Goals

Phase 5.7 does **not** enable:

* Resume scoring
* Suitability judgments
* Candidate ranking
* “You should apply” recommendations
* Preference learning
* Behavioral modeling
* Long-term memory
* Automated follow-ups or actions

Any of the above requires a **new phase and charter**.

---

## Entry Conditions (Hard Requirements)

Proposal generation may occur **only if all conditions are met**:

1. **Deterministic analysis has already completed**

   * Job parsing and gap surfacing must run first
   * AI may not replace or shortcut deterministic output

2. **User explicitly requests proposal generation**

   * No auto-generation
   * No background generation
   * No “helpful” defaults

3. **Generation context is explicitly declared**

   * Example contexts:

     * `evidence_gap_clarification`
     * `project_example`
     * `phrasing_variant`
   * Context describes *why* the proposal exists, never *what the user should do*

If any condition is unmet, **generation must not occur**.

---

## Generation Constraints (LLM Guardrails)

All proposal generation must obey the following constraints:

* Output must be:

  * descriptive, not prescriptive
  * suggestion-oriented, not directive
  * phrased without evaluative language

* Forbidden language includes (non-exhaustive):

  * “you should”
  * “best option”
  * “recommended”
  * “strong candidate”
  * “likely to succeed”

* Proposals must not:

  * assert correctness
  * imply hiring outcomes
  * compare the user to other candidates

---

## Output Requirements

Every generated proposal must:

1. Be wrapped in a **Proposal object** as defined in the Phase 5.6 addendum

2. Enter the system in `pending` state

3. Be clearly labeled as:

   > **AI-generated, optional, non-authoritative**

4. Pass through the **unchanged Phase 5.6 approval workflow**

The generation step may not bypass, pre-fill, or pre-approve any proposal.

---

## Ephemerality & Memory Rules

* Generated proposals are **ephemeral**
* No proposal text, metadata, or outcomes may be stored beyond the current interaction
* No aggregation or learning from:

  * accepted proposals
  * edited proposals
  * rejected proposals

Generation has **zero memory** of prior interactions.

---

## Failure & Abort Conditions

Proposal generation must abort immediately if:

* Deterministic analysis fails
* User cancels generation
* Guardrail validation fails
* Output cannot be safely labeled

In all cases:

* No partial output may be shown
* No proposal object may be created

---

## Auditability

Phase 5.7 must remain auditable by ensuring:

* Clear separation between deterministic output and AI output
* Explicit labeling of all AI-generated text
* No hidden control flow or background execution

A user must be able to answer, at any time:

> **“Why does this proposal exist?”**

---

## Design Lock Statement

Phase 5.7 introduces **generation capability only**, under strict conditions.

Any expansion involving:

* personalization
* persistence
* automation
* inference
* ranking
* or behavioral modeling

requires a **new phase and explicit user consent**.

---

## Guiding Question (Reaffirmed)

At every step of proposal generation, the system must ask:

> **“If this feature disappeared tomorrow, would the user lose agency?”**

If the answer is **yes**, the design is invalid.

---

**End of Phase 5.7 Spec**

