# Interpretation Behavior Specification
## Phase 5.2 — Structured, Consent-Gated Job Reasoning

---

# Purpose

This document defines the behavioral contract for Phase 5.2 interpretation.

Phase 5.2 performs structured reasoning over hydrated job content.
It does NOT provide advice.
It does NOT evaluate fit.
It does NOT recommend actions.

Interpretation must remain analytical, neutral, and traceable.

---

# Architectural Context

Phase 5.2 sits between:

- Phase 5.1 (Hydration — raw content)
- Phase 5.3 (Fit analysis — user material required)

Interpretation operates ONLY on:

- job_id
- raw_content
- read_at timestamp

It must not:

- Fetch additional data
- Persist reasoning
- Access user resume
- Infer user skill
- Infer hiring probability

---

# Core Behavioral Principles

1. Hydration ≠ Interpretation  
2. Interpretation ≠ Advice  
3. Interpretation ≠ Fit Judgment  
4. Interpretation must be explainable  
5. Interpretation must remain non-prescriptive  
6. Interpretation must remain reversible (revocation clears results)

---

# Output Structure

Phase 5.2 produces structured output:

- Role Summary
- Requirements Analysis
- Capability Emphasis Signals (descriptive only)
- Project Opportunity Signals (descriptive only)

Each section has constraints defined below.

---

# 1. Role Summary

## Allowed

- Description of what the role appears to do
- Description of team context (if present in text)
- Description of mission language used in posting
- Neutral synthesis of responsibilities

Example (Allowed):

> "This role focuses on building distributed backend systems for financial infrastructure."

## Forbidden

- “This role is a great opportunity for…”
- “This would be ideal if you…”
- “You would enjoy this if…”

No personalization.
No evaluative framing.

---

# 2. Requirements Analysis

Must separate:

- Explicit requirements (clearly stated)
- Implicit signals (inferred from language)
- Seniority indicators

## Allowed

- Extraction of bullet requirements
- Identification of repeated skill themes
- Identification of ownership language
- Identification of cross-functional collaboration signals

Example (Allowed):

> "The posting repeatedly references cross-team collaboration and ownership."

## Forbidden

- Ranking difficulty
- Stating candidate competitiveness
- Declaring role “senior” unless explicitly stated
- Probability statements

No hiring outcome inference.

---

# 3. Capability Emphasis Signals

This section describes capability categories emphasized by the role.

It must remain strictly job-focused.

Allowed:
- “The role emphasizes distributed systems experience.”
- “Backend ownership appears central.”
- “Cross-functional collaboration is repeatedly referenced.”

Forbidden:
- Any second-person language
- Any reference to a specific candidate
- Any suggestion to modify a resume
- Any evaluation of candidate strength
- Any comparative judgment

This section must not reference the user in any form.
It describes role expectations only.

---

# 4. Project Opportunity Signals (Descriptive Capability Framing)

This section identifies capability demonstration categories.

Allowed:
- “Demonstration of event-driven architecture aligns with system design emphasis.”
- “Projects reflecting API ownership would correspond to listed backend responsibilities.”
- This section must describe categories of demonstrable capability only.It must not suggest that such projects should be created.

Forbidden:
- Imperative verbs (“build”, “create”, “design” directed at user)
- Instructional framing
- Strategic advice
- Application tactics
- Direct suggestion to take action

Project signals must describe capability categories,
not actions to be taken.


---

# Determinism Requirement

Given identical raw_content input, Phase 5.2 must produce structurally equivalent output.

Minor phrasing variation is acceptable.
Structural meaning must not vary.

Interpretation must not introduce stochastic reasoning differences that alter:

- Identified requirements
- Extracted signals
- Capability categories
- Seniority indicators

---

# Implicit Signal Constraints

Implicit signals may be derived from:

- Repeated terminology
- Ownership language
- Collaboration language
- Seniority cues
- Responsibility density

Implicit signals must not:

- Invent unstated requirements
- Infer hiring competitiveness
- Assume organizational structure not described
- Add external company knowledge

If implicit signal inference is uncertain, it must be omitted.
---

# Grounding Requirement

All interpretation output must be grounded exclusively in the provided raw_content.

Interpretation must not:

- Use external knowledge of the company
- Reference known industry context not present in the text
- Inject assumptions about hiring practices
- Infer unstated role expectations
- Add historical, market, or competitive commentary

Every structured output element must be directly traceable to language patterns in raw_content.

If grounding is unclear, the interpreter must omit the signal rather than speculate.

---

# Confidence Semantics

The confidence field reflects structural interpretation quality only.

Confidence may reflect:
- Clarity of job description
- Density of explicit requirements
- Structural completeness of extraction

Confidence must NOT reflect:
- Hiring likelihood
- Candidate fit
- Difficulty of role
- Market competitiveness

Confidence is about interpretation reliability,
not outcome probability.

---

# Tone Requirements

All output must be:

- Neutral
- Analytical
- Structured
- Impersonal
- Non-evaluative
- Non-judgmental

Language must avoid:

- Second-person pronouns ("you")
- Imperatives ("do", "apply", "build")
- Value judgments ("strong", "weak", "excellent")
- Emotional framing
- Motivational language

---

# Disallowed Language List

The following phrases must NEVER appear in Phase 5.2 output:

- you should
- you must
- you need to
- good fit
- great fit
- perfect fit
- recommend
- advise
- apply now
- likely to get
- high chance
- competitive
- ideal for you

This list is not exhaustive.
It represents the non-prescriptive guardrail.

---

# LLM Usage Constraints (Future)

If LLM is used:

- It must operate under strict system prompt constraints
- It must return structured JSON
- It must not output advice
- It must not infer candidate quality
- It must not generate probabilistic hiring language

LLM output is proposal-only.
The interpreter is responsible for validation and filtering.

---

# Revocation Semantics

If interpretation consent is revoked:

- Structured interpretation must be cleared
- No structured reasoning remains in memory
- Raw hydrated content may remain
- No derived artifacts may persist

Interpretation must be ephemeral.

---

# Failure Behavior

If:

- raw_content is empty
- read_at is missing
- scope is invalid

Interpretation must fail with explicit error.

No silent fallback.
No default behavior.

---

# Definition of Compliant Interpretation

An interpretation is compliant if:

- It remains descriptive
- It references only job content
- It avoids second-person language
- It contains no prescriptive phrasing
- It does not evaluate fit
- It does not predict hiring outcome
- It does not persist state

---

END OF SPEC
