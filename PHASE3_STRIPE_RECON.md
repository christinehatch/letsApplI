# Phase 3.3 — Stripe Careers Source Reconnaissance

This document records the evidence used to approve Stripe Careers
as a valid Phase 3 real-data source.

This is a decision record, not a specification.

---

## Source

- Company: Stripe
- Careers platform: Greenhouse
- Access type: Public, read-only

---

## Robots.txt Verification

- Checked: https://stripe.com/robots.txt
- Result: No disallow rules for `/jobs`
- Conclusion: Read-only access to job listings is permitted

---

## Jobs Endpoint Verification

- Endpoint:
  https://boards-api.greenhouse.io/v1/boards/stripe/jobs

- Access:
  - No authentication
  - No cookies required
  - No JavaScript execution
  - GET requests only

- Response format:
  - JSON
  - Top-level `jobs` array

---

## Required Fields Confirmed

Each job object includes:

- `id` (stable Greenhouse job ID)
- `title`
- `location.name` (human-readable string)
- `absolute_url`

Additional fields (e.g. `updated_at`, `first_published`) are present
but intentionally ignored in Phase 3.

---

## Location Notes

Observed location strings include short labels (e.g. `"SF"`).

Phase 3 location filtering will use an explicit string allowlist
with no geocoding or inference.

---

## Decision

Stripe Careers satisfies all Phase 3 requirements:

- Public and read-only
- Robots-compliant
- Stable identifiers
- Clean mapping to adapter contract

Approved to proceed to Phase 3.4 (adapter implementation).

