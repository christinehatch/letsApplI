# AUDIT_NOTES.md — Systems Audit (Consent-First, Phase-Locked)

Date: 2026-02-02
Auditor stance: **Detect drift / inconsistencies / integration errors** (no redesign)

## Project invariants (non-negotiable)

* No hidden automation
* No scraping gated content
* No inference without explicit consent
* Deterministic > clever
* Discovery ≠ interpretation ≠ recommendation
* Phases are hard boundaries; earlier phases must not anticipate later ones
* UX can be rough early; correctness comes first

## Phase map (high-level)

* **Phase 3:** Discovery only (job listings + metadata)
* **Phase 5.1:** Read-only job hydration (raw content)
* **Phase 5.2:** Interpretation (classification only)
* **Phase 5.3:** Fit analysis (descriptive, not prescriptive)
* **Phase 5.4+:** Requires explicit new consent
* **Phase 6:** UX/orchestration/polish (must not change phase semantics)

---

## ✅ Fixes completed (minimal, phase-preserving)

### 1) Removed Phase 5.1 hydration from Phase 3 adapter (hard boundary)

**Problem:** Stripe Phase 3 adapter contained hydration logic and UI depended on it (cross-phase leak).
**Fix:** Hydration moved to Phase 5.1 source module; Phase 3 adapter remains discovery-only.

* Phase 5.1 hydration now lives in:
  `src/phase5/phase5_1/sources/stripe_greenhouse.py`
* Phase 3 adapter now exposes only:
  `fetch_jobs()` (plus private helpers)

### 2) Removed interpretation/orientation from discovery (Phase 3)

**Problem:** Discovery CLI included “explain roles” orientation based on titles (interpretation leak).
**Fix:** Removed `--explain-roles` flag and deleted the orientation block in discovery summarizer.

### 3) Fixed Phase 5.1 package export drift

**Problem:** `src/phase5/phase5_1/__init__.py` contained a broken stub `Phase51Reader` shadowing the real one.
**Fix:** `__init__.py` now cleanly re-exports the real `Phase51Reader`.

### 4) Ensured shadow-mode LLM import cannot break baseline behavior

**Problem:** Import-time dependency chain could break even when shadow mode was off.
**Fix:** `LLMAdapter` import is lazy + wrapped in `try/except` inside the shadow-mode branch, preserving fallback.

### 5) Stabilized execution model (deterministic entrypoints)

**Problem:** Import roots were inconsistent; running modules depended on cwd/PYTHONPATH.
**Fix:** Added repo-root entrypoints that insert `src/` on `sys.path`:

* `main.py` → discovery CLI
* `phase5_main.py` → phase5 CLI

### 6) Fixed Phase 3 spec drift re: `first_seen_at`

**Problem:** Phase 3 contract required `first_seen_at` while also claiming Phase 4 owns persistence/stability.
**Fix:** Removed `first_seen_at` from Phase 3 required fields; clarified Phase 4 assigns/stabilizes it.
Also removed `first_seen_at` from Phase 3 adapter output (contract match).

### 7) Prevented location filter drift without expanding scope

**Problem:** Location tokens were duplicated in multiple places, risking divergence.
**Fix:** Centralized Stripe-specific NorCal tokens in `src/discovery/location_filters.py` as:

* `STRIPE_NORCAL_TOKENS`
* `is_stripe_norcal(location: str) -> bool`
  Updated Stripe adapter to import/use `is_stripe_norcal` and removed local token set.

### 8) Added explicit Phase 5.1 consent gate for CLI gap analysis

**Problem:** Phase 5 CLI could read job text and run analysis without explicit “read job” consent.
**Fix:** Added `--i-consent-to-read-job` gate to `phase5 cli gap`, blocking without consent.
Also added clean file-not-found handling (no stack trace).

### 9) Aligned “explicit opt-in” language with reality for proposals

**Decision:** Env-var gate is sufficient for opt-in.
**Fix:** Updated CLI help text to state LLM generation requires `USE_LLM_SHADOW_MODE=1` (wording-only; no behavior change).

### 10) Standardized UI imports to chosen execution model

**Problem:** UI used `from src.phase5...` imports while runtime assumed `src/` on path.
**Fix:** UI now imports `phase5.*` consistently (works with repo-root entrypoints / `sys.path.insert(0, "src")`).

---

## ✅ Verification commands (passed)

From repo root:

```bash
python3 main.py summary --help
python3 phase5_main.py --help
python3 phase5_main.py gap --job /tmp/job.txt --resume /tmp/resume.txt
python3 -c "import os, sys; sys.path.insert(0,'src'); from ui.read_job import read_job_interactive; print('ui ok')"
```

---

## 🟨 Known deferred risk (intentional for now)

### R8 — Analysis consent granularity in Phase 5 CLI

Current state: `phase5 gap` requires explicit consent to **read** job text (`--i-consent-to-read-job`), but proceeds to deterministic analysis immediately after.
This may be acceptable if “running gap” is treated as implicit consent to analyze.
If stricter policy is desired later, add a second explicit gate (e.g., `--i-consent-to-analyze`).

---

## Notes on scope discipline

All changes were:

* minimal and local
* aimed at restoring **phase boundaries**, **contract alignment**, and **deterministic runability**
* no feature additions beyond explicit consent gating required to satisfy stated invariants

