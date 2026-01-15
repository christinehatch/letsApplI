# Phase 3 — Real Data Ingestion (Read-Only)

## Purpose

Introduce **one real job data source** into letsA(ppl)I without:
- modifying core prioritization logic
- introducing automation
- inferring data that cannot be verified

This phase proves the system can ingest real-world job data
while preserving explainability, determinism, and human trust.

---

## Source Selection

- [x] One real company careers source selected
- [x] Source is publicly accessible without login
- [x] Source is read-only
- [x] Source scope explicitly constrained

**Selected source:** Stripe Careers (Greenhouse-backed)  
**Scope constraint:** Explicit location strings only (no inference)

---

## Compliance & Access

- [x] robots.txt checked for relevant endpoints
- [x] No login, cookies, or authenticated requests required
- [x] No JS execution or headless browser use
- [x] Read-only GET requests only
- [x] Public JSON endpoint verified

If access is disallowed at any point, Phase 3 stops.

---

## Adapter Contract

- [x] Adapter lives in `src/sources/`
- [x] Adapter is read-only
- [x] Adapter returns a list of job dicts
- [x] Adapter does not modify or rank jobs
- [x] Adapter maps external data into normalized schema

### Required job fields
- `source`
- `title`
- `company`
- `location`
- `first_seen_at`

### Optional job fields
- `url`
- `source_job_id`
- `referral`

### Explicitly disallowed
- Posting date inference
- “Likely new” heuristics
- Ranking logic
- Persistence
- Automation

---

## Location Rules (Explicit)

- Location handling is **string-based only**
- No geocoding
- No ZIP inference
- No regional assumptions

Filtering relies only on exact strings provided by the source.

---

## Rendering & UX

- [x] Real jobs appear in `DAILY_OUTPUT.md`
- [x] Output format unchanged
- [x] “First observed” language clarified
- [x] Clickable job links rendered when available
- [x] Missing optional fields handled safely

---

## Schema Stability (Phase 3.5)

- [x] Minimum adapter schema defined
- [x] Optional fields documented
- [x] Renderer made defensive
- [x] Fixtures added for each adapter

---

## Completion Criteria

Phase 3 is complete when:
- A real job source appears in output
- The system remains deterministic and explainable
- No automation or persistence is introduced
- Schema expectations are explicit

**Status:** ✅ Complete
