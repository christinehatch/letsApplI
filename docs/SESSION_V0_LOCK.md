# Session V0 — Daily Discovery Loop (Lock)

**Status:** Locked
**Lock Type:** UX / Orchestration Boundary
**Date Locked:** 2026-01-26

---

## 0. Purpose

This document locks **Session V0**, the first end-to-end, user-operable experience of letsA(ppl)I.

Session V0 defines the **minimum complete daily loop** that allows a user to:

1. Declare exploration intent
2. Trigger job discovery
3. Browse a generated daily feed
4. Select a job by stable ID
5. Read raw job content safely

This lock ensures the session experience remains:

* Deterministic
* Non-authoritative
* Free of hidden intelligence
* Safe to extend incrementally

---

## 1. What Session V0 Is

Session V0 is a **procedural orchestration layer**.

It acts as:

* A conductor
* A UX spine
* A wiring harness between already-locked phases

It is intentionally allowed to feel linear and imperative.

---

## 2. Responsibilities (Explicitly Allowed)

Session V0 **may**:

* Capture ephemeral user intent (non-persisted)
* Invoke discovery across registered source adapters
* Generate `DAILY_OUTPUT.md`
* Display stable job identifiers (`source:source_job_id`)
* Route job selection to Phase 5.1 readers
* Allow repeated browsing within a single session

Session V0 **does not** own intelligence, meaning, or judgment.

---

## 3. Explicit Non-Responsibilities (Hard Boundaries)

Session V0 **must not**:

* Interpret job content
* Rank jobs using inference or scoring
* Filter jobs based on intent semantics
* Modify job data
* Persist user preferences
* Infer user goals
* Trigger downstream phases automatically
* Cache or learn from interaction behavior

Any such behavior requires:

* A new phase
* Explicit user consent
* A separate lock document

---

## 4. Phase Relationships

Session V0 composes the following locked components:

* **Phase 3** — Source Adapters (read-only ingestion)
* **State Layer** — `apply_first_seen` (deterministic timestamps)
* **Phase 5.1** — Job Reading (raw, consent-gated)
* **Feed Generator** — Rule-based daily output

Session V0 does **not** elevate the authority of any phase.

---

## 5. Data & Persistence Rules

* User intent is **ephemeral**
* Job discovery state is limited to:

  * `first_seen_at`
  * stable job identity
* No session history is persisted
* No analytics are recorded

---

## 6. UX Guarantees

Session V0 guarantees that:

* The user always knows what happened
* Output is inspectable (`DAILY_OUTPUT.md`)
* Job IDs are stable and reproducible
* No hidden steps occur between input and output

---

## 7. Why This Lock Exists

Session V0 exists to answer one question:

> “What does it feel like to use this system, end-to-end, *before* it becomes intelligent?”

This lock preserves that answer.

---

## 8. Change Policy

Any change that alters:

* Authority
* Interpretation
* Persistence
* Recommendation

**must not modify Session V0**, and instead requires:

* A new session mode, or
* A new downstream phase

---

## 9. Summary

Session V0 is:

> **A daily mirror, not a guide.
> A browser, not an advisor.
> A system you can trust because it does not pretend to know.**

This lock makes that invariant explicit and durable.

