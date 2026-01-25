# Phase 6 — Lock Declaration (Hydration & Exploration)

**Design Lock — Frozen Behavior + Frozen Meaning**

**Lock Date:** 2026-01-25
**Lock Owner:** letsA(ppl)I
**Applies To:** `docs/PHASE6_*` and `src/ui/phase6/**` (behavior + UX meaning)

---

## 0. Declaration

Phase 6 is hereby **formally locked**.

Phase 6 defines a **human-led viewing and exploration surface** that preserves epistemic integrity:

> **Viewing is not reading.**
> **Reading is not interpretation.**
> **Interpretation is never automatic.**

This lock does **not** mean Phase 6 will never change.
It means Phase 6 must never change what it **means** or what it **permits**.

---

## 1. What Phase 6 Is

Phase 6 exists to let the user:

* Select a discovered job
* Open and view it
* Orient themselves (optional, title-only)
* Explicitly request consent for reading
* Retain full control over whether the system has read anything

Phase 6 is intentionally **not** an AI phase.

It is a **boundary-preserving UX phase**.

---

## 2. Frozen State Model

Phase 6 must preserve these **explicit, user-visible states**:

* **VIEWING** — User is viewing a job; the system has not read it
* **ORIENTED** — Optional title-only orientation (non-interpretive)
* **CONSENT_REQUESTED** — User has been asked for consent to read
* **CONSENT_GRANTED** — Consent granted; Phase 6 hands off immediately

At all times, the system must be able to truthfully state one of the following:

1. *“You are viewing this job. I have not read it.”*
2. *“You have allowed me to read this job.”*
3. *“I have read this job and produced the following artifacts.”*

Phase 6 may only ever be in states (1) or (2).
State (3) is downstream of Phase 5.x.

---

## 3. Hard Prohibitions (Non-Negotiable)

The following are **permanently forbidden** in Phase 6.

### 3.1 No Reading Without Consent

* No parsing, extracting, summarizing, tokenizing, embedding, or indexing
* No background fetch that makes job content available to the system
* No “temporary reads,” “UI-only reads,” or similar exceptions

### 3.2 No Interpretation

* No fit analysis
* No skills or requirements extraction
* No prioritization or highlighting
* No recommendations or next-step suggestions
* No inferred seniority beyond generic title archetypes
* No persuasive language that nudges consent

### 3.3 No Persistence of Meaning

* No saving interpretations, notes, or assessments
* No preference learning
* No silent accumulation of user behavior

### 3.4 No Authority Creep

* The system must not imply it knows job content
* The system must not imply the user *should* grant consent
* The system must not imply downstream artifacts exist when they do not

If a source blocks access:
**Mark unavailable, document, move on. Restraint is a feature.**

---

## 4. Allowed Changes

Changes to Phase 6 are permitted **only** if they do not alter meaning or authority.

### Allowed

* Copy edits and typo fixes
* Visual or layout refinements
* Accessibility improvements
* Refactors that preserve state semantics
* Tests that strengthen enforcement

### Not Allowed

* Any reading of job content
* Any analysis prior to Phase 5.1
* Any state that blurs viewing vs. reading
* Any automatic transition toward interpretation

---

## 5. Enforcement

All Phase 6 changes must be reviewed using:

* `docs/PHASE6_PR_REVIEW_RUBRIC.md`

Any pull request that fails the rubric must be rejected, regardless of utility.

---

## 6. Boundary With Phase 5.1

Phase 6 may emit **only**:

* A selected job identifier (from discovery metadata)
* A user action requesting consent to read
* A UI state indicating consent requested or granted

Phase 6 must **not**:

* Accept hydrated job text
* Store hydrated job text
* Transform hydrated job text
* Produce artifacts derived from job text

All consent-scoped reading begins in **Phase 5.1**.

---

## 7. Lock Summary

Phase 6 is frozen as:

**A truth-preserving, human-led viewing interface**
that cannot become a pre-analysis assistant.

Phase 6 protects system integrity by protecting what it does **not** know.

**This lock is binding.**

