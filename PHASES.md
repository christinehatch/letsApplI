# letsA(ppl)I — Project Phases

This document defines the **intentional, finite phases** of letsA(ppl)I.

Each phase is:
- independently valuable
- demoable on its own
- explicitly scoped to avoid automation creep

This is not a promise of future work.  
It is a **map for disciplined exploration**.

---

## Phase 0 — Output Contract & Rules (COMPLETE)

**Purpose:**  
Prove that job prioritization can be done using **explicit, inspectable rules**, producing a human-readable daily output.

**What exists:**
- A deterministic prioritization model (High / Medium / Low)
- Clear, explainable reasons for why each job appears
- A generated `DAILY_OUTPUT.md` artifact

**Explicitly not included:**
- No scraping
- No AI / LLMs
- No personalization
- No automation

**Completion criteria:**  
A stable output format that humans can reason about without trusting a black box.

---

## Phase 1 — Real Inputs via Source Adapters (COMPLETE)

**Purpose:**  
Prove the system can accept **realistic inputs** without modifying core logic.

### Phase 1.0
- Replace fake job data with a single source adapter

### Phase 1.1
- Compose multiple source adapters
- Preserve the same output contract and prioritization logic

**What exists:**
- Source adapters as isolated modules
- Composition of multiple sources via simple concatenation
- No refactors to prioritization or formatting code

**Completion criteria:**  
Adding a new source means *adding a file*, not changing the system.

---

## Phase 2 — Deterministic “Same-Day” Detection (COMPLETE)

**Purpose:**  
Make “new today” an **explicit, explainable concept**, not an assumption.

**What may be added:**
- Deterministic recency rules (timestamps, feed order, known refresh patterns)
- Clear explanation in output of *how* recency was determined

**Explicitly not included:**
- No background jobs
- No schedulers
- No heuristics without explanation

**Completion criteria:**  
Humans can understand *why* a job is considered new, even when it’s wrong.

---

## Phase 3 — Real Data Ingestion (Read-Only)

**Purpose:**  
Transition from simulated inputs to **one real, verifiable data source** without changing core logic or introducing automation.

**What may be added:**
- A single real website adapter (e.g., one company careers page)
- Read-only data fetching
- Clean mapping into the existing adapter contract
- Explicit compliance with robots.txt and ToS

**Explicitly not included:**
- No persistence
- No background jobs
- No posting-date inference
- No ranking logic inside adapters

**Completion criteria:**  
A real job source appears in `DAILY_OUTPUT.md` using the same rules and explanations as demo data.

---

## Phase 4 — State & Memory

**Purpose:**  
Improve accuracy of “first seen” detection by persisting previously observed jobs across runs.

**What may be added:**
- Local persistence (JSON or SQLite)
- Stable mapping of `{source, source_job_id → first_seen_at}`
- Deterministic rehydration of state

**Explicitly not included:**
- No ML or prediction
- No personalization
- No inferred preferences

**Completion criteria:**  
“New today” remains accurate across restarts and repeated runs.

---

## Phase 5 — Guided Human Actions

**Purpose:**  
Reduce cognitive load **after** jobs are surfaced, without automating decisions.

**Explicit non-goals:**
- Full automation
- Personality inference
- Resume scoring
- Hiring decisions
- “AI that knows you better than you know yourself”

**Completion criteria:**  
Further work would require a new charter and a new name.

Phase 5.7 is design-locked at the specification level.
No code implementing proposal generation exists yet.
Adobe requires JS rendering; deterministic fetch is unavailable.

---

## Current Status

- Phase 0: ✅ Complete
- Phase 1: ✅ Complete
- Phase 2: ✅ Complete
- Phase 3: ✅ Complete
- Phase 4: ✅ Complete
- Phase 5: ✅ Complete
- Phase 6 — Hydration & Exploration (Complete)

Phase 6 is **design-complete and behaviorally locked**. This phase establishes the consent-first UX and state machine that governs job exploration without silent reading or interpretation. Users can view job listings with explicit system transparency (“I have not read this job”), optionally access bounded, non-interpretive role orientation, and deliberately transition into Phase 5.1 consent before any reading occurs. All valid state transitions are enforced at runtime, and AI participation remains impossible without explicit user intent. Remaining unchecked items (job rendering, failure handling, and discovery integration) are intentional implementation deferrals and do not represent scope gaps.



This project is considered **demo-complete after Phase 1**.

