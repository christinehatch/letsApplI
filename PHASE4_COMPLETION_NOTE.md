# Phase 4 — Complete (State & Memory)

Phase 4 is complete.

## What Phase 4 added

letsA(ppl)I now maintains a small, local, human-readable record of previously observed jobs so that “first observed” timestamps remain accurate across runs.

### Implemented

* Local JSON state file for first-seen tracking (`state/seen_jobs.json`)
* Stable job identity: `(source, source_job_id) → first_seen_at`
* Pipeline wiring: `apply_first_seen()` runs before prioritization/formatting
* Adapter schema expectation enforced (demo adapters now include `source_job_id`)

## What Phase 4 did NOT add

* No automation / background scheduling
* No personalization or preference tracking
* No inferred posting dates
* No ranking logic inside adapters

## Invariants

* “First observed” reflects when letsA(ppl)I first saw a role — not when the employer posted it
* State is local, inspectable, and removable by deleting the state file
* Only `(source, source_job_id → first_seen_at)` is stored — nothing about the user

## Completion criteria satisfied

* “New today” remains deterministic across restarts and repeated runs
* Output remains explainable and unchanged in structure (only more accurate timestamps)

