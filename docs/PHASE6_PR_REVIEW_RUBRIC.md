# Phase 6 — PR Review Rubric (Hydration & Exploration)

This rubric governs **all pull requests that modify or introduce Phase 6 behavior or UI**.

A PR must pass **every applicable check** to be approved.

If a change fails a check, it must be rejected or revised — even if it appears useful.

---

## 0. Scope Check (Gate 0)

Before reviewing details, confirm:

- [ ] The PR explicitly states it affects Phase 6
- [ ] The PR does not introduce Phase 5 behavior
- [ ] The PR does not collapse Phase 6 into Phase 5

If unclear, request clarification **before** continuing.

---

## 1. Epistemic Integrity (Highest Priority)

Phase 6 exists to preserve *what the system does not know*.

Reject the PR if **any** of the following are true:

- [ ] The system reads job content without explicit consent
- [ ] The system implies it has read the job when it has not
- [ ] The system generates summaries, highlights, or interpretations
- [ ] The system extracts requirements, skills, or responsibilities
- [ ] The system references job content before Phase 5.1 entry

**Pass condition:**  
The system remains visibly ignorant until the user explicitly changes that state.

---

## 2. UI Boundary Enforcement

Confirm strict separation between surfaces:

- [ ] Job content is rendered only in the main content area
- [ ] System UI never overlays, annotates, or modifies job content
- [ ] Side panel contains no job-derived text or structure
- [ ] No DOM parsing or injection occurs in Phase 6

Reject if job content and system UI are visually or logically merged.

---

## 3. State Visibility & Transitions

Phase 6 state must be **visible, explicit, and user-controlled**.

Check that:

- [ ] Current phase/state is visible in the UI
- [ ] State transitions are triggered only by user action
- [ ] No automatic transitions occur
- [ ] Consent is a visible, explicit step
- [ ] Phase 6 → Phase 5.1 handoff includes a pause

Reject if the system advances without user intent.

---

## 4. Trust Copy & Language Accuracy

Language is part of the system’s contract.

Confirm:

- [ ] The phrase “I have not read this job” appears verbatim in Viewing state
- [ ] Disclaimers are not paraphrased or softened
- [ ] No enthusiastic, persuasive, or suggestive language is used
- [ ] Orientation copy is clearly labeled as general and title-based
- [ ] No copy implies fit, suitability, or recommendation

Reject if copy overstates capability or certainty.

---

## 5. Orientation Behavior (Optional, Non-Interpretive)

If the PR touches role orientation:

- [ ] Orientation is user-triggered only
- [ ] Orientation is based solely on role archetypes
- [ ] Orientation does not mention the specific job
- [ ] Orientation is dismissible and non-persistent
- [ ] Orientation does not influence system state

Reject if orientation leaks interpretation.

---

## 6. Consent Handling

Consent must be scoped, reversible, and respected.

Verify:

- [ ] Consent applies to one job only
- [ ] Consent is not reused implicitly
- [ ] Consent can be revoked
- [ ] Granting consent does not trigger analysis
- [ ] User chooses when Phase 5.1 begins

Reject if consent implies action.

---

## 7. Persistence & Memory

Phase 6 must not learn or remember meaning.

Confirm:

- [ ] No interpretation is persisted
- [ ] No preferences are inferred or stored
- [ ] No orientation outcomes are saved
- [ ] Viewing alone does not alter user state

Allowed persistence is limited to:
- timestamps
- consent flags (scoped)

---

## 8. Automation & Background Work

Phase 6 must be synchronous and observable.

Reject if the PR introduces:

- [ ] Background job reading
- [ ] Prefetching or speculative analysis
- [ ] Deferred processing without user awareness
- [ ] “While you were viewing…” behavior

---

## 9. Non-Scope Enforcement

Confirm the PR does **not** introduce:

- [ ] Resume interaction
- [ ] Fit scoring or match language
- [ ] Job ranking or prioritization
- [ ] Recommendations or nudges
- [ ] AI-generated summaries

If any appear, the PR is out of scope.

---

## 10. Reviewer Verdict

Approve **only if**:

- [ ] All relevant sections pass
- [ ] No ambiguity exists about what the system knows
- [ ] The user remains in control of meaning-making
- [ ] Phase boundaries are preserved

When in doubt, **reject or request changes**.

---

## Final Reviewer Rule

