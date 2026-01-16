# Phase 5.3 — Language Guardrails (LLM-Safe Phrasing)

**Status:** Design lock (no implementation)  
**Scope:** Output language only  
**Applies to:** All future LLM participation in Phase 5+

---

## Purpose

Phase 5.3 defines **strict language constraints** that govern how the system may describe:

- Job requirements
- Resume evidence
- Gaps or missing signals
- Suggested next steps

These guardrails exist to prevent:
- Evaluation or judgment
- Career advice masquerading as insight
- Confidence erosion
- Authority transfer from human → system

This phase does **not** introduce LLMs.  
It defines how LLMs *must speak* once introduced.

---

## Core Principle

> The system may **surface relationships between text artifacts**,  
> but may **never assess the person behind them**.

---

## Allowed Language (Whitelisted Patterns)

The system may use **descriptive, relational phrasing** only.

### Evidence Surfacing
- “This resume includes experience related to…”
- “This job posting mentions…”
- “An example of X appears in your resume as…”
- “This requirement appears to be referenced here…”

### Gap Surfacing
- “This posting mentions X, but no direct reference was found in the resume text.”
- “This requirement is present in the job description, but no matching evidence was detected.”
- “This area may benefit from additional visible examples.”

### Neutral Framing
- “Based on the text provided…”
- “In the materials shared…”
- “From the content alone…”

---

## Explicitly Disallowed Language (Hard Blocks)

The system must **never** produce:

### Judgment / Evaluation
- ❌ “You are qualified / unqualified”
- ❌ “You would be a good fit”
- ❌ “You are missing key skills”
- ❌ “Your resume is weak / strong”

### Authority Claims
- ❌ “This role is right for you”
- ❌ “You should apply / shouldn’t apply”
- ❌ “Hiring managers want…”
- ❌ “This will hurt your chances”

### Psychological Inference
- ❌ “You seem inexperienced”
- ❌ “You lack confidence”
- ❌ “You are not ready”
- ❌ “This suggests seniority / lack thereof”

---

## Structural Language Rules

All generated language must satisfy:

- **Artifact-anchored**  
  Every claim must reference *job text* or *resume text*, never the person.

- **Non-comparative**  
  No ranking, scoring, or weighting between job and resume.

- **Non-directive**  
  No instructions framed as advice (“you should…”).

- **Optional framing only**  
  Suggestions must be framed as *optional explorations*, never prescriptions.

---

## Approved Suggestion Framing

When proposing next steps:

**Allowed**
- “One possible way to make this experience more visible is…”
- “If you wanted to demonstrate this skill, an example could be…”
- “Some candidates choose to show this by…”

**Disallowed**
- “You need to add…”
- “You should fix…”
- “You must demonstrate…”

---

## LLM Participation Contract (Forward-Looking)

When LLMs are introduced:

- LLM output must pass a **language lint step**
- Any sentence violating guardrails is:
  - rewritten, or
  - removed entirely
- Deterministic fallback copy must exist for all outputs

No free-form LLM output is allowed without post-processing.

---

## Non-Goals

Phase 5.3 explicitly does **not**:

- Decide fit
- Score resumes
- Predict hiring outcomes
- Recommend career paths
- Optimize resumes automatically

---

## Completion Criteria

Phase 5.3 is complete when:

- All allowed / disallowed language is documented
- Guardrails are referenced by future phases
- No LLM can be added without complying with this spec

---

## Phase Boundary

> If any future change requires *breaking these guardrails*,  
> it must be introduced as a **new phase with a new charter**.

