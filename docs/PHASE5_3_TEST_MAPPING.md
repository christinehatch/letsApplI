# Phase 5.3 — Invariant → Test Mapping  
**Fit Analysis (Non-Prescriptive)**

**Applies To:** Phase 5.3 — Fit Analysis  
**Source of Truth:** `PHASE5_3_TEST_INVARIANTS.md`  
**Purpose:** Make fit analysis authority explicit, bounded, and enforceable

---

## 0. How to Read This Document

For each invariant, this document specifies:

- **Test Type**
  - *Unit*: validates guards, input validation, and output shaping
  - *Integration*: validates end-to-end behavior and language constraints
- **Test Setup**
- **Expected Assertion**
- **Failure Signal**

Every invariant must be enforced by **at least one automated test**.  
Critical authority boundaries require **both unit and integration coverage**.

---

## 1. Consent & Activation

### INV-5.3-CONSENT-001 — Explicit User Intent Required

**Unit Test**
- **Setup:** Phase 5.3 analyzer instantiated without user intent flag
- **Action:** Attempt to run analysis
- **Assert:** Analyzer raises `AnalysisNotAuthorizedError`

**Integration Test**
- **Setup:** Navigate UI without selecting “Analyze Fit”
- **Action:** Trigger Phase 5.3
- **Assert:** No analysis runs; system reports “analysis not requested”

**Failure Signal**
- Analysis executes without explicit user request

---

### INV-5.3-CONSENT-002 — Explicit Input Selection

**Unit Test**
- **Setup:** Provide analyzer with empty or implicit user input set
- **Action:** Attempt analysis
- **Assert:** Analyzer aborts with input selection error

**Failure Signal**
- Analyzer accesses user data not explicitly provided

---

## 2. Input Boundaries

### INV-5.3-INPUT-001 — Phase 5.2 Output Required

**Unit Test**
- **Setup:** Analyzer without Phase 5.2 interpretation input
- **Action:** Run analysis
- **Assert:** Error raised indicating missing interpretation artifacts

**Failure Signal**
- Analyzer runs directly on raw job content

---

### INV-5.3-INPUT-002 — No Raw Job Content Access

**Integration Test**
- **Setup:** Instrument Phase 5.1 content store
- **Action:** Run Phase 5.3
- **Assert:** No reads of raw job text occur

**Failure Signal**
- Any access to Phase 5.1 raw content

---

## 3. Analysis Scope

### INV-5.3-ANALYSIS-001 — Comparison Only

**Unit Test**
- **Setup:** Provide interpretation artifacts + user resume
- **Action:** Run analysis
- **Assert:** Output describes alignment relationships only

**Failure Signal**
- Output contains evaluative language

---

### INV-5.3-ANALYSIS-002 — No Scoring or Ranking

**Unit Test**
- **Setup:** Normal analysis run
- **Action:** Inspect output
- **Assert:** No numeric scores, percentages, or rankings

**Failure Signal**
- Presence of any scoring or ranking artifacts

---

### INV-5.3-ANALYSIS-003 — Gaps Are Descriptive

**Integration Test**
- **Setup:** Provide resume missing a requirement
- **Action:** Run analysis
- **Assert:** Output states absence neutrally

**Failure Signal**
- Deficit framing (e.g. “weak”, “lacking”, “critical gap”)

---

## 4. Output Language

### INV-5.3-LANGUAGE-001 — No Advice

**Integration Test**
- **Setup:** Run full analysis
- **Action:** Scan output language
- **Assert:** No imperatives, suggestions, or guidance phrases

**Failure Signal**
- “You should…”, “Consider…”, “Recommended…”

---

### INV-5.3-LANGUAGE-002 — No Fit Judgments

**Integration Test**
- **Setup:** Run analysis with strong alignment
- **Action:** Inspect output
- **Assert:** No “good fit”, “strong match”, or equivalent phrasing

**Failure Signal**
- Any fit labeling or endorsement

---

## 5. Persistence

### INV-5.3-PERSIST-001 — No Preference Learning

**Unit Test**
- **Setup:** Run analysis
- **Action:** Inspect persistence layer
- **Assert:** No user preferences or traits stored

**Failure Signal**
- Stored conclusions or inferred preferences

---

### INV-5.3-PERSIST-002 — No Downstream Triggering

**Integration Test**
- **Setup:** Run Phase 5.3
- **Action:** Observe system state
- **Assert:** Phase 5.4+ does not auto-start

**Failure Signal**
- Automatic phase escalation

---

## 6. Truthfulness

### INV-5.3-TRUTH-001 — Descriptive Framing Only

**Integration Test**
- **Setup:** Run analysis
- **Action:** Inspect system language
- **Assert:** Output framed as comparison, not authority

**Failure Signal**
- Claims implying correctness or judgment

---

### INV-5.3-TRUTH-002 — Uncertainty Preserved

**Unit Test**
- **Setup:** Ambiguous interpretation input
- **Action:** Run analysis
- **Assert:** Output acknowledges ambiguity

**Failure Signal**
- Overconfident or definitive language

---

## 7. Enforcement Rule

All Phase 5.3 tests must:

- Run in CI
- Block merge on failure
- Be treated as **authority enforcement**, not feature tests

Weakening or skipping these tests is equivalent to
**granting advisory authority without consent**.

---

## 8. Summary

These tests ensure Phase 5.3 remains:

- Analytical, not advisory
- Comparative, not judgmental
- Informative, not directive

If the tests pass, Phase 5.3 is compliant.  
If they fail, the design has been violated.

**This mapping is binding.**

