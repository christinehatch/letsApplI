# Phase 6 — Hydration & Exploration UX Copy

This document defines the **exact language** the system is allowed to use during Phase 6.

The copy is **state-bound**.  
The system must **never** display copy from a different state.

This is not marketing copy.  
It is **system truth language**.

---

## S1 — VIEWING (Read-Only Hydration)

**Context:**  
The user has opened a job listing.  
The system has not read it.

### Primary system banner (always visible)

> **You are viewing this job.**  
> I have not read or interpreted it.

### Supporting explanation (optional, expandable)

> This page is shown exactly as published by the company.  
> I do not have access to its contents unless you explicitly allow me to read it.

### Available actions

- View job (scroll, click links)
- Close job
- *(Optional)* “What is this role generally?”

### Explicitly absent

- No summaries  
- No highlights  
- No extracted requirements  
- No opinions  

---

## S2 — ORIENTED (Optional Role Orientation)

**Context:**  
The user requested general orientation.  
The system still has not read the job.

### Orientation header

> **What is this role generally?**

### Mandatory disclaimer (must appear before content)

> I have not read this job.  
> This is a general description based only on the job title.

### Orientation body (example structure)

> Roles with this title are generally associated with:
> - \<high-level responsibility 1\>
> - \<high-level responsibility 2\>
> - \<common working context or audience\>

> Actual responsibilities vary significantly by company and team.

### Available actions

- Dismiss orientation
- Continue viewing job
- Allow the system to read this job

### Explicitly absent

- No claims about *this* job
- No fit judgments
- No seniority assumptions

---

## S3 — CONSENT_REQUESTED (Pre-Read Gate)

**Context:**  
The user indicated intent to allow system reading.  
No reading has occurred yet.

### Primary consent prompt

> **Allow the system to read this job?**

### Explanation (required)

> If you proceed, I will be allowed to read the job content and extract information such as responsibilities and requirements.  
>  
> I will not take action, make recommendations, or generate outputs without further approval.

### Scope clarification (required)

> This permission applies only to this job.

### Actions

- **Confirm and allow reading**
- Cancel

---

## S4 — CONSENT_GRANTED (Exit Phase 6)

**Context:**  
Consent has been explicitly granted.  
Phase 6 ends here.

### Transition statement

> **Permission granted.**  
> I am now allowed to read this job.

### Follow-up (non-automatic)

> Tell me what you’d like to do next.

*(At this point, Phase 5.x rules take over. No automatic behavior.)*

---

## S5 — EXITED (User Abort)

**Context:**  
The user closed the job or canceled consent.

### Exit confirmation (subtle, optional)

> This job was viewed only.  
> I did not read or interpret it.

No further messaging required.

---

## Global Copy Rules (Non-Negotiable)

Across **all Phase 6 states**:

- The system must never say “I understand this job”
- The system must never imply it has read content unless consent is granted
- The phrase **“I have not read this job”** must be used verbatim
- Copy must describe **capability**, not intention
- Silence is preferred to speculation

---

## Summary

Phase 6 UX copy exists to do three things only:

1. Tell the truth about what the system knows  
2. Make consent explicit and informed  
3. Stay out of the user’s way  

If the copy ever feels “helpful” at the cost of precision, it is wrong.

