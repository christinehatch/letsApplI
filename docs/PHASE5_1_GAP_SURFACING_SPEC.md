# Phase 5.1 — Guided Job → Evidence Gap Surfacing (Specification)

**Status:** Design lock (spec only)  
**Code:** ❌ None  
**LLM use:** ❌ Not enabled  
**Scope:** letsA(ppl)I ↔ applyAI boundary definition

---

## Purpose

Phase 5.1 introduces **guided evidence gap surfacing** for individual job postings.

The goal is to help a user answer:

> “Based on *my existing resume and projects*, what parts of this job posting are **already evidenced**, and what parts **lack visible proof** — without judging fit or making recommendations.”

This phase **does not** decide whether a user is qualified.  
It **does not** score, rank, or recommend jobs.

It exists to:
- Reduce cognitive load when reading job descriptions
- Make implicit expectations explicit
- Create a bridge to **user-initiated project creation** via applyAI

---

## High-Level Behavior

Given:
- A single job posting (URL or structured job object)
- A user-provided resume or portfolio snapshot

The system may:
1. Extract **explicit skill and responsibility claims** from the job posting
2. Match those claims against **explicit evidence** in the resume
3. Surface **gaps as “missing evidence”**, not deficiencies
4. Offer the option to explore those gaps via applyAI

At no point does the system:
- Decide if the user is “good enough”
- Suggest applying or not applying
- Rank the user against other candidates

---

## Definitions

### Evidence (strict)

Evidence is **explicit, user-provided proof**, such as:
- Named projects
- Shipped systems
- Specific technologies used
- Measurable outcomes

Evidence is **not**:
- Inferred ability
- Adjacent experience
- “Likely capable” assumptions
- Soft skill extrapolation

If it is not explicitly stated, it does not count.

---

### Gap (reframed)

A “gap” is defined as:

> A job requirement for which **no explicit evidence is currently visible** in the provided materials.

A gap is **not**:
- A failure
- A weakness
- A rejection signal
- A recommendation to fix anything

It is simply **unmapped territory**.

---

### Ambiguous Evidence Handling

When comparing job requirements to resume evidence, ambiguity must be handled conservatively.

- If a requirement is partially implied but not explicitly stated, it must be treated as **not present**
- The system must not speculate, infer intent, or “read between the lines”
- Ambiguity is surfaced neutrally (e.g., *“This requirement is not explicitly mentioned”*)
- No clarification questions are asked automatically

This rule exists to prevent interpretive creep and to ensure that all surfaced gaps are based solely on observable, inspectable text.

---


## Allowed Outputs (Phase 5.1)

The system may generate:

### 1. Job Requirement Breakdown
A neutral list of:
- Core responsibilities
- Required skills
- Preferred experience

All extracted verbatim or near-verbatim from the posting.

---

### 2. Evidence Mapping Table

For each requirement:

| Job Requirement | Evidence Found | Evidence Source |
|-----------------|---------------|-----------------|
| X               | Yes / No      | Resume section / Project name |

No confidence scoring.  
No language like “strong”, “weak”, or “insufficient”.

---

### 3. Gap Summary (Neutral)

Example phrasing (illustrative only):

> “The following areas do not currently have visible evidence in your resume or projects:  
> • Distributed systems at scale  
> • Payment compliance (PCI, SOX)”

---

### 4. Optional Bridge Prompt (Non-Directive)

The system **may** ask:

> “Would you like to explore creating evidence for any of these areas?”

This is the **only forward action allowed** in Phase 5.1.

---

## Explicitly Forbidden Behaviors

The system must **not**:

- Say “you should apply” or “you shouldn’t apply”
- Score fit, readiness, or likelihood of success
- Rank gaps by importance
- Suggest learning paths
- Suggest courses, certifications, or bootcamps
- Rephrase gaps as weaknesses
- Create projects automatically
- Persist any interpretation as memory

No exceptions.

---

## Relationship to applyAI

Phase 5.1 **does not create projects**.

Instead, it may:
- Hand off a **user-selected gap** to applyAI
- Provide **context only**, not instructions

applyAI remains responsible for:
- Project ideation
- Skill validation scaffolding
- Confidence-building through creation
- Ethical guardrails and consent

The boundary is strict:
> letsA(ppl)I surfaces gaps → user chooses → applyAI explores

---

## Consent & Control

- The user must explicitly opt in before:
  - Resume analysis
  - Gap surfacing
  - applyAI handoff
- No automatic progression
- No background analysis

Closing the flow must leave **no state changes** unless the user explicitly requests continuation.

---

## Non-Goals (Out of Scope)

Phase 5.1 does **not** attempt to:
- Optimize resumes
- Rewrite bullet points
- Predict recruiter behavior
- Simulate ATS systems
- Perform skill assessments
- Diagnose career paths

These are intentionally excluded.

---

## Success Criteria

Phase 5.1 is complete when:

- A user can look at a job posting and say:
  > “I clearly see what I’ve already proven — and what I haven’t — without feeling judged.”

- The output feels **clarifying, not evaluative**
- The user retains full agency over next steps

---

## Phase Boundary

Phase 5.1 ends **before**:
- Any recommendation
- Any scoring
- Any project creation
- Any memory persistence

Those require later phases with separate consent and specs.

---

**End of Phase 5.1 Specification**

