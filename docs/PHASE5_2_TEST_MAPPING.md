# Phase 5.2 — Invariant → Test Mapping

**Human-Gated Interpretation**

**Applies To:** Phase 5.2 — Interpretation
**Source of Truth:** `PHASE5_2_TEST_INVARIANTS.md`
**Blocking:** YES
**Purpose:** Make interpretation authority explicit, bounded, and test-enforced

---

## 0. How to Read This Document

For each Phase 5.2 invariant, this document defines:

* **Test Type**

  * *Unit*: internal logic, guardrails, state checks
  * *Integration*: end-to-end behavior across reader → interpreter → UI
* **Test Setup**
* **Assertion**
* **Failure Signal**

Every invariant **must** be enforced by at least one automated test.
Critical invariants require **both unit and integration coverage**.

If a test fails, **Phase 5.2 is non-compliant**.

---

## 1. Interpretation Activation

### INV-5.2-ACT-001 — Interpretation Requires Explicit User Action

**Unit Test**

* **Setup:** Phase 5.1 read completed
* **Action:** Call interpretation logic without user approval flag
* **Assert:** Interpretation function aborts with `NotAuthorizedError`

**Integration Test**

* **Setup:** UI shows “job read” state
* **Action:** Observe system without clicking “Interpret”
* **Assert:**

  * No interpretation artifacts created
  * No LLM calls triggered

**Failure Signal**

* Interpretation occurs automatically after read

---

### INV-5.2-ACT-002 — Interpretation Is Job-Scoped

**Unit Test**

* **Setup:** Two job IDs exist
* **Action:** Attempt to interpret job B after approving job A
* **Assert:** Interpretation rejected

**Failure Signal**

* Cross-job interpretation

---

## 2. Input Boundaries

### INV-5.2-IN-001 — Interpretation Input Is Limited to ReadResult

**Unit Test**

* **Setup:** Mock interpreter input
* **Assert:**

  * Only `ReadResult.content` is passed
  * No resume, history, preferences, or prior interpretations included

**Failure Signal**

* Interpreter receives external context

---

### INV-5.2-IN-002 — No Hidden Augmentation

**Integration Test**

* **Setup:** Run interpretation with minimal job content
* **Assert:**

  * No enrichment from external sources
  * No inferred requirements beyond literal text

**Failure Signal**

* Interpretation references unseen information

---

## 3. Output Constraints

### INV-5.2-OUT-001 — Output Is Proposal-Only

**Unit Test**

* **Setup:** Run interpretation
* **Assert:**

  * Output type is `Proposal` (or equivalent)
  * No advice, ranking, or recommendation types returned

**Failure Signal**

* Interpretation emits conclusions or directives

---

### INV-5.2-OUT-002 — No Persistence Without Acceptance

**Integration Test**

* **Setup:** Generate proposal
* **Action:** User rejects or ignores proposal
* **Assert:**

  * No interpretation artifacts stored
  * No state mutation occurs

**Failure Signal**

* Interpretation saved without acceptance

---

## 4. Language & Framing

### INV-5.2-LANG-001 — Interpretive Language Is Conditional

**Integration Test**

* **Setup:** Generate interpretation proposal
* **Assert:**

  * Language uses conditional framing (“may suggest”, “could imply”)
  * No absolute claims (“this role requires”, “you should”)

**Failure Signal**

* Definitive or authoritative language

---

### INV-5.2-LANG-002 — No User Fit Claims

**Unit Test**

* **Setup:** Interpretation output
* **Assert:**

  * No references to user skill match
  * No suitability, fit, or recommendation language

**Failure Signal**

* Fit or evaluation claims appear

---

## 5. LLM Authority Limits (If Used)

### INV-5.2-LLM-001 — LLM Runs in Advisory Mode Only

**Unit Test**

* **Setup:** Mock LLM client
* **Assert:**

  * Output is wrapped as proposal
  * LLM output never bypasses human gate

**Failure Signal**

* LLM output treated as truth

---

### INV-5.2-LLM-002 — LLM Cannot Trigger Downstream Phases

**Integration Test**

* **Setup:** Accept or reject interpretation
* **Assert:**

  * No automatic transition to Phase 5.3
  * No resume or fit logic invoked

**Failure Signal**

* LLM output causes phase advancement

---

## 6. Phase Boundary Enforcement

### INV-5.2-BOUNDARY-001 — Interpretation Does Not Imply Action

**Integration Test**

* **Setup:** Complete Phase 5.2 interpretation
* **Assert:**

  * No guidance UI shown
  * No next-step prompts auto-rendered

**Failure Signal**

* System nudges or guides user

---

## 7. Enforcement Rule

All Phase 5.2 tests must:

* Run in CI
* Block merge on failure
* Be treated as **authority tests**, not UX tests

Weakening or skipping a test is equivalent to **expanding system authority**.

---

## 8. Summary

This mapping ensures that Phase 5.2:

* Interprets only when asked
* Knows only what it has read
* Proposes meaning without asserting it
* Never substitutes judgment for the human

If these tests pass, Phase 5.2 is compliant.
If they fail, interpretation has exceeded its mandate.

**This mapping is binding.**

