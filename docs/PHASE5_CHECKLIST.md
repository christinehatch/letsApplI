# PHASE 5 — Job ↔ Evidence Gap Surfacing (Checklist)

**Status:** Design-locked (spec only)  
**Scope:** Read-only, user-initiated analysis  
**Non-goal:** Automation, scoring, or judgment

Phase 5 introduces **guided comparison between a job posting and a user’s existing evidence (e.g., resume)** while preserving user agency, neutrality, and reversibility.

This checklist defines **what Phase 5 is allowed to do, what it must never do, and the invariants that must hold before any code is written.**

---

## 1. Entry Conditions (Must Be True)

- [x] Phase 4 is complete and locked
- [x] Job listings are surfaced without recommendations or scoring
- [x] User explicitly selects a single job to explore
- [x] User explicitly provides resume or evidence (paste or file)
- [x] No automatic processing occurs without user initiation

---

## 2. Allowed Inputs

- [x] A single job posting chosen by the user
- [x] User-provided resume text or document
- [ ] Optional user context (e.g., “I’m curious about this role”)

❌ Not allowed:
- External profile scraping
- Auto-imported resumes
- Historical user behavior
- Implicit preferences

---

## 3. Processing Rules (Hard Constraints)

- [x] Compare **explicit job requirements ↔ explicit resume evidence**
- [x] Identify:
  - Clear overlaps (mentioned in both)
  - Clear absences (mentioned in job, not present in resume)
- [x] Do **not** infer skills, intent, seniority, or potential
- [x] Do **not** normalize, score, rank, or weight requirements
- [x] Do **not** guess what the user “meant” or “likely has”

Allowed verbs:
- “mentions”
- “appears”
- “is listed”
- “is not present”

Disallowed verbs:
- “lacks”
- “fails”
- “needs”
- “should have”
- “is unqualified”

---

## 4. Output Language & Tone

All output must be:

- [x] Neutral
- [x] Descriptive
- [x] Non-evaluative
- [x] Reversible (no lasting conclusions)

Required framing examples:
- “This role mentions X; your resume includes Y.”
- “This requirement does not appear in the provided resume.”

Forbidden framing:
- “You are not qualified”
- “You should apply / shouldn’t apply”
- “This is a good / bad fit”

---

## 5. User Agency & Control

- [x] User initiates every comparison
- [x] User can stop or dismiss at any point
- [x] No automatic follow-up actions
- [x] No hidden state or memory creation
- [x] No persistence of resume content after session ends

---

## 6. applyAI Integration Boundary

- [x] Phase 5 may surface **optional evidence gaps**
- [x] Gaps may be offered as **inputs** to applyAI
- [x] applyAI must treat gaps as *exploration prompts*, not deficits
- [x] applyAI must never generate identity claims (“you are X”)
- [x] applyAI must never imply hiring outcomes

Phase 5 does **not**:
- Generate projects automatically
- Prescribe learning paths
- Convert gaps into obligations

---

## 7. Explicitly Out of Scope (Phase 5)

Phase 5 must **not** include:

- [x] Resume scoring or ATS optimization
- [x] Fit percentages or rankings
- [x] Career advice or recommendations
- [x] Hiring likelihood predictions
- [x] Behavioral or personality inference
- [x] Long-term memory creation

---

## 8. Completion Criteria (Phase 5 Overall)

Phase 5 can be considered complete when:

- [x] Single job ↔ single resume comparison
- [x] Explicit text-only comparison
- [x] Read-only analysis
- [x] Markdown output

---

## Design Principle Reminder

> **Phase 5 surfaces information, not conclusions.**  
> **It enables reflection, not decisions.**  
> **People remain the authority.**

---

## 9. Phase 5.1.1 — Interface Constraint (Design Lock)

**Initial implementation is CLI-first.**

- [x] User supplies job text (paste or file)
- [x] User supplies resume text (paste or file)
- [x] Output is a single Markdown report
- [x] No UI, browser automation, or background processing
- [x] No persistence of job or resume content

This constraint exists to:
- Preserve transparency
- Enable fast iteration
- Avoid premature UI or plugin coupling

Future interfaces (UI, plugin, chat-based) must preserve
all Phase 5 invariants before being considered.

---

## 10. Phase 5.1.1 — Evidence Highlighting (COMPLETE)

- [x] CLI-first flow remains unchanged
- [x] Explicit requirement → resume line matching only
- [x] No inference or paraphrasing
- [x] Evidence shown via quoted resume lines
- [x] Missing evidence labeled as “not visible”
- [x] Neutral, observational copy enforced
- [x] Output rendered as human-readable Markdown
- [x] No scoring, ranking, or recommendations introduced

