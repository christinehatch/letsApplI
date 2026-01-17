# Phase 5.4 — LLM Participation Model (Constrained, Non-Evaluative)

**Status:** 🔒 Design lock (no implementation)  
**Applies to:** letsA(ppl)I Phase 5+  
**LLM usage:** Not enabled until this phase is locked

---

## Purpose

This phase defines **exactly how and where an LLM may participate** in letsA(ppl)I.

Its goal is to ensure that:
- The LLM never evaluates the user
- The LLM never makes career judgments or predictions
- All outputs remain assistive, inspectable, and reversible
- Human agency is preserved at all times

This phase acts as a **hard safety boundary** before any LLM-backed functionality is introduced.

---

## Core Principle

> The LLM is a **language transformer**, not a decision-maker.

The LLM may help manipulate *text*, but it must never:
- Assess competence
- Judge readiness
- Predict outcomes
- Recommend actions implicitly or explicitly

---

## Allowed LLM Capabilities (Strict Allowlist)

The LLM may only be used for the following operations.

### 1. Text Normalization

The LLM may:
- Simplify job posting language
- Remove marketing or non-instructional fluff
- Normalize terminology (e.g., “experience with Python” → “Python”)

**Constraints:**
- No semantic interpretation
- No addition of meaning
- Output must be traceable to original text

---

### 2. Evidence Extraction (Descriptive Only)

From provided text (resume, project descriptions, job posting), the LLM may extract:
- Explicitly mentioned skills
- Explicitly named tools
- Explicitly described projects
- Explicitly referenced artifacts

**Disallowed:**
- Inferring skills not present
- Estimating proficiency
- Interpreting intent or depth

---

### 3. Phrase Matching & Clustering

The LLM may:
- Identify synonymous or near-synonymous phrases
- Cluster related terminology
- Match similar language across inputs

Examples:
- “REST APIs” ↔ “API development”
- “Demo systems” ↔ “technical demos”

This is **linguistic matching only**, not evaluative comparison.

---

### 4. Output Rewriting (User-Facing)

The LLM may:
- Rephrase system-generated facts into clearer language
- Format outputs as Markdown
- Produce neutral summaries of already-determined information

**All rewritten content must be derived from deterministic system outputs.**

---

## Explicitly Disallowed LLM Behaviors

The LLM must **never**:

- Say or imply:
  - “You are a good fit”
  - “You are missing X”
  - “You should apply”
  - “You are not qualified”
- Rank, score, or grade:
  - Resume sections
  - Skills
  - Experience
  - Fit percentage
- Infer:
  - Seniority
  - Readiness
  - Likelihood of success
- Invent:
  - Skills
  - Experience
  - Job requirements

If a task cannot be completed **without inference**, it must fail closed.

---

## Determinism & Control Requirements

Any future LLM usage must satisfy:

- Static, versioned prompts
- Fixed, low temperature
- No conversational memory
- No personalization state
- Post-processing via deterministic rules
- Full traceability back to source text

The LLM is never the final authority.

---

## Failure Behavior

If the LLM:
- Encounters ambiguity
- Cannot extract without inference
- Would need to judge or evaluate to proceed

Then the system must:
- Return a neutral fallback response
- Surface ambiguity to the user
- Defer interpretation to applyAI (future integration)

Silent guessing is not permitted.

---

## Relationship to Other Phases

**Depends on:**
- Phase 5.2 — Evidence classification
- Phase 5.3 — Language guardrails

**Unlocks:**
- Phase 5.5 — LLM-assisted gap surfacing (if approved)

No LLM-backed code may be written before this phase is locked.

---

## Completion Criteria (Design Lock)

Phase 5.4 is considered complete when:
- Allowed behaviors are exhaustively enumerated
- Disallowed behaviors are explicit and unambiguous
- Failure modes are documented
- Another engineer cannot accidentally overreach

---

## Explicit Non-Goals

- Resume evaluation
- Career advice
- Application decisions
- Hiring predictions
- Personality or aptitude analysis

These concerns belong outside letsA(ppl)I and are intentionally deferred.

---

**Design intent:**  
LLMs may assist with language — never judgment.

