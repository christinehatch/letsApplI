# Phase 5.3 — Guard Lock

**Fit Analysis (Non-Prescriptive)**

**Phase:** 5.3
**Status:** Locked
**Locked On:** 2026-01-25
**Depends On:**

* `PHASE5_3_OPENING_DECLARATION.md`
* `PHASE5_2_OUTPUT_LOCK.md`

---

## 0. Purpose

This document formally **locks the guard conditions** for Phase 5.3.

Phase 5.3 introduces comparative analysis between:

* Interpreted job artifacts (Phase 5.2)
* User-provided materials

Because this phase operates closer to judgment and advice, its **entry conditions and output constraints are non-negotiable**.

This lock ensures Phase 5.3 cannot silently drift into recommendation, evaluation, or persuasion.

---

## 1. Required Preconditions

Phase 5.3 **must not execute** unless **all** of the following are true:

### 1.1 Interpretation Exists

* A valid Phase 5.2 `InterpretationResult` must be present
* Interpretation must include provenance (`job_id`, `source_read_at`)

If missing → **abort**

---

### 1.2 Explicit User Consent

* User must explicitly request fit analysis
* Consent must be affirmative and unambiguous

Implicit consent is forbidden.

If consent is missing → **abort**

---

### 1.3 User-Provided Materials

* User must explicitly provide or select materials to analyze
* Materials must be user-owned and voluntarily supplied

No inferred, cached, or assumed data is allowed.

If materials are missing → **abort**

---

## 2. Execution Constraints

While Phase 5.3 is executing:

* No fetching is permitted
* No interpretation is permitted
* No modification of user materials is permitted
* No persistence of conclusions as preferences is permitted

Phase 5.3 is **purely analytical**.

---

## 3. Output Guardrails

Phase 5.3 output **must**:

* Be descriptive, not evaluative
* Describe alignment, gaps, or ambiguity
* Use neutral, observational language

Phase 5.3 output **must not**:

* Recommend actions
* Judge candidate quality
* Predict outcomes
* Encourage or discourage applications
* Contain prescriptive language

---

## 4. Forbidden Language (Non-Exhaustive)

Phase 5.3 output must not include phrases implying:

* Advice (“you should”, “recommended”)
* Endorsement (“good fit”, “strong candidate”)
* Deficiency (“missing critical”, “lacking essential”)
* Optimization (“improve”, “fix”, “strengthen”)

Detection of such language constitutes a **design failure**, not a content bug.

---

## 5. Error Semantics

Violations of this guard lock must result in:

* Explicit exceptions
* No partial output
* No fallback behavior

Silent degradation is forbidden.

---

## 6. Invariants

While Phase 5.3 is active:

* Analysis ≠ recommendation
* Comparison ≠ judgment
* Gaps ≠ deficiencies
* Matches ≠ endorsements
* Insight ≠ instruction

These invariants are **structural**, not stylistic.

---

## 7. Summary

This guard lock ensures Phase 5.3 remains:

> **A mirror for alignment — not a voice of authority.**

Any future expansion of Phase 5.3 authority requires:

* A new opening declaration
* New guard tests
* A new lock document

**Phase 5.3 guard conditions are now immutable.**

