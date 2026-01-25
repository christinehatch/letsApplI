# Phase 6 → Phase 5.1 Handoff Contract

**Consent-Scoped Reading Boundary**

**Status:** Active Contract
**Defined On:** 2026-01-25
**Upstream Phase:** Phase 6 — Hydration & Exploration (Locked)
**Downstream Phase:** Phase 5.1 — Consent-Scoped Reading

---

## 0. Purpose

This document defines the **only permitted interface** between:

* **Phase 6** (human-led viewing & consent acquisition)
* **Phase 5.1** (explicit, consent-scoped reading)

The purpose of this contract is to:

* Preserve the epistemic boundary between *viewing* and *reading*
* Prevent early interpretation or authority creep
* Ensure Phase 6 remains behaviorally frozen
* Ensure Phase 5.1 activates **only** after explicit user intent

This contract is **binding**.

---

## 1. Directionality

The handoff is **strictly one-way**.

```
Phase 6  ──(consent + job_id)──▶  Phase 5.1
```

Phase 6 **emits** signals.
Phase 5.1 **consumes** signals.

Phase 6 must never receive hydrated content, derived artifacts, or interpretation results from Phase 5.1.

---

## 2. Preconditions for Handoff

Phase 6 may initiate a handoff **only** if all conditions are met:

1. A job has been selected from the discovery registry
2. The user is in one of the following states:

   * `VIEWING`
   * `ORIENTED`
3. The user performs an **explicit consent action**
4. The consent scope is clearly stated and visible to the user

If any precondition is not met, **handoff must not occur**.

---

## 3. Handoff Payload (Strict Schema)

Phase 6 may emit **only** the following payload:

```json
{
  "job_id": "string",
  "consent": {
    "granted": true,
    "scope": "read_job_posting",
    "granted_at": "ISO-8601 timestamp",
    "revocable": true
  },
  "source": {
    "origin": "discovery_registry",
    "availability": "available | unavailable"
  }
}
```

### Explicitly Excluded

The payload must **not** include:

* Job description text
* Parsed HTML
* Tokens, embeddings, summaries, or excerpts
* Orientation notes
* User preferences or inferred intent
* Any interpretation or derived meaning

---

## 4. Responsibilities by Phase

### Phase 6 Responsibilities (Upstream)

Phase 6 is responsible for:

* Presenting the consent request clearly and neutrally
* Making explicit what the system **has not read**
* Emitting the handoff payload exactly once per consent action
* Immediately relinquishing control after consent is granted

Phase 6 must **not**:

* Perform reading itself
* Cache job content
* “Prepare” content for Phase 5.1
* Predict or preview downstream outcomes

---

### Phase 5.1 Responsibilities (Downstream)

Phase 5.1 is responsible for:

* Verifying the consent payload
* Validating scope and revocability
* Performing the **first actual read** of job content
* Operating strictly within the granted consent scope

Phase 5.1 must **not**:

* Assume prior knowledge of the job
* Attribute meaning or intent to Phase 6 actions
* Persist content or interpretation beyond its defined scope
* Expand scope without a new consent action

---

## 5. Consent Semantics

Consent at this boundary is:

* **Explicit** — requires a deliberate user action
* **Scoped** — applies only to `read_job_posting`
* **Revocable** — user may withdraw at any time
* **Non-transitive** — does not grant interpretation, summarization, or analysis

Granting consent to read **does not** imply consent to:

* Evaluate fit
* Extract skills
* Compare jobs
* Modify resumes
* Generate recommendations

Those require later phases and separate consent.

---

## 6. Failure & Unavailability Handling

If the job source is blocked or inaccessible:

* Phase 6 must mark the job as `unavailable`
* The handoff must still be well-formed
* Phase 5.1 must abort reading gracefully
* The system must state clearly:

  > “This job could not be read. No content was accessed.”

**No retries, no workarounds, no escalation.**

Restraint is a feature.

---

## 7. Invariants

This contract enforces the following invariants:

* Phase 6 never reads job content
* Phase 5.1 never runs without consent
* No phase implies knowledge it does not have
* Discovery ≠ Reading ≠ Interpretation
* Human intent gates every boundary crossing

Violation of any invariant is a **system failure**, not a UX bug.

---

## 8. Contract Stability

This handoff contract may be:

* Clarified
* Commented
* Tested

It may **not** be relaxed or widened.

Any change that alters authority, scope, or meaning requires a new phase and a new lock.

---

## 9. Summary

The Phase 6 → Phase 5.1 handoff is:

**A narrow, explicit, consent-gated bridge**
between **seeing** and **reading**.

It exists to protect user agency, system truthfulness,
and the long-term integrity of letsA(ppl)I.

**This contract is binding.**

