# AGENTS.md

## System Overview

letsA(ppl)I is a deterministic, consent-first job discovery and analysis system.

Core flow:

Discovery
→ Hydration
→ Structured Interpretation
→ Personal Job Pipeline

From Milestone 6, a user-owned **Profile** sits beside this flow and is used
to recommend roles and, on request, to show how a role lines up with the user.

The architecture deliberately separates responsibilities:

- Discovery: finding jobs
- Hydration: reading jobs
- Interpretation: understanding jobs
- Profile: what the user has chosen to tell the system about themselves
- Matching: setting a role beside the profile, with evidence
- User pipeline: tracking applications

Agents must not merge these responsibilities.

## Architectural Principles

AI agents must follow these rules:

- Deterministic architecture is preferred over automation.
- No background AI actions.
- All AI analysis must be user-initiated (reading a profile source, interpreting
  a role, vetting a role).
- Hydration and interpretation are separate steps.
- Interpreter and extractor outputs are untrusted and must be validated.
- Matching must be explainable: every match or vetting item cites the profile
  fact and the posting text it rests on. No unexplained score, percentage or
  grade is ever shown.
- The system never rates the person. It describes overlap and gaps between a
  posting and the profile, in neutral language.
- Profile data is added by the user, proposed before it is stored, visible with
  its source, editable, and deletable.

The system focuses on role understanding and explainable alignment, not
applicant ranking. See `docs/PROFILE_PLAN.md` for the full reasoning behind
this rule change (2026-11-17).

## Current Milestone Status

- Milestone 1 — Job Discovery (Complete)
- Milestone 2 — Job Hydration (Complete)
- Milestone 3 — Job State Persistence (Complete)
- Milestone 4 — Pipeline UI / Kanban (Complete)
- Milestone 5 — Structured Job Interpretation (Complete: `Phase52Interpreter`,
  validator, `job_interpretations` persistence and reuse, interpretation
  endpoint, Role Snapshot UI)
- Milestone 6 — Personal Profile & Recommendations (Next; plan in
  `docs/PROFILE_PLAN.md`)

Agents implementing Milestone 6 should follow the step order in
`docs/PROFILE_PLAN.md` §6 and add, step by step:

- Profile tab and local source storage (no AI)
- User-triggered source reading with proposed, quoted facts and a validator
- Deterministic profile → saved-search recommendations with "why this showed up"
- Sidebar redesign around the profile
- User-triggered role vetting with a citation-and-language validator
- applyAI return path (requires handoff contract v2 first)

## Boundaries

Agents must NOT:

- automatically run AI on jobs or on profile sources
- add profile data the user didn't provide or confirm
- infer personality types or identity labels
- show a fit score, percentage, grade or ranking number
- call the user qualified, unqualified, strong or weak
- generate career advice or tell the user whether to apply
- alter pipeline states automatically
- log in to or scrape LinkedIn or other sites the user didn't name

All AI interpretation and vetting must be explicitly triggered by the user.
