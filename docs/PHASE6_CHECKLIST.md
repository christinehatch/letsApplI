# Phase 6 — Hydration & Exploration Checklist

This checklist defines the minimum, complete scope of **Phase 6**.

Phase 6 is **human-led UX only**.
It exists to let the user view and explore a job listing
without the system silently reading or interpreting it.

Nothing in this checklist permits AI interpretation.

---

## 1. Entry Conditions—***Deferred until integration***

- [🟡] Phase 4.5 discovery is complete and stable
- [🟡] Jobs are presented as metadata-only prior to hydration
- [🟡] User must explicitly select a job to enter Phase 6

***Phase 6 currently assumes entry from a discovery surface but is not yet wired to the live Phase 4.5 discovery UI.
The Phase 6 side panel is designed to be invoked only after explicit job selection.
These items will be checked once Phase 6 is integrated with the discovery click flow.***

---

## 2. View-Only Hydration Surface (6.0)— ***Explicitly deferred***

- [ ] User can open a job listing via an explicit action (click/select)
- [ ] Job is shown exactly as-is (raw page or raw text)
- [ ] No summarization, parsing, or extraction occurs automatically
- [ ] The job remains visible at all times during exploration

***Phase 6 defines the consent and state architecture for hydration, not the rendering mechanism.
The actual job viewing surface (new tab, iframe, Atlas side view, or raw HTML) is deferred to a subsequent phase.
No fallback scraping or intermediate parsing is permitted when this surface is implemented.***

---

## 3. System State Transparency

- [x] System explicitly states:  
  **“You are viewing this job. I have not read or interpreted it.”**
- [x] This statement is visible and unambiguous
- [x] There is no hidden or implied reading state

---

## 4. Optional Role Orientation (Non-Interpretive)

- [🟡] Optional orientation may be shown based on:
  - job title only
  - predefined role archetypes
- [x] Orientation text includes a disclaimer such as:  
  **“I have not read this job.”**
- [x] Orientation is dismissible and does not block viewing
- [x] Orientation is not persisted or treated as interpretation

---

## 5. Transition to Consent (Bridge to Phase 5.1)

- [x] A clear action exists to request system reading, e.g.:  
  **“Allow the system to read this job”**
- [x] No job content is read before this action
- [x] This action explicitly invokes Phase 5.1 consent rules
- [x] Consent is scoped to the selected job only

---

## 6. Failure & Edge-Case Handling— ***Deferred until rendering exists***

- [ ] If a job page cannot be loaded, the system states the limitation
- [ ] No fallback scraping, guessing, or substitution occurs
- [ ] Failure does not advance the system into interpretation

***Failure handling depends on the presence of a concrete job viewing surface.
Phase 6 explicitly documents non-goals and forbids fallback behaviors, but UI-level failure handling will be implemented once job rendering exists.***

---

## 7. Explicit Non-Goals (Guardrails)

- [x] No AI summaries by default
- [x] No fit assessment
- [x] No resume comparison
- [x] No recommendations
- [x] No ranking or scoring
- [x] No persistence of interpretations

---

## Phase 6 Exit Criteria— ***Partial by design***

Phase 6 is complete when:

- [ ] A user can open and view a job listing
- [x] The system clearly communicates that it has not read the job
- [x] Optional orientation is available but bounded
- [x] A clear, explicit transition to Phase 5.1 consent exists
- [x] No AI interpretation occurs without user intent

If all non-deferred boxes above are checked, Phase 6 is complete.

***Phase 6 is considered complete when the consent boundary, state machine, and non-interpretive UX are fully enforced.
The ability to view the raw job listing is deferred and does not block Phase 6 completion.***


---


## Phase 6 Completion Status (Formal)

Phase 6 is design-complete and behaviorally locked.
All remaining unchecked items are implementation dependencies, not scope gaps.
