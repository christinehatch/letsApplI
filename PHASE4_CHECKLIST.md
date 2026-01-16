# Phase 4 — State & Memory

## Purpose

Persist previously observed jobs so that “first observed”
timestamps remain accurate across runs.

This phase adds continuity, not intelligence.

---

## Persistence Model

- [x] Choose a local persistence format (JSON or SQLite)
- [x] Store mapping of `(source, source_job_id → first_seen_at)`
- [x] Persistence is local and inspectable
- [x] No cloud storage

---

## Pipeline Integration

- [x] Load persisted state at startup
- [x] Rehydrate `first_seen_at` for known jobs
- [x] Assign `first_seen_at` only for newly observed jobs
- [x] Persist new entries deterministically

---

## Constraints

- [x] Adapters remain read-only
- [x] No ranking logic changes
- [x] No posting-date inference
- [x] No user behavior tracking
- [x] No personalization

---

## Transparency

- [x] State file is human-readable
- [x] Deleting the state resets memory
- [ ] Memory behavior documented

---

## Completion Criteria

Phase 4 is complete when:
- “First observed” remains stable across runs
- Restarting the program does not reset history
- Behavior is deterministic and explainable

