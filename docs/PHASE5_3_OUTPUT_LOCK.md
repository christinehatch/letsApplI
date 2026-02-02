# Phase 5.3 — Fit Analysis Output Contract

**Non-Prescriptive Alignment Signals**

**Phase:** 5.3 — Fit Analysis
**Status:** Draft (Binding Upon Lock)
**Depends On:**

* `PHASE5_3_OPENING_DECLARATION.md`
* `PHASE5_3_GUARD_LOCK.md`
* `PHASE5_2_OUTPUT_LOCK.md`

---

## 0. Purpose

This document defines the **only permitted output** of Phase 5.3.

Phase 5.3 is the first phase in which the system may **relate interpreted job content to user-provided materials**. This introduces significant risk of implicit judgment or advice.

This contract exists to:

* Ensure fit analysis remains **descriptive, not prescriptive**
* Prevent alignment signals from being mistaken as recommendations
* Preserve user agency and reflective decision-making
* Make Phase 5.3 output auditable, bounded, and non-authoritative

This contract is **binding** once locked.

---

## 1. Fit Analysis Boundary

Phase 5.3 operates strictly within the following boundary:

```
InterpretationResult (Phase 5.2)
        +
User-Provided Materials
        │
        ▼
Fit Analysis (Phase 5.3)
        │
        ▼
FitAnalysisResult (This Contract)
```

Phase 5.3:

* **Consumes** structured interpretation artifacts
* **Consumes** explicit, user-supplied materials
* **Produces** alignment observations only

Phase 5.3 **does not** decide meaning, value, or action.

---

## 2. FitAnalysisResult Schema

Phase 5.3 must produce an object conforming to the following conceptual schema:

```json
{
  "job_id": "string",
  "analyzed_at": "ISO-8601 timestamp",
  "source_interpreted_at": "ISO-8601 timestamp",
  "alignment": {
    "matches": ["string", "..."],
    "gaps": ["string", "..."],
    "ambiguous": ["string", "..."]
  },
  "confidence": "low | medium | high",
  "limitations": ["string", "..."],
  "summary": "string"
}
```

This schema is **illustrative**, not prescriptive at the field level, but all
outputs must obey the semantic rules below.

---

## 3. Allowed Claims

Phase 5.3 **may**:

* State where user materials explicitly align with job requirements
* Identify where requirements are not addressed in provided materials
* Describe ambiguity or insufficient evidence
* Rephrase alignment in neutral, observational language

All claims must be traceable to:

* Phase 5.2 interpretation artifacts, and
* Explicit user-provided data

---

## 4. Forbidden Claims

Phase 5.3 must **not**:

* Judge candidate quality or readiness
* Predict hiring outcomes
* Recommend applying or not applying
* Suggest resume changes
* Rank strengths or weaknesses
* Assert what the user *should* do next

Phase 5.3 **must not** produce language such as:

* “You should highlight…”
* “This is a good fit”
* “You are missing critical skills”
* “You are well-qualified”
* “We recommend…”

Such language requires downstream phases and new consent.

---

## 5. Summary Field Constraints

If a free-text `summary` field is present:

* It must be **descriptive only**
* It must restate alignment observations without interpretation
* It must not contain advice, encouragement, or discouragement
* It must not include prescriptive verbs

The summary exists for **human readability**, not decision guidance.

---

## 6. Confidence & Limitations

Every FitAnalysisResult must include:

* A **confidence indicator** reflecting completeness of the comparison
* A **limitations list** describing missing data, ambiguity, or scope constraints

Confidence signals **do not imply correctness or authority**.

---

## 7. Provenance Requirements

Every FitAnalysisResult must explicitly include:

* `job_id` — unchanged from Phase 5.2
* `source_interpreted_at` — timestamp from Phase 5.2
* `analyzed_at` — timestamp of fit analysis execution

If provenance cannot be established, fit analysis must **abort**.

---

## 8. Persistence Rules

Phase 5.3 may:

* Persist alignment artifacts **only if** required by later phases

Phase 5.3 must **not**:

* Persist judgments
* Persist user preferences
* Persist conclusions as facts
* Persist inferred intent

Persistence semantics must be explicitly defined downstream.

---

## 9. Relationship to Phase 5.4+

Phase 5.3 output:

* **May** be consumed by Phase 5.4 (Guided Resume Refinement)
* **May not** trigger downstream phases automatically
* **May not** be shown as advice without new user consent

Downstream phases must treat Phase 5.3 output as:

> *Descriptive alignment signals — not evaluation.*

---

## 10. Invariants

This contract enforces the following invariants:

* Alignment ≠ endorsement
* Gaps ≠ deficiencies
* Comparison ≠ judgment
* Insight ≠ instruction
* Confidence ≠ authority

Violation of these invariants is a **design failure**, not a UX issue.

---

## 11. Summary

Phase 5.3 produces:

**Structured observations about how job requirements and user materials relate —
without telling the user what that means or what to do next.**

This contract defines the **maximum authority** of Phase 5.3 output.

Anything beyond this requires a new phase, new consent, and a new lock.

