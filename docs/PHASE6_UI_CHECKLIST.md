# Phase 6 — Hydration & Exploration UI Checklist (Current Status)

This checklist defines the **non-negotiable UI requirements** for Phase 6.

Unchecked items are **intentional deferrals** and do not represent design gaps.

---

## 1. Side Panel Presence & Layout

- [ ] Side panel opens when a discovered job is selected
- [ ] Side panel is positioned adjacent to the job content (not overlaying it)
- [ ] Side panel width is constrained (approx. 360–420px)
- [ ] Side panel scrolls independently of the job page
- [ ] Job content is never rendered inside the side panel
- [ ] Side panel remains open while the job is viewed

> **Note:** Side panel components exist, but are not yet integrated with a live
> job viewing surface. These will be checked upon integration.

---

## 2. Global Panel Header (Always Visible)

- [ ] Header is always visible, regardless of panel state
- [ ] Header displays current phase (e.g. “Phase 6 — Viewing”)
- [ ] Header does not imply analysis or interpretation
- [ ] Header contains no job-derived content

> **Note:** `PhaseHeader` is implemented but global visibility guarantees
> cannot be verified until the panel is mounted in the app shell.

---

## 3. Viewing State (S1 — Default)

- [x] The following text appears prominently and verbatim:

  > **You are viewing this job.**  
  > **I have not read or interpreted it.**

- [x] Supporting explanation is visible or expandable:

  > This page is shown exactly as published by the company.  
  > I do not have access to its contents unless you explicitly allow it.

- [x] No job summary, highlights, or extracted data are shown
- [x] No AI-generated interpretation appears in this state

---

## 4. Optional Role Orientation (S2)

Triggered only by explicit user action.

- [x] Orientation is not shown automatically
- [x] Orientation content replaces the viewing body (header remains)
- [x] The following disclaimer appears verbatim and first:

  > I have not read this job.  
  > This is a general description based only on the job title.

- [ ] Orientation content is derived only from role archetypes
- [x] Orientation content makes no claims about the specific job
- [x] Orientation can be dismissed without side effects
- [x] Orientation does not persist across jobs

> **Note:** Orientation is currently title-based. Archetypes are v0 /
> conceptual and will be finalized later.

---

## 5. Consent Request State (S3)

Triggered only by explicit user action.

- [x] Consent prompt is clearly framed as a question
- [x] The system explains what reading enables
- [x] The system explicitly states what it will NOT do automatically
- [x] Scope clarification is present:

  > This permission applies only to this job.

- [x] “Confirm and allow reading” is clearly distinguishable from cancel
- [x] No reading occurs before confirmation

---

## 6. Consent Granted Transition (S4)

- [x] Confirmation state is brief and explicit
- [x] The following text appears:

  > Permission granted.  
  > I am now allowed to read this job.

- [x] No automatic analysis or output is triggered
- [x] Control passes explicitly to Phase 5.1 behavior

---

## 7. Exit & Abort Handling (S5)

- [ ] Explicit UI exists to abort and return to discovery
- [ ] Failure to load job content is clearly communicated
- [ ] Failure does not advance the system into interpretation

> **Note:** Exit and failure handling depend on a concrete job rendering
> surface and are intentionally deferred.

---

## Phase 6 UI Status

- Phase 6 UI is **internally complete and state-locked**
- All unchecked items are **integration-dependent**
- No unchecked item permits silent reading, interpretation, or AI involvement
