# Phase 5.1 — Opening Declaration

**Consent-Scoped Reading**

**Status:** Formally Open
**Opened On:** 2026-01-25
**Preceded By:** Phase 6 — Hydration & Exploration (Locked)
**Governing Contract:** `PHASE6_TO_PHASE5_1_HANDOFF.md`

---

## 0. Declaration

Phase 5.1 is hereby **formally opened**.

Phase 5.1 is the **first phase in letsA(ppl)I** in which the system is permitted to **read job content** — and only under **explicit, user-granted consent**.

This phase exists to cross a single boundary:

> **From viewing → to reading**

No other boundary is crossed in this phase.

---

## 1. Purpose of Phase 5.1

Phase 5.1 exists solely to:

* Perform the **first actual read** of a job posting
* Do so **only after explicit consent**
* Operate within a narrowly defined, revocable scope
* Preserve truth about what the system knows and does not know

Phase 5.1 is **not** an interpretation phase.
Phase 5.1 is **not** an evaluation phase.
Phase 5.1 is **not** a recommendation phase.

It is a **reading-only phase**.

---

## 2. Authority Granted

Phase 5.1 is granted authority to:

* Fetch job posting content **only after consent**
* Read the content in full
* Represent that content faithfully
* Acknowledge unavailability or failure explicitly

Phase 5.1 is **not** granted authority to:

* Interpret meaning
* Judge relevance or fit
* Extract skills or requirements
* Rank, summarize, or prioritize content
* Persist derived meaning
* Influence user decisions

Reading is the **only** permitted operation.

---

## 2.1 Definition: Faithful Representation

For the purposes of Phase 5.1, a **faithful representation** means:

- No reordering of content
- No omission of sections
- No highlighting, emphasis, or prioritization
- No normalization, summarization, or cleanup
- No UI-driven salience changes

If content is displayed, it must be either:
- the full raw content as retrieved, or
- clearly marked as incomplete or unavailable

Any transformation beyond literal display constitutes interpretation and is forbidden in Phase 5.1.

Fetching job content is limited to the primary job posting surface explicitly requested by the user.
No auxiliary pages, expandable sections, attachments, or linked resources may be fetched without additional consent.

---

## 3. Consent Requirements

Phase 5.1 may activate **only** if it receives a valid handoff payload containing:

* A `job_id`
* Explicit consent with scope `read_job_posting`
* A revocable consent flag
* A timestamped user action

If consent is missing, ambiguous, expired, or revoked:

**Phase 5.1 must not run.**

---

## 3.1 Consent Revocation

If consent is revoked at any point:

- Phase 5.1 must immediately halt
- Any unread content must not be accessed
- Any read content must not be reused or persisted
- The system must revert to a truthful “not authorized” state

Consent revocation does not permit continued display, reuse, or downstream reliance on previously read content.


---

## 4. Scope Boundaries

The scope of Phase 5.1 is **intentionally narrow**.

### Included

* Accessing the job posting text
* Handling blocked or unavailable sources
* Truthfully stating what was or was not read

### Excluded

* Any transformation of meaning
* Any analysis beyond literal reading
* Any user guidance or advice
* Any persistence of interpretations
* Any cross-job comparison
* An active user session ends when the user navigates away, revokes consent, or closes the interface.
* These invariants must be enforced at the code and review level.

Phase 5.1 produces **no insight artifacts**.

---

## 5. Output Guarantees

Phase 5.1 may produce **only**:

* A statement that the job was successfully read
* A statement that the job could not be read
* A faithful representation of the raw content (if shown)
* Provenance information (source, timestamp)

Phase 5.1 must be able to say, clearly and truthfully:

> “I have now read this job posting.
> I have not analyzed or interpreted it.”

---

## 6. Failure Handling

If job content is unavailable, blocked, or gated:

* Phase 5.1 must abort immediately
* No partial reads may be retained
* No retries or alternate access paths may be attempted
* The system must state explicitly that no content was accessed

Restraint is a feature.

---

## 7. Relationship to Future Phases

Phase 5.1 does **not** imply or unlock:

* Phase 5.2 (Interpretation)
* Phase 5.3 (Fit analysis)
* Phase 5.4+ (Resume, guidance, recommendations)

Each future phase requires:

* A new declaration
* A new consent boundary
* A new authority grant

---

## 8. Invariants

While Phase 5.1 is active, the following must remain true:

* Reading does not imply understanding
* Content does not imply advice
* Consent does not imply permission expansion
* The system never claims insight it has not earned

Any violation is a **design failure**, not a usability issue.

---

## 9. Summary

Phase 5.1 opens a **single, deliberate capability**:

**The ability to read — and nothing more.**

This phase exists to preserve trust by ensuring that
*knowing begins only when the user allows it*.

**Phase 5.1 is now open.**

