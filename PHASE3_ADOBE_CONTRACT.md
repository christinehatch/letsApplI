# Phase 3.2 — Adobe Careers Adapter Contract

This document defines the **non-negotiable contract** for the Adobe Careers
adapter introduced in Phase 3.

This is a specification, not an implementation guide.

No code should be written that violates this contract.

---

## Source Overview

- Company: Adobe
- Careers platform: Workday-backed
- Access: Public, read-only
- Scope constraint: Northern California locations only

---

## Adapter Identity

- File (Phase 3.4): `src/sources/adobe_careers.py`
- Public function: `fetch_jobs() -> list[dict]`
- Source label: `"adobe"`

---

## Job Object Contract (Phase 3)

Each job returned by the adapter MUST contain exactly these fields:

- `source`: `"adobe"`
- `source_job_id`: stable Workday-provided identifier
- `title`: job title
- `company`: `"Adobe"`
- `location`: raw location string as provided by source
- `url`: canonical job posting URL
- `first_seen_at`: datetime assigned at fetch time

No additional fields are required in Phase 3.

---

## Stable Identity Rules

- `source_job_id` must come from a Workday-provided identifier
- URLs must not be used as the primary identity unless no ID exists
- If no stable ID is available, Phase 3 stops

---

## Location Filtering Rules

- Location filtering occurs inside the adapter
- Filtering is string-based only
- No geocoding or inference

Allowed location matches include:
- San Jose, CA
- San Francisco, CA
- San Mateo, CA
- Santa Clara, CA
- Sunnyvale, CA
- Mountain View, CA
- Cupertino, CA
- Redwood City, CA
- Explicit “Northern California” labels

---

## Explicit Non-Goals

The adapter must NOT:
- Infer posting dates
- Rank jobs
- Persist state
- Execute JavaScript
- Use authentication or cookies
- Guess user intent

---

## Relationship to Other Phases

- Phase 3: real data ingestion only
- Phase 4: persistence and first_seen_at stability
- Phase 5: human interaction and guidance

This contract is intentionally minimal and conservative.

