# Phase 6 — Hydration & Exploration (Human-Led UX)

## Purpose

Phase 6 defines how a user **views, explores, and inspects a job listing**
after discovery but **before AI interpretation**.

This phase exists to give the user **direct access to the job itself** while
maintaining strict boundaries around what the system has and has not read.

Phase 6 is explicitly **human-led**.

The system’s role is to:
- present access
- clarify state
- wait for instruction

Not to infer, interpret, or decide.

---

## Core Principle

> **Viewing is not reading.  
> Reading is not interpretation.  
> Interpretation is never automatic.**

This principle governs every behavior in Phase 6.

---

## Relationship to Other Phases

### Upstream

**Phase 4.5 — Discovery**
- Jobs are discovered via metadata only.
- The system truthfully states:  
  _“I have not read these jobs.”_

**Phase 5.1 — Hydration Consent**
- Defines the consent boundary for allowing the system to read job content.
- Phase 6 must never bypass this gate.

### Downstream

**Phase 5.2+ — Evidence, Guardrails, LLM Participation**
- May only occur after:
  - the user has hydrated a job
  - consent has been explicitly granted
  - content has been user-provided or explicitly authorized

Phase 6 does **not** replace or duplicate Phase 5 safeguards.
It precedes them.

---

## Definition: Hydration (Phase 6 Context)

In Phase 6, “hydration” means:

> **The user intentionally opens and views a job listing.**

Hydration does **not** mean:
- scraping
- parsing
- summarizing
- extracting requirements
- assessing fit
- invoking AI

Hydration is **access**, not understanding.

---

## System States (Explicit and Observable)

At all times during Phase 6, the system must be able to state one of the following:

1. **“You are viewing this job. I have not read it.”**
2. **“You have allowed me to read this job.”**
3. **“I have read this job and produced the following artifacts.”**

There must be no ambiguous or hidden intermediate state.

---

## Phase 6 Capabilities

### 6.0 — View Job (Read-Only)

- The user can open a job listing via:
  - a side panel
  - an embedded browser view
  - or an external link
- The job is shown **as-is**
- No transformation or summarization occurs
- The system clearly labels its state:
  > “I am showing you this job. I have not read or interpreted it.”

This is the default and safest behavior.

---

### 6.1 — Optional Orientation (Non-Interpretive)

While viewing a job, the system **may** provide general orientation that:

- is based only on:
  - job title
  - known role archetypes
- does **not** rely on job content
- does **not** claim accuracy

Example language:
> “Roles with this title are generally associated with X/Y/Z.  
> I have not read this job.”

This orientation must remain:
- optional
- dismissible
- clearly bounded

---

### 6.2 — Explicit Read Request (Bridge to Phase 5)

The system may present an explicit action, such as:

> **“Allow the system to read this job”**

Selecting this action:
- invokes Phase 5.1 consent
- clearly explains what reading enables
- does nothing automatically beyond the granted scope

If the user does not take this action, the system remains passive.

---

## Non-Goals (Explicit)

Phase 6 does **not** include:

- AI summaries by default
- Fit scoring
- Resume matching
- Recommendations
- Seniority inference
- Role desirability judgments
- Persistence of interpretations

Any of the above must occur in later phases and only after consent.

---

## Failure and Edge-Case Handling

If:
- the job page is blocked
- content cannot be rendered
- the link breaks
- the format is unsupported

The correct behavior is:

> **State the limitation.  
> Do not guess.  
> Do not substitute.**

Restraint remains a feature.

---

## UX Integrity Requirements

Phase 6 UX must ensure:

- The user can always see the original job
- The system never replaces the job with its own output
- The user knows exactly what the system has access to
- The user can disengage at any time

No irreversible actions occur in this phase.

---

## Exit Criteria (Phase 6 Complete)

Phase 6 is considered complete when:

- A user can open and view a job listing
- The system clearly communicates that it has not read the job
- Optional, title-based orientation is available but not forced
- A clear transition exists into Phase 5.1 consent
- No AI interpretation occurs without explicit user intent

---

## Summary

Phase 6 establishes a **trust-preserving bridge** between discovery and AI assistance.

It ensures that:
- users see what matters first
- systems remain honest about their knowledge
- consent precedes comprehension
- interpretation remains human-approved

This phase is intentionally quiet.

That quiet is what makes the rest of the system credible.

