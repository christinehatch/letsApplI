# Phase 5.7 Checklist — Controlled Proposal Generation

## Status

[ ] Not started  
[ ] In progress  
[x] **Design-locked (no code permitted beyond this point)**

---

## Scope Confirmation

[x] Phase 5.7 introduces **proposal generation only**  
[x] Phase 5.6 approval and apply semantics remain unchanged  
[x] No persistence, learning, or automation is introduced  
[x] All AI output remains optional and non-authoritative  

---

## Entry Conditions (All Required)(⏳ Deferred)

[⏳] Deterministic analysis (Phase 5.1+) completes before any generation  
[⏳] Proposal generation cannot occur if deterministic analysis fails  
[⏳] User must explicitly request proposal generation  
[⏳] No background or automatic proposal generation exists  
[⏳] Generation request cannot be inferred from ambiguous input  

---

## Generation Context Enforcement (Partially ⏳ Deferred)

[x] Every generation request declares an explicit context  
[x] Context describes *why* the proposal exists, not *what the user should do*  
[⏳] Vague or overly broad contexts are rejected  
[⏳] Generation does not proceed without a declared context  

---

## LLM Participation Constraints (Partially ⏳ Deferred)

[x] LLM is invoked **only after** deterministic output is shown  
[x] LLM output is descriptive, not prescriptive  
[x] LLM output contains no evaluative or ranking language  
[⏳] Forbidden language is blocked or causes generation abort  
[⏳] LLM output does not assert correctness or outcomes  

---

## Proposal Object Requirements

[x] Every generated suggestion is wrapped in a Proposal object  
[x] Proposal object uses the Phase 5.6 schema  
[x] Proposal enters the system in `pending` state  
[x] Proposal text is passed unchanged into Phase 5.6  
[x] Proposal includes explicit context metadata  

---

## Human Approval Gate Integrity (Phase 5.6)

[x] All generated proposals pass through Phase 5.6 unchanged  
[x] No proposal is auto-approved or pre-applied  
[x] Accept / Edit / Reject behavior is unchanged  
[x] Apply semantics remain user-controlled and explicit  

---

## Ephemerality & Memory Guarantees

[x] Generated proposals are ephemeral  
[x] No proposal text is stored beyond the current interaction  
[x] No proposal metadata is persisted  
[x] No aggregation of accept/edit/reject outcomes occurs  
[x] No learning from user behavior or choices  

---

## Failure & Abort Behavior (⏳ Deferred)

[⏳] Generation aborts if any entry condition fails  
[⏳] Generation aborts if guardrail validation fails  
[⏳] No partial or degraded AI output is shown  
[⏳] No Proposal object is created on abort  

---

## Auditability & Transparency

[x] All AI-generated content is clearly labeled  
[x] Deterministic output is visually and structurally distinct from AI output  
[x] A user can answer: “Why does this proposal exist?”  
[x] No hidden control flow or background execution exists  

---

## Explicit Non-Goals (Re-Verified)

[x] No resume scoring  
[x] No candidate ranking  
[x] No suitability judgments  
[x] No “you should apply” recommendations  
[x] No personalization or preference modeling  
[x] No automated application actions  

---

## Design Lock Confirmation

[x] Phase 5.7 introduces **generation capability only**  
[x] Any expansion requires a new phase and charter  
[x] No code may be written until this checklist is satisfied and locked  

---

## Guiding Question (Final Check)

[x] If proposal generation disappeared tomorrow, the user would **not lose agency**

If unchecked, **Phase 5.7 is invalid**.

---

**End of Phase 5.7 Checklist**

