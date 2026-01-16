# PHASE 5 — Job ↔ Evidence Gap Surfacing (Checklist)

**Status:** Design phase  
**Scope:** Read-only, user-initiated analysis  
**Non-goal:** Automation, scoring, or judgment

Phase 5 introduces guided comparison between a job posting and a user’s existing evidence (e.g., resume), while preserving user agency, neutrality, and reversibility.

This checklist defines **what Phase 5 is allowed to do, what it must never do, and the invariants that must hold before any code is written.**

---

## 1. Entry Conditions (Must Be True)

- [ ] Phase 4 is complete and locked
- [ ] Job listings are surfaced without recommendations or scoring
- [ ] User explicitly selects a single job to explore
- [ ] User explicitly provides resume or evidence (paste or file)
- [ ] No automatic processing occurs without user initiation

---

## 2. Allowed Inputs

- [ ] A single job posting chosen by the user
- [ ] User-provided resume text or document
- [ ] Optional user context (e.g., “I’m curious about this role”)

❌ Not allowed:
- External profile scraping
- Auto-imported resumes
- Historical user behavior
- Implicit preferences

---

## 3. Processing Rules (Hard Constraints)

- [ ] Compare **explicit job requirements ↔ explicit resume evidence**
- [ ] Identify:
  - Clear overlaps (mentioned in both)
  - Clear absences (mentioned in job, not present in resume)
- [ ] Do **not** infer skills, intent, seniority, or potential
- [ ] Do **not** normalize, score, rank, or weight requirements
- [ ] Do **not** guess what the user “meant” or “likely has”

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

- [ ] Neutral
- [ ] Descriptive
- [ ] Non-evaluative
- [ ] Reversible (no lasting conclusions)

Required framing examples:
- “This role mentions X; your resume includes Y.”
- “This requirement does not appear in the provided resume.”

Forbidden framing:
- “You are not qualified”
- “You should apply / shouldn’t apply”
- “This is a good / bad fit”

---

## 5. User Agency & Control

- [ ] User initiates every comparison
- [ ] User can stop or dismiss at any point
- [ ] No automatic follow-up actions
- [ ] No hidden state or memory creation
- [ ] No persistence of resume content after session ends

---

## 6. applyAI Integration Boundary

- [ ] Phase 5 may surface **optional evidence gaps**
- [ ] Gaps may be offered as **inputs** to applyAI
- [ ] applyAI must:
  - Treat gaps as *exploration prompts*, not deficits
  - Never generate identity claims (“you are X”)
  - Never imply hiring outcomes

Phase 5 does **not**:
- Generate projects automatically
- Prescribe learning paths
- Convert gaps into obligations

---

## 7. Explicitly Out of Scope (Phase 5)

Phase 5 must **not** include:

- [ ] Resume scoring or ATS optimization
- [ ] Fit percentages or rankings
- [ ] Career advice or recommendations
- [ ] Hiring likelihood predictions
- [ ] Behavioral or personality inference
- [ ] Long-term memory creation

---

## 8. Completion Criteria (Phase 5)

Phase 5 can be considered complete when:

- [ ] Checklist invariants are met
- [ ] User can explore a job → evidence comparison safely
- [ ] No automation or judgment is introduced
- [ ] applyAI integration remains optional and user-driven
- [ ] All outputs preserve human agency

---

## Design Principle Reminder

> **Phase 5 surfaces information, not conclusions.**  
> **It enables reflection, not decisions.**  
> **People remain the authority.**


