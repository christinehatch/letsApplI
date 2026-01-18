# Phase 5.7 Checklist — Controlled Proposal Generation

## Status

☐ Not started  
☐ In progress  
☐ **Design-locked (no code permitted beyond this point)**

---

## Scope Confirmation

☐ Phase 5.7 introduces **proposal generation only**  
☐ Phase 5.6 approval and apply semantics remain unchanged  
☐ No persistence, learning, or automation is introduced  
☐ All AI output remains optional and non-authoritative  

---

## Entry Conditions (All Required)

☐ Deterministic analysis (Phase 5.1+) completes before any generation  
☐ Proposal generation cannot occur if deterministic analysis fails  
☐ User must explicitly request proposal generation  
☐ No background or automatic proposal generation exists  
☐ Generation request cannot be inferred from ambiguous input  

---

## Generation Context Enforcement

☐ Every generation request declares an explicit context  
☐ Context describes *why* the proposal exists, not *what the user should do*  
☐ Vague or overly broad contexts are rejected  
☐ Generation does not proceed without a declared context  

---

## LLM Participation Constraints

☐ LLM is invoked **only after** deterministic output is shown  
☐ LLM output is descriptive, not prescriptive  
☐ LLM output contains no evaluative or ranking language  
☐ Forbidden language is blocked or causes generation abort  
☐ LLM output does not assert correctness or outcomes  

---

## Proposal Object Requirements

☐ Every generated suggestion is wrapped in a Proposal object  
☐ Proposal object uses the Phase 5.6 schema  
☐ Proposal enters the system in `pending` state  
☐ Proposal text is passed unchanged into Phase 5.6  
☐ Proposal includes explicit context metadata  

---

## Human Approval Gate Integrity (Phase 5.6)

☐ All generated proposals pass through Phase 5.6 unchanged  
☐ No proposal is auto-approved or pre-applied  
☐ Accept / Edit / Reject behavior is unchanged  
☐ Apply semantics remain user-controlled and explicit  

---

## Ephemerality & Memory Guarantees

☐ Generated proposals are ephemeral  
☐ No proposal text is stored beyond the current interaction  
☐ No proposal metadata is persisted  
☐ No aggregation of accept/edit/reject outcomes occurs  
☐ No learning from user behavior or choices  

---

## Failure & Abort Behavior

☐ Generation aborts if any entry condition fails  
☐ Generation aborts if guardrail validation fails  
☐ No partial or degraded AI output is shown  
☐ No Proposal object is created on abort  

---

## Auditability & Transparency

☐ All AI-generated content is clearly labeled  
☐ Deterministic output is visually and structurally distinct from AI output  
☐ A user can answer: “Why does this proposal exist?”  
☐ No hidden control flow or background execution exists  

---

## Explicit Non-Goals (Re-Verified)

☐ No resume scoring  
☐ No candidate ranking  
☐ No suitability judgments  
☐ No “you should apply” recommendations  
☐ No personalization or preference modeling  
☐ No automated application actions  

---

## Design Lock Confirmation

☐ Phase 5.7 introduces **generation capability only**  
☐ Any expansion requires a new phase and charter  
☐ No code may be written until this checklist is satisfied and locked  

---

## Guiding Question (Final Check)

☐ If proposal generation disappeared tomorrow, the user would **not lose agency**

If unchecked, **Phase 5.7 is invalid**.

---

**End of Phase 5.7 Checklist**

