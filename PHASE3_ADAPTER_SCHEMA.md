# Phase 3.5 — Adapter Job Schema

This document defines the expected structure of job objects
returned by source adapters in Phase 3.

This is a rendering contract, not a storage or ranking model.

---

## Required Fields (all adapters)

Every adapter MUST return these fields:

- `source` (str)
- `title` (str)
- `company` (str)
- `location` (str)
- `first_seen_at` (datetime)

These fields are required for prioritization and rendering.

---

## Optional Fields (adapter-dependent)

Adapters MAY return additional fields.

Known optional fields:

- `url` — canonical job posting link
- `source_job_id` — stable external identifier
- `referral` — human-provided referral note

The renderer must treat all optional fields as non-guaranteed.

---

## Renderer Rules

- The renderer MUST NOT assume optional fields exist
- Optional fields must be accessed via `job.get(...)`
- Absence of optional fields must not cause errors
- Rendering should omit unavailable sections silently

---

## Versioning Notes

- Phase 3 adapters may return heterogeneous schemas
- Schema unification or enforcement is deferred to Phase 4

