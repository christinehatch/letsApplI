# letsApplI — ARCHITECTURE LOCK (Phase 5 Hardening)

Date: 2026-02-20  
Mode: Phase 5.2 HARD-LOCK (Option A)

---

## 1. System Philosophy

letsApplI is a **phase-locked, consent-first architecture**.

No phase may perform work outside its declared authority.

Hydration is not interpretation.

Consent is explicit, scoped, and emitted only by Phase 6.

---

## 2. Active Phases

### Phase 5.1 — Hydration (ACTIVE)

Responsibilities:
- Fetch job content
- Validate authority
- Return raw artifact
- Normalize availability

Explicitly forbidden:
- Interpretation
- Requirement extraction
- LLM calls
- Persistence
- Implicit inference

Endpoint:
POST `/api/hydrate-job`

Allowed scope:
"hydrate"

---

### Phase 5.2 — Interpretation (LOCKED)

Status:
Not implemented.
Not callable.
No endpoint exists.

Any interpretation must be reintroduced as:
- Separate endpoint
- Separate consent scope
- Separate UI trigger
- Separate tests

---

## 3. Phase 6 — Authority Boundary

Phase 6:
- Owns consent state
- Emits authority payload
- Does not read job content
- Does not fetch URLs
- Does not interpret content

Consent payload format:

```json
{
  "job_id": "provider:company:external_id",
  "consent": {
    "granted": true,
    "scope": "hydrate",
    "granted_at": "ISO timestamp"
  }
}