**Invariant:**  
This phase surfaces *visibility*, not capability.

---

## Phase 5.2 — Evidence Classification (DESIGN LOCKED)

Status: 🔒 Specification complete  
Scope: Text-only classification of evidence types  
Code: Not yet written

---

## 11. Phase 5 Completion Criteria (Overall)

Phase 5 may advance to LLM-assisted steps **only after**:

- [x] Phase 5.2 evidence classification is design-locked
- [x] Phase 5.3 language guardrails are specified
- [ ] All outputs remain reversible and user-controlled
- [ ] No automated conclusions are introduced

---

### Phase 5.3 — Language Guardrails (Design Lock)

- [x] Allowed language patterns documented
- [x] Disallowed language explicitly enumerated
- [x] Artifact-anchored phrasing enforced
- [x] No judgment / no advice / no authority claims
- [x] Forward-looking LLM participation contract defined

---

## Phase 5.5 — LLM Shadow Mode (Design Locked)

Purpose:  
Allow LLMs to participate **invisibly** for evaluation and comparison, without influencing user-visible behavior or system state.

- [x] Define Shadow Mode as non-user-visible
- [x] LLM output must never override deterministic output
- [x] No persistence of LLM output
- [x] No personalization or inference
- [x] All behavior gated behind prior Phase 5 invariants
- [x] Explicitly prohibit recommendations, judgments, or predictions

Status: 🔒 Design locked (no code)

---

## Phase 5.5.1 — Prompt Test Harness (Design Locked)

Purpose:  
Treat prompts as testable artifacts and prevent silent drift before any LLM output reaches users.

- [x] Define deterministic output as the source of truth
- [x] Require explicit prompt templates (versioned, static text)
- [x] Specify guardrail constraints evaluated outside the model
- [x] Compare LLM output against deterministic baseline
- [x] Categorize results (aligned / divergent / violation)
- [x] Discard outputs that violate guardrails
- [x] Prohibit automatic promotion of prompt changes

Status: 🔒 Design locked (no code)

---

### Phase 5 Boundary Reminder

> No LLM output may be user-visible, persisted, or action-driving
> until **explicit human approval gates** are introduced.

Next eligible phase: **Phase 5.6 — Human Approval & Escalation Gate**

---

## Phase 5.6 — Human Approval Gate (Design Locked)

[ ] Deterministic output is always generated and shown **before** any AI-generated content  
[ ] AI-generated content is clearly labeled as such and never presented as authoritative  
[ ] AI output is surfaced only as **explicit proposals**, never auto-applied  

### Proposal Object & State Model

[ ] Every AI-generated suggestion is wrapped in a **Proposal object**  
[ ] Proposal object includes, at minimum:
  - `proposal_id` (unique per proposal instance)
  - `source` (must be `"llm"`)
  - `context` (descriptive reason for proposal existence)
  - `generated_at` timestamp (audit/debug only)
  - `status`
  - `content.text` (exact AI-generated text)

[ ] Proposal may exist in **exactly one** state:
  - `pending`
  - `accepted`
  - `edited`
  - `rejected`

[ ] No proposal may skip `pending`  
[ ] No proposal may auto-transition  
[ ] Acceptance does not imply correctness  
[ ] Rejection does not imply error  

### Approval Semantics

[ ] User must explicitly choose one of:
  - Accept (use proposal verbatim as user-authored content)
  - Edit (edited result becomes user-authored; original proposal discarded)
  - Reject (proposal discarded with no downstream effect)

[ ] No inference is made from acceptance, editing, or rejection  
[ ] No preference, skill level, or intent is inferred from user choice  

### Persistence & Learning Constraints (Hard)

[ ] Proposal objects are **ephemeral only**
[ ] Proposals may exist only in-session or local transient state  
[ ] No proposal is stored after the interaction ends  
[ ] No proposal outcome is reused, replayed, or learned from  
[ ] No aggregation of approvals or rejections is permitted  
[ ] Deleting local state fully resets the system  

### Apply Semantics

[ ] “Apply” means copying text into a **user-controlled output** (file/stdout buffer)  
[ ] The system never sends, submits, or applies content on the user’s behalf  

### Explicit Non-Goals (Reaffirmed)

[ ] No resume scoring  
[ ] No suitability judgments  
[ ] No career advice  
[ ] No automated application steps  
[ ] No long-term memory or personalization  

Any expansion of state, persistence, inference, or automation requires:
[ ] A new phase  
[ ] A new written spec  
[ ] Explicit design lock before implementation

---

## Design Principle Reminder

> **Phase 5 surfaces information, not conclusions.**  
> **It enables reflection, not decisions.**  
> **People remain the authority.**
