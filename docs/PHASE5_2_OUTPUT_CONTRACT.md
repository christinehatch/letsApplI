# Phase 5.2 — Interpretation Output Contract

**Phase:** 5.2 — Interpretation
**Status:** Draft (Binding Upon Lock)
**Depends On:**

* `PHASE5_2_OPENING_DECLARATION.md`
* `PHASE5_2_GUARD_LOCK.md`

---

## 0. Purpose

This document defines the **only permitted output** of Phase 5.2.

Phase 5.2 is the first phase in which the system is allowed to **interpret**
job content that has already been read in Phase 5.1.

This contract exists to:

* Prevent interpretation from drifting into evaluation or recommendation
* Preserve epistemic honesty about what the system knows
* Ensure downstream phases do not over-trust interpretation artifacts
* Make interpretation output auditable, bounded, and non-authoritative

This contract is **binding**.

---

## 1. Interpretation Boundary

Phase 5.2 operates strictly within the following boundary:

```
Raw Job Content (Phase 5.1)
        │
        ▼
Interpretation (Phase 5.2)
        │
        ▼
InterpretationResult (This Contract)
```

Phase 5.2:

* **Consumes** raw job content and metadata from Phase 5.1
* **Produces** interpretation artifacts only
* **Does not** perform evaluation, ranking, or recommendation

---

## 2. InterpretationResult Schema

Phase 5.2 must produce an object conforming to the following conceptual schema:

```json
{
  "job_id": "string",
  "interpreted_at": "ISO-8601 timestamp",
  "source_read_at": "ISO-8601 timestamp",
  "artifacts": {
    "responsibilities": ["string", "..."],
    "requirements": ["string", "..."],
    "qualifications": ["string", "..."]
  },
  "confidence": "low | medium | high",
  "limitations": ["string", "..."]
}
```

This schema is **illustrative**, not prescriptive at the field level, but all
outputs must obey the semantic rules below.

---

## 3. Allowed Claims

Phase 5.2 **may**:

* Rephrase job content into structured language
* Extract explicitly stated responsibilities or requirements
* Normalize wording (e.g. bullet lists → sentences)
* Identify *what the job posting says*, not what it implies

All claims must be traceable to **observable job text**.

---

## 4. Forbidden Claims

Phase 5.2 must **not**:

* Judge candidate fit or suitability
* Score relevance or importance
* Rank requirements by value
* Infer employer intent beyond the text
* Recommend actions to the user
* Compare this job to other jobs
* Assert facts not present in the posting

Phase 5.2 **must not** produce language such as:

* “This role is a good fit for you”
* “You should apply”
* “This is a senior-level role”
* “This skill is critical”

Those require later phases and explicit consent.

---

## 5. Confidence & Limitations

Every InterpretationResult must include:

* A **confidence signal** indicating how literal vs inferred the interpretation is
* A **limitations list** describing ambiguity, missing data, or uncertainty

This ensures downstream phases cannot treat interpretation as ground truth.

---

## 6. Provenance Requirements

Every InterpretationResult must explicitly include:

* `job_id` — unchanged from Phase 5.1
* `source_read_at` — timestamp from Phase 5.1
* `interpreted_at` — timestamp of interpretation

If provenance cannot be established, interpretation must **abort**.

---

## 7. Persistence Rules

Phase 5.2 may:

* Persist interpretation artifacts **only if** later phases require them

Phase 5.2 must **not**:

* Persist raw job content
* Persist user-specific conclusions
* Persist preferences or judgments

Persistence semantics must be explicitly defined in downstream phases.

---

## 8. Relationship to Phase 5.3+

Phase 5.2 output:

* **May** be consumed by Phase 5.3 (Fit Analysis)
* **May not** be shown directly to users as advice
* **May not** trigger actions without new consent

Downstream phases must treat Phase 5.2 output as:

> *Structured interpretation, not evaluation.*

---

## 9. Invariants

This contract enforces the following invariants:

* Interpretation ≠ recommendation
* Structure ≠ judgment
* Confidence ≠ authority
* Interpretation does not imply user intent

Violation of these invariants is a **design failure**, not a UX issue.

---

## 10. Summary

Phase 5.2 produces:

**Interpretation artifacts that describe what a job posting says —
and nothing about what the user should do.**

This contract exists to ensure interpretation remains helpful
without becoming prescriptive, persuasive, or misleading.

**This contract defines the maximum authority of Phase 5.2 output.**

