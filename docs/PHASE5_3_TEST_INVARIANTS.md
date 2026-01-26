# Phase 5.3 — Test Invariants  
**Fit Analysis (Non-Prescriptive)**

**Applies To:** Phase 5.3 — Fit Analysis  
**Depends On:**  
- `PHASE5_2_OUTPUT_LOCK.md`  
- Explicit user consent for fit analysis

**Status:** Binding upon Phase 5.3 implementation

---

## 0. Purpose

This document defines **non-negotiable test invariants** for Phase 5.3.

These invariants exist to ensure that:

- Fit analysis does not become advice
- Comparative logic does not become judgment
- Interpretation artifacts are not overstated
- User agency remains intact
- Downstream phases are not implicitly triggered

If any invariant in this document is violated,  
**the Phase 5.3 implementation is invalid**, regardless of UX quality.

---

## 1. Consent & Activation Invariants

### INV-5.3-CONSENT-001 — Explicit User Intent Required

**Assert**
- Phase 5.3 must not execute unless the user explicitly requests fit analysis

**Failure Mode**
- Automatic or implied analysis is forbidden

---

### INV-5.3-CONSENT-002 — Explicit Input Selection

**Assert**
- Only user-selected materials are analyzed
- No implicit resume, profile, or historical data is included

**Failure Mode**
- Silent inclusion of user data is forbidden

---

## 2. Input Boundary Invariants

### INV-5.3-INPUT-001 — Phase 5.2 Output Required

**Assert**
- Phase 5.3 must not run without valid Phase 5.2 interpretation output

**Failure Mode**
- Direct analysis of raw job content is forbidden

---

### INV-5.3-INPUT-002 — No Raw Job Content Access

**Assert**
- Phase 5.3 never accesses Phase 5.1 raw job content

**Failure Mode**
- Any read of raw job text is forbidden

---

## 3. Analysis Scope Invariants

### INV-5.3-ANALYSIS-001 — Comparison Only

**Assert**
- Output describes alignment or non-alignment between:
  - Interpreted job artifacts
  - User-provided materials

**Failure Mode**
- Any evaluative language is forbidden

---

### INV-5.3-ANALYSIS-002 — No Scoring or Ranking

**Assert**
- No numeric scores, grades, or rankings are produced

**Failure Mode**
- Scoring implies authority and is forbidden

---

### INV-5.3-ANALYSIS-003 — Gaps Are Descriptive, Not Deficiencies

**Assert**
- Missing alignment is described neutrally
- Language does not imply fault, weakness, or failure

**Failure Mode**
- Deficit framing is forbidden

---

## 4. Output Language Invariants

### INV-5.3-LANGUAGE-001 — No Advice

**Assert**
- Output contains no recommendations, suggestions, or instructions

**Forbidden Examples**
- “You should add…”
- “You need to improve…”
- “Consider revising…”

---

### INV-5.3-LANGUAGE-002 — No Fit Judgments

**Assert**
- Output does not label the user as a good or bad fit

**Forbidden Examples**
- “Strong match”
- “Poor fit”
- “Well-qualified”

---

## 5. Persistence Invariants

### INV-5.3-PERSIST-001 — No Preference Learning

**Assert**
- No conclusions are persisted as user preferences or traits

**Failure Mode**
- Learning from analysis without consent is forbidden

---

### INV-5.3-PERSIST-002 — No Downstream Triggering

**Assert**
- Phase 5.3 does not automatically activate Phase 5.4+

**Failure Mode**
- Implicit phase escalation is forbidden

---

## 6. Truthfulness Invariants

### INV-5.3-TRUTH-001 — Analysis Is Framed as Descriptive

**Assert**
- Output language reflects comparison, not authority

**Failure Mode**
- Implying correctness or expertise is forbidden

---

### INV-5.3-TRUTH-002 — Uncertainty Is Preserved

**Assert**
- Ambiguity or incomplete alignment is acknowledged where present

**Failure Mode**
- Overconfidence is forbidden

---

## 7. Enforcement Rule

All Phase 5.3 implementations must:

- Include automated tests for each invariant
- Fail fast on invariant violation
- Treat violations as **design errors**, not recoverable issues

---

## 8. Summary

Phase 5.3 is powerful and dangerous if unconstrained.

These invariants ensure that:

**Comparison does not become judgment.  
Insight does not become advice.  
Analysis does not replace human choice.**

Phase 5.3 exists to support reflection —  
**not to decide outcomes.**

