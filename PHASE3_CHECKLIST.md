# PHASE3_CHECKLIST.md
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

**Selected source:** Adobe Careers (Workday-backed)  
**Scope constraint:** Northern California locations only

---

## Compliance & Access

- [ ] robots.txt explicitly checked for relevant endpoints
- [ ] No login, cookies, or authenticated requests required
- [ ] No JS execution or headless browser use
- [ ] Clear User-Agent identifying read-only purpose
- [ ] Conservative rate limits defined (≤ 1 req/sec)

If access is disallowed at any point, Phase 3 stops.

---

## Adapter Contract

- [ ] Adapter lives in `src/sources/`
- [ ] Adapter is read-only
- [ ] Adapter returns a list of job dicts only
- [ ] Adapter does not modify or rank jobs

### Required job fields
- `source` (e.g. `"stripe"`)
- `source_job_id` (stable per posting)
- `title`
- `company`
- `location` (string, unmodified)
- `url`
- `first_seen_at` (assigned by pipeline, not adapter)

### Explicitly disallowed
- Posting date inference
- “Likely new” heuristics
- Ranking logic
- Persistence

---

## Location Filtering Rules (Explicit)

- Location filtering is **string-based only**
- No geocoding
- No ZIP-based inference
- No “CA implies Northern CA”

Allowed matches include:
- San Jose, CA
- San Francisco, CA
- San Mateo, CA
- Santa Clara, CA
- Sunnyvale, CA
- Mountain View, CA
- Cupertino, CA
- Redwood City, CA
- “Northern California” (if explicitly labeled)

---

## Testing & Verification

- [ ] Parsing logic tested using sa


