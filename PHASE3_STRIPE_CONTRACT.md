# Phase 3.2 — Stripe Careers Adapter Contract

This document defines the **non-negotiable contract** for the Stripe Careers
adapter introduced in Phase 3.

This is a **specification**, not an implementation guide.

No code should be written that violates this contract.

---

## Source Overview

* Company: **Stripe**
* Careers platform: Greenhouse (public, read-only)
* Access: Public, unauthenticated
* Scope constraint: Northern California locations only

Stripe is selected as the Phase 3 source because it exposes a
stable, documented, read-only job feed suitable for ethical ingestion.

---

## Adapter Identity

* File (Phase 3.4): `src/sources/stripe_careers.py`
* Public function: `fetch_jobs() -> list[dict]`
* Source label: `"stripe"`

The adapter must expose **exactly one public function** and must not
modify global state.

---

## Job Object Contract (Phase 3)

Each job returned by the adapter MUST contain **exactly** the following fields:

* `source`: `"stripe"`
* `source_job_id`: stable Greenhouse job identifier
* `title`: job title
* `company`: `"Stripe"`
* `location`: raw location string as provided by Greenhouse
* `url`: canonical job posting URL
* `first_seen_at`: datetime assigned at fetch time

No additional fields are required in Phase 3.

---

## Stable Identity Rules

* `source_job_id` must come from the Greenhouse-provided job ID
* URLs must not be used as the primary identifier
* If a stable ID is not present, Phase 3 stops

This identifier will be used for persistence in Phase 4.

---

## Location Filtering Rules

* Location filtering occurs **inside the adapter**
* Filtering is **string-based only**
* No geocoding
* No ZIP-code inference
* No assumptions that “CA implies Northern California”

Allowed location matches include:

* San Francisco, CA
* San Jose, CA
* San Mateo, CA
* Santa Clara, CA
* Sunnyvale, CA
* Mountain View, CA
* Cupertino, CA
* Redwood City, CA
* Explicit “Northern California” labels (if present)

If Stripe does not expose human-readable location strings,
Phase 3 stops.

---

## Adapter Behavior Rules

The adapter MUST:

* Be strictly read-only
* Return an empty list on failure
* Fail closed (no partial or guessed data)
* Avoid raising uncaught exceptions
* Avoid per-job logging

The adapter MUST NOT:

* Infer posting dates
* Rank or score jobs
* Persist state
* Execute JavaScript
* Require authentication or cookies
* Guess user intent

---

## Relationship to Other Phases

* Phase 3: real data ingestion only
* Phase 4: persistence and `first_seen_at` stability
* Phase 5: human interaction and guidance

This contract is intentionally minimal and conservative.

Any expansion requires a new phase.

