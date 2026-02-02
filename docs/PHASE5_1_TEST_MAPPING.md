# Phase 5.1 — Invariant → Test Mapping

**Concrete Unit & Integration Tests**

**Applies To:** Phase 5.1 — Consent-Scoped Reading
**Source of Truth:** `PHASE5_1_TEST_INVARIANTS.md`
**Purpose:** Make authority limits executable and enforceable

---

## 0. How to Read This Document

For each invariant, this document specifies:

* **Test Type**

  * *Unit*: validates internal logic, guards, and state transitions
  * *Integration*: validates end-to-end behavior across boundaries
* **Test Setup**
* **Expected Assertion**
* **Failure Signal**

Any implementation of Phase 5.1 must implement **at least one test per invariant**.
Critical invariants require **both** unit and integration coverage.

---

## 1. Consent Enforcement

### INV-5.1-CONSENT-001 — No Read Without Consent

**Unit Test**

* **Setup:** Instantiate Phase 5.1 reader with no consent payload
* **Action:** Attempt to invoke read/fetch method
* **Assert:**

  * Fetch function is never called
  * Reader throws or returns an explicit “not authorized” error

**Integration Test**

* **Setup:** Navigate from Phase 6 without granting consent
* **Action:** Attempt to enter Phase 5.1
* **Assert:**

  * No network request to job source occurs
  * UI states “job not read”

**Failure Signal**

* Any job content present in memory, logs, or UI

---

### INV-5.1-CONSENT-002 — Explicit Scope Validation

**Unit Test**

* **Setup:** Provide consent payload with scope ≠ `read_job_posting`
* **Action:** Initialize Phase 5.1
* **Assert:** Phase 5.1 aborts with scope error

**Integration Test**

* **Setup:** Tamper consent payload (e.g. `read_job`, `read_anything`)
* **Action:** Attempt read
* **Assert:** No fetch, no read, explicit rejection

**Failure Signal**

* Phase 5.1 proceeds under non-exact scope

---

### INV-5.1-CONSENT-003 — Consent Revocation Halts Execution

**Unit Test**

* **Setup:** Begin read with valid consent
* **Action:** Revoke consent mid-execution
* **Assert:**

  * Reader halts immediately
  * No further read calls are executed

**Integration Test**

* **Setup:** Start reading, then revoke consent via UI
* **Action:** Observe system behavior
* **Assert:**

  * Content disappears or is hidden
  * System reports “not authorized”

**Failure Signal**

* Continued access or display after revocation

---

## 2. Reading Boundary

### INV-5.1-READ-001 — Reading Is the First Content Access

**Unit Test**

* **Setup:** Phase 5.1 instantiated but not activated
* **Action:** Inspect internal state
* **Assert:**

  * No job content in memory
  * No parsing/tokenization methods invoked

**Failure Signal**

* Any pre-read inspection or preprocessing

---

### INV-5.1-READ-002 — Fetch Scope Is Single-Surface Only

**Unit Test**

* **Setup:** Mock fetch layer
* **Action:** Trigger read
* **Assert:**

  * Exactly one fetch call
  * URL matches primary job posting only

**Integration Test**

* **Setup:** Job posting with links, expandable sections, PDFs
* **Action:** Read job
* **Assert:**

  * No secondary network requests
  * No linked assets loaded

**Failure Signal**

* Multiple fetches or auxiliary requests

---

### INV-5.1-READ-003 — Unavailability Is Terminal

**Unit Test**

* **Setup:** Mock job source to return blocked/unavailable
* **Action:** Attempt read
* **Assert:**

  * Abort occurs
  * No retries
  * Explicit unavailable state returned

**Integration Test**

* **Setup:** Use known gated source
* **Action:** Attempt read
* **Assert:**

  * Single failed attempt
  * Clear “not accessed” message

**Failure Signal**

* Retry logic, fallback fetches, or bypass attempts

---

## 3. Representation

### INV-5.1-REP-001 — No Content Transformation

**Unit Test**

* **Setup:** Provide known job content fixture
* **Action:** Read and render content
* **Assert:**

  * Output text matches input byte-for-byte
  * Order and sections unchanged

**Failure Signal**

* Any diff beyond transport encoding

---

### INV-5.1-REP-002 — No UI Salience Injection

**Integration Test**

* **Setup:** Render job content UI
* **Action:** Inspect rendered DOM / view tree
* **Assert:**

  * No highlights
  * No emphasized sections
  * No labels like “important” or “key”

**Failure Signal**

* Any visual or structural emphasis not present in source

---

### INV-5.1-REP-003 — Partial Content Must Be Marked

**Integration Test**

* **Setup:** Force truncated content (e.g. network cutoff)
* **Action:** Display content
* **Assert:**

  * Explicit “incomplete content” notice visible
  * No implication of completeness

**Failure Signal**

* Silent truncation

---

## 4. Persistence

### INV-5.1-PERSIST-001 — No Raw Content Persistence

**Unit Test**

* **Setup:** Complete Phase 5.1
* **Action:** Inspect storage layers (cache, disk, logs)
* **Assert:** No raw job content stored

**Integration Test**

* **Setup:** Restart application/session
* **Action:** Inspect state
* **Assert:** Job content is absent

**Failure Signal**

* Any durable content retention

---

### INV-5.1-PERSIST-002 — No Derived Meaning Persistence

**Unit Test**

* **Setup:** Complete read
* **Action:** Inspect persistence layer
* **Assert:**

  * No summaries
  * No tags
  * No embeddings
  * No inferred metadata

**Failure Signal**

* Any stored interpretation artifacts

---

## 5. Truthfulness

### INV-5.1-TRUTH-001 — Knowledge Claims Must Be Accurate

**Integration Test**

* **Setup:** Run through read, failure, and no-consent paths
* **Action:** Query system status language
* **Assert:**

  * Claims exactly match system knowledge
  * No implied analysis or understanding

**Failure Signal**

* Overstated or misleading claims

---

### INV-5.1-TRUTH-002 — Reading Does Not Imply Understanding

**Integration Test**

* **Setup:** Read job
* **Action:** Observe system messaging
* **Assert:**

  * No advice
  * No evaluation
  * No fit language

**Failure Signal**

* Any guidance-like phrasing

---

## 6. Phase Boundary

### INV-5.1-BOUNDARY-001 — No Phase Leakage

**Integration Test**

* **Setup:** Complete Phase 5.1
* **Action:** Monitor system
* **Assert:**

  * No Phase 5.2+ triggers
  * No downstream artifacts created

**Failure Signal**

* Any automatic transition or precomputation

---

## 7. Enforcement Rule

All invariant tests must:

* Run in CI
* Block merge on failure
* Be treated as **design correctness tests**, not feature tests

Skipping or weakening an invariant test is equivalent to expanding system authority without consent.

---

## 8. Summary

These tests make Phase 5.1’s promise **real**:

* Consent is enforced, not assumed
* Reading is bounded, not helpful
* Authority is earned, not inferred

If the tests pass, Phase 5.1 is compliant.
If they fail, the design has been violated.

**This mapping is binding.**

