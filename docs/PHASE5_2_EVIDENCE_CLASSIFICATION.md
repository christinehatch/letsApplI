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

# Phase 5.2 — Evidence Classification (Invariant Lock)

**Status:** Design-locked (no code yet)  
**Depends on:** Phase 5.1.1 (CLI-first gap surfacing)

Phase 5.2 introduces **classification of surfaced evidence and gaps**  
without judgment, scoring, or recommendation.

This phase answers:

> “What *type* of evidence is visible or missing?”  
> not  
> “Is this good enough?”

---

## 1. Purpose (Non-Negotiable)

Phase 5.2 exists to:
- Reduce cognitive load when reading gaps
- Organize information into recognizable categories
- Prepare *neutral inputs* for future exploration (e.g., applyAI)

It must **never** evaluate, rank, or advise.

---

## 2. Allowed Classification Axes (Closed Set)

Evidence and gaps may only be labeled using **one or more** of the following
**non-evaluative categories**:

- **Experience Evidence**  
  (roles, responsibilities, past work described)

- **Skill / Tool Mention**  
  (languages, frameworks, platforms explicitly named)

- **System / Domain Exposure**  
  (payments, infra, ML, security, etc., as explicitly stated)

- **Output / Artifact Evidence**  
  (projects, demos, repos, docs, shipped systems)

- **Scope / Level Indicator**  
  (senior, intern, manager — *only if explicitly written*)

No other categories may be introduced in Phase 5.2.

---

## 3. Classification Rules (Hard Constraints)

- [x] Classification is **descriptive only**
- [x] Classification is based on **verbatim text**
- [x] No inference across sections or lines
- [x] No normalization or abstraction
- [x] No combining weak signals into stronger claims

Allowed phrasing:
- “This requirement appears to be a **Skill / Tool Mention**”
- “The resume includes **Experience Evidence** related to X”

Forbidden phrasing:
- “This demonstrates competence in…”
- “This suggests readiness for…”
- “This is insufficient experience”

---

## 4. Handling Missing Evidence

When a job requirement has no matching resume evidence:

- It must be labeled **only** as:
  > “No explicit evidence found in the provided resume”

- It may optionally include:
  - The **classification type** of the requirement  
    (e.g., Skill / Tool Mention)

It must **never**:
- Imply deficiency
- Suggest remediation
- Predict outcomes

---

## 5. Output Structure (Stable)

Phase 5.2 output must preserve this structure:

1. **Requirement (verbatim)**
2. **Classification type**
3. **Resume evidence (quoted)** *or* “Not visible”

No scores.  
No percentages.  
No ordering by importance.

---

## 6. Language Guardrails (Strict)

The system must not use:

- “gap” (use “not visible” instead)
- “missing skill”
- “lacking”
- “needs”
- “should”

Approved neutral terms:
- “appears”
- “is mentioned”
- “is not present”
- “is classified as”

---

## 7. User Agency Invariants

- [x] User explicitly requests classification
- [x] User can opt out at any time
- [x] No classification persists beyond the run
- [x] Resume and job text are not stored
- [x] No cross-job aggregation

---

## 8. Relationship to applyAI (Boundary Lock)

Phase 5.2 outputs may be **passed forward** as inputs to applyAI *only if*:

- They remain neutral descriptors
- They are treated as **exploration prompts**
- They are never reframed as “deficits”

applyAI must:
- Ask before generating projects
- Avoid identity claims
- Avoid prescriptive paths

---

## 9. Explicitly Out of Scope (Phase 5.2)

Phase 5.2 must not include:

- Scoring or weighting
- ATS simulation
- Fit assessment
- Hiring likelihood
- Resume rewriting
- Recommendations

---

## 10. LLM Constraint

If an LLM is used in Phase 5.2:

- It may only:
  - Extract
  - Classify
  - Quote

- It must not:
  - Interpret intent
  - Predict ability
  - Generalize beyond text

**Violation of these constraints invalidates Phase 5.2.**

---

## Design Principle Reminder

> **Classification organizes information.**  
> **It does not judge it.**  
> **Understanding belongs to the user.**


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

