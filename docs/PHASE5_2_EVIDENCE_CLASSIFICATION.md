# Phase 5.2 — Evidence Classification (Deterministic)

## Status
**Design lock (spec-only)**  
No LLMs. No scoring. No recommendations.

---

## Purpose

Phase 5.2 introduces **structured, auditable classification** of how a resume relates to a job posting **without interpretation**.

The system answers:

> *“What evidence exists, what is missing, and what is unknown — based only on explicit text?”*

This phase transforms raw comparison output (Phase 5.1) into **machine-readable evidence signals** while preserving human judgment.

---

## Inputs

### Required
- Job description text (plain text)
- Resume text (plain text)

### Optional (but supported)
- User-provided highlights (e.g., manually emphasized resume sections)
- Prior Phase 5.1 output

---

## Output (Authoritative)

A **deterministic, structured artifact** (JSON + Markdown rendering) with **explicit evidence states**, never conclusions.

---

## Core Evidence States
All classifications are derived strictly from literal text present in the job description and resume.

Each detected requirement or capability must be classified into **exactly one** of the following:

### `explicit_match`
- Direct textual overlap
- Same term or clearly identical phrasing  
- Example: “Python”, “REST APIs”, “Docker”

### `partial_match`
- Related but not identical wording
- Requires **human confirmation**  
- Example: “Data pipelines” vs “ETL workflows”

### `missing`
- Present in job text
- Absent from resume text

### `unknown`
- Ambiguous or unverifiable from text alone  
- Example: “Ability to influence stakeholders”

⚠️ **No inferred matches are allowed.**  
If it is not textually supported, it cannot be upgraded.

---

## Classification Rules (Hard Invariants)

- No scoring
- No ranking
- No weighting
- No “fit” language
- No confidence estimates
- No career advice

Each classification must be:
- Explainable
- Reproducible
- Reversible

---

## Example Output (JSON)

```json
{
  "job_title": "Demo Engineer",
  "company": "Stripe",
  "classified_evidence": {
    "explicit_match": [
      {
        "requirement": "Python",
        "resume_evidence": "Built Flask-based demo systems in Python"
      }
    ],
    "partial_match": [
      {
        "requirement": "Customer-facing technical demos",
        "resume_evidence": "Presented technical walkthroughs to stakeholders"
      }
    ],
    "missing": [
      {
        "requirement": "Payments infrastructure experience"
      }
    ],
    "unknown": [
      {
        "requirement": "Cross-functional influence"
      }
    ]
  }
}


---

##Markdown Rendering (Human View)
Rendered as a neutral evidence table, not a judgment.

## Evidence Classification

### ✅ Explicit Matches
- Python — documented in demo systems
- Flask — explicitly listed

### ⚠️ Partial Matches (Review Needed)
- Customer-facing demos — similar experience described
- partial_match exists to flag potential relevance without asserting equivalence.

### ❌ Missing Evidence
- Payments infrastructure experience

### ❓ Unknown / Unverifiable
- Cross-functional influence


---

## Relationship to applyAI

**Phase 5.2 is the handoff boundary.**

### letsA(ppl)I
- Surfaces gaps  
- Classifies evidence  
- Stops  

### applyAI
- Helps users generate evidence  
- Proposes projects  
- Guides skill demonstration  

**No memory is shared automatically.**  
**No assumptions cross systems.**

---

## Explicit Non-Goals

Phase 5.2 does **not**:

- Decide readiness  
- Suggest resume edits  
- Recommend jobs  
- Rank candidates  
- Predict outcomes  
- Replace recruiters  
- Simulate hiring judgment  

---

## Completion Criteria

Phase 5.2 is complete when:

- Given the same job + resume, output is identical every run  
- Every requirement is classified exactly once  
- A human can disagree without the system “arguing”  
- Output can be safely passed to an LLM without granting authority  