> If a change makes Phase 6 feel “more helpful”  
> at the cost of clarity, restraint, or consent,  
> **it is incorrect.**
# Phase 6 — PR Review Rubric (Hydration & Exploration)

This rubric governs **all pull requests that modify or introduce Phase 6 behavior or UI**.

A PR must pass **every applicable check** to be approved.

If a change fails a check, it must be rejected or revised — even if it appears useful.

---

## 0. Scope Check (Gate 0)

Before reviewing details, confirm:

- [ ] The PR explicitly states it affects Phase 6
- [ ] The PR does not introduce Phase 5 behavior
- [ ] The PR does not collapse Phase 6 into Phase 5

If unclear, request clarification **before** continuing.

---

## 1. Epistemic Integrity (Highest Priority)

Phase 6 exists to preserve *what the system does not know*.

Reject the PR if **any** of the following are true:

- [ ] The system reads job content without explicit consent
- [ ] The system implies it has read the job when it has not
- [ ] The system generates summaries, highlights, or interpretations
- [ ] The system extracts requirements, skills, or responsibilities
- [ ] The system references job content before Phase 5.1 entry

**Pass condition:**  
The system remains visibly ignorant until the user explicitly changes that state.

---

## 2. UI Boundary Enforcement

Confirm strict separation between surfaces:

- [ ] Job content is rendered only in the main content area
- [ ] System UI never overlays, annotates, or modifies job content
- [ ] Side panel contains no job-derived text or structure
- [ ] No DOM parsing or injection occurs in Phase 6

Reject if job content and system UI are visually or logically merged.

---

## 3. State Visibility & Transitions

Phase 6 state must be **visible, explicit, and user-controlled**.

Check that:

- [ ] Current phase/state is visible in the UI
- [ ] State transitions are triggered only by user action
- [ ] No automatic transitions occur
- [ ] Consent is a visible, explicit step
- [ ] Phase 6 → Phase 5.1 handoff includes a pause

Reject if the system advances without user intent.

---

## 4. Trust Copy & Language Accuracy

Language is part of the system’s contract.

Confirm:

- [ ] The phrase “I have not read this job” appears verbatim in Viewing state
- [ ] Disclaimers are not paraphrased or softened
- [ ] No enthusiastic, persuasive, or suggestive language is used
- [ ] Orientation copy is clearly labeled as general and title-based
- [ ] No copy implies fit, suitability, or recommendation

Reject if copy overstates capability or certainty.

---

## 5. Orientation Behavior (Optional, Non-Interpretive)

If the PR touches role orientation:

- [ ] Orientation is user-triggered only
- [ ] Orientation is based solely on role archetypes
- [ ] Orientation does not mention the specific job
- [ ] Orientation is dismissible and non-persistent
- [ ] Orientation does not influence system state

Reject if orientation leaks interpretation.

---

## 6. Consent Handling

Consent must be scoped, reversible, and respected.

Verify:

- [ ] Consent applies to one job only
- [ ] Consent is not reused implicitly
- [ ] Consent can be revoked
- [ ] Granting consent does not trigger analysis
- [ ] User chooses when Phase 5.1 begins

Reject if consent implies action.

---

## 7. Persistence & Memory

Phase 6 must not learn or remember meaning.

Confirm:

- [ ] No interpretation is persisted
- [ ] No preferences are inferred or stored
- [ ] No orientation outcomes are saved
- [ ] Viewing alone does not alter user state

Allowed persistence is limited to:
- timestamps
- consent flags (scoped)

---

## 8. Automation & Background Work

Phase 6 must be synchronous and observable.

Reject if the PR introduces:

- [ ] Background job reading
- [ ] Prefetching or speculative analysis
- [ ] Deferred processing without user awareness
- [ ] “While you were viewing…” behavior

---

## 9. Non-Scope Enforcement

Confirm the PR does **not** introduce:

- [ ] Resume interaction
- [ ] Fit scoring or match language
- [ ] Job ranking or prioritization
- [ ] Recommendations or nudges
- [ ] AI-generated summaries

If any appear, the PR is out of scope.

---

## 10. Reviewer Verdict

Approve **only if**:

- [ ] All relevant sections pass
- [ ] No ambiguity exists about what the system knows
- [ ] The user remains in control of meaning-making
- [ ] Phase boundaries are preserved

When in doubt, **reject or request changes**.

---

## Final Reviewer Rule

> If a change makes Phase 6 feel “more helpful”  
> at the cost of clarity, restraint, or consent,  
> **it is incorrect.**

