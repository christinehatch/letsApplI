# Phase 6 — Hydration & Exploration UI Checklist

This checklist defines the **non-negotiable UI requirements** for Phase 6.

If an item is unchecked, Phase 6 is not complete.

This checklist governs **layout, state visibility, copy placement, and interaction boundaries**.
It does not describe implementation details or styling preferences.

---

## 1. Side Panel Presence & Layout

- [ ] Side panel opens when a discovered job is selected
- [ ] Side panel is positioned adjacent to the job content (not overlaying it)
- [ ] Side panel width is constrained (approx. 360–420px)
- [ ] Side panel scrolls independently of the job page
- [ ] Job content is never rendered inside the side panel
- [ ] Side panel remains open while the job is viewed

---

## 2. Global Panel Header (Always Visible)

- [ ] Header is always visible, regardless of panel state
- [ ] Header displays current phase (e.g. “Phase 6 — Viewing”)
- [ ] Header does not imply analysis or interpretation
- [ ] Header contains no job-derived content

---

## 3. Viewing State (S1 — Default)

- [ ] The following text appears prominently and verbatim:

  > **You are viewing this job.**  
  > **I have not read or interpreted it.**

- [ ] Supporting explanation is visible or expandable:

  > This page is shown exactly as published by the company.  
  > I do not have access to its contents unless you explicitly allow it.

- [ ] No job summary, highlights, or extracted data are shown
- [ ] No AI-generated interpretation appears in this state

---

## 4. Optional Role Orientation (S2)

Triggered only by explicit user action.

- [ ] Orientation is not shown automatically
- [ ] Orientation content replaces the viewing body (header remains)
- [ ] The following disclaimer appears verbatim and first:

  > I have not read this job.  
  > This is a general description based only on the job title.

- [ ] Orientation content is derived only from role archetypes
- [ ] Orientation content makes no claims about the specific job
- [ ] Orientation can be dismissed without side effects
- [ ] Orientation does not persist across jobs

---

## 5. Consent Request State (S3)

Triggered only by explicit user action.

- [ ] Consent prompt is clearly framed as a question
- [ ] The system explains what reading enables
- [ ] The system explicitly states what it will NOT do automatically
- [ ] Scope clarification is present:

  > This permission applies only to this job.

- [ ] “Confirm and allow reading” is clearly distinguishable from cancel
- [ ] No reading occurs before confirmation

---

## 6. Consent Granted Transition (S4)

- [ ] Confirmation state is brief and explicit
- [ ] The following text appears:

  > Permission granted.  
  > I am now allowed to read this job.

- [ ] No automatic analysis or output is triggered
- [ ] Control passes explicitly to Phase 5.1 behavior

---

## 7. Exit & Abort Handling (S5)

