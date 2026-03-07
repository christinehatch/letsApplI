# AGENTS.md

## System Overview

letsA(ppl)I is a deterministic, consent-first job discovery and analysis system.

Core flow:

Discovery
→ Hydration
→ Structured Interpretation
→ Personal Job Pipeline

The architecture deliberately separates responsibilities:

- Discovery: finding jobs
- Hydration: reading jobs
- Interpretation: understanding jobs
- User pipeline: tracking applications

Agents must not merge these responsibilities.

## Architectural Principles

AI agents must follow these rules:

- Deterministic architecture is preferred over automation.
- No background AI actions.
- All analysis must be user-initiated.
- Hydration and interpretation are separate steps.
- Interpreter outputs are untrusted and must be validated.
- No candidate evaluation or job-fit scoring.

The system focuses on role understanding, not applicant ranking.

## Current Milestone Status

- Milestone 1 — Job Discovery (Complete)
- Milestone 2 — Job Hydration (Complete)
- Milestone 3 — Job State Persistence (Complete)
- Milestone 4 — Pipeline UI / Kanban (Complete)
- Milestone 5 — Structured Job Interpretation (Next)

Agents implementing Milestone 5 should add:

- `Phase52Interpreter`
- `Phase52Validator`
- `job_interpretations` persistence
- interpretation API endpoint
- UI rendering of structured role analysis

## Boundaries

Agents must NOT:

- automatically analyze jobs
- generate career advice
- evaluate candidate fit
- alter pipeline states automatically

All interpretation must be explicitly triggered by the user.
