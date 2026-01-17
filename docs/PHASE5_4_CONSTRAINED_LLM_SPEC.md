# Phase 5.4 — Constrained LLM Participation (Design Lock)

## Purpose

Introduce an LLM into letsA(ppl)I **only as a constrained language transformation component**, not as a decision-maker, evaluator, advisor, or agent.

This phase defines **how an LLM may participate** without violating:
- Human-in-the-loop principles
- Phase 5.3 language guardrails
- The non-automation charter of letsA(ppl)I

No implementation is permitted until this phase is locked.

---

## Core Principle

> The LLM may only transform **explicit text provided by the user** into clearer, structured, or categorized language — without adding judgment, prediction, or advice.

The LLM is a **text mirror**, not an authority.

---

## Allowed LLM Capabilities

The LLM may:

- Rewrite job descriptions into clearer bullet points
- Extract skills explicitly stated in job text
- Extract skills explicitly stated in resume text
- Map resume phrases to job phrases (surface-level correspondence)
- Classify evidence using Phase 5.2 categories:
  - `explicit`
  - `adjacent`
  - `missing`
- Reformat output into human-readable Markdown
- Ask **clarifying questions** without implying deficiency

Example allowed outputs:
- “The job description mentions experience with distributed systems.”
- “The resume includes a project involving API design.”
- “Evidence classification: adjacent.”

---

## Explicitly Disallowed Capabilities

The LLM must **never**:

- Judge candidate fit
- Recommend applying or not applying
- Predict interview outcomes
- Assess competence, strength, or readiness
- Suggest career paths or next steps
- Rewrite resume content proactively
- Invent or infer missing experience
- Use motivational or discouraging language

Example forbidden outputs:
- “You are a strong fit for this role.”
- “You should improve your backend skills.”
- “This role may be challenging for you.”
- “I recommend building a project in X.”

---

## Input Contract (Strict)

The LLM may receive **only** the following inputs:

- `JOB_TEXT` — verbatim job description
- `RESUME_TEXT` — verbatim resume content
- Optional user-authored notes

The LLM may **not** receive:
- User history
- Stored memory
- Prior chats
- External context
- Any inferred user profile

---

## Output Contract (Strict)

The LLM may output only:

- Neutral, artifact-anchored statements  
- Structured classifications  
- Rephrasings of existing text  
- Questions phrased as invitations, not evaluations  

Allowed phrasing examples:
- “This requirement appears in the job description.”
- “There is no direct mention of this in the resume.”
- “Would you like to add an example related to this?”

---

## Enforcement Requirements

Phase 5.4 requires **two independent enforcement layers**.

### 1. Prompt-Level Guardrails
- System prompt explicitly references Phase 5.3
- Enumerated forbidden language
- Clear statement of non-advisory role

### 2. Post-Generation Validation
- Output scanned for:
  - Advice verbs (“should”, “recommend”, “need to”)
  - Judgment terms (“strong”, “weak”, “fit”, “qualified”)
  - Predictive language (“likely”, “will”, “chance”)
- Any violation causes the output to be rejected or rewritten

Fail-closed behavior is mandatory.

---

## Failure Handling

If the LLM cannot comply:
- The system must return a neutral error
- Or ask the user to rephrase input
- No partial or speculative output is allowed

---

## Explicit Non-Goals (Phase 5.4)

- ❌ Resume scoring
- ❌ Fit ranking
- ❌ Application automation
- ❌ Behavioral inference
- ❌ Personalized advice
- ❌ “AI coach” functionality

Any of the above would require a **new phase and new charter**.

---

## Completion Criteria (Design Lock)

Phase 5.4 is considered complete when:

- [ ] LLM role is fully constrained in writing
- [ ] Allowed and disallowed behaviors are enumerated
- [ ] Input and output contracts are explicit
- [ ] Enforcement strategy is defined
- [ ] No code violates these constraints

Once locked, Phase 5.4 may not be modified retroactively.

---

## Relationship to applyAI

letsA(ppl)I uses the LLM to **surface evidence gaps**.

applyAI may later use the same outputs to:
- Suggest project-based learning paths
- Scaffold evidence creation

However:
- letsA(ppl)I never prescribes solutions
- applyAI operates under a separate consent and exploration model

---

## Status

🔒 **Phase 5.4 — Design Locked**  
Implementation may begin only after this document is committed.

