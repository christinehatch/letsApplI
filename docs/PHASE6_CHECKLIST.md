# Phase 6 — Hydration & Exploration Checklist

This checklist defines the minimum, complete scope of **Phase 6**.

Phase 6 is **human-led UX only**.
It exists to let the user view and explore a job listing
without the system silently reading or interpreting it.

Nothing in this checklist permits AI interpretation.

---

## 1. Entry Conditions

- [ ] Phase 4.5 discovery is complete and stable
- [ ] Jobs are presented as metadata-only prior to hydration
- [ ] User must explicitly select a job to enter Phase 6

---

## 2. View-Only Hydration Surface (6.0)

- [ ] User can open a job listing via an explicit action (click/select)
- [ ] Job is shown exactly as-is (raw page or raw text)
- [ ] No summarization, parsing, or extraction occurs automatically
- [ ] The job remains visible at all times during exploration

---

## 3. System State Transparency

- [ ] System explicitly states:  
  **“You are viewing this job. I have not read or interpreted it.”**
- [ ] This statement is visible and unambiguous
- [ ] There is no hidden or implied reading state

---

## 4. Optional Role Orientation (Non-Interpretive)

- [ ] Optional orientation may be shown based on:
  - job title only
  - predefined role archetypes
- [ ] Orientation text includes a disclaimer such as:  
  **“I have not read this job.”**
- [ ] Orientation is dismissible and does not block viewing
- [ ] Orientation is not persisted or treated as interpretation

---

## 5. Transition to Consent (Bridge to Phase 5.1)

- [ ] A clear action exists to request system reading, e.g.:  
  **“Allow the system to read this job”**
- [ ] No job content is read before this action
- [ ] This action explicitly invokes Phase 5.1 consent rules
- [ ] Consent is scoped to the selected job only

---

## 6. Failure & Edge-Case Handling

- [ ] If a job page cannot be loaded, the system states the limitation
- [ ] No fallback scraping, guessing, or substitution occurs
- [ ] Failure does not advance the system into interpretation

---

## 7. Explicit Non-Goals (Guardrails)

- [ ] No AI summaries by default
- [ ] No fit assessment
- [ ] No resume comparison
- [ ] No recommendations
- [ ] No ranking or scoring
- [ ] No persistence of interpretations

---

## Phase 6 Exit Criteria

Phase 6 is complete when:

- [ ] A user can open and view a job listing
- [ ] The system clearly communicates that it has not read the job
- [ ] Optional orientation is available but bounded
- [ ] A clear, explicit transition to Phase 5.1 consent exists
- [ ] No AI interpretation occurs without user intent

If all boxes above are checked, Phase 6 is complete.

