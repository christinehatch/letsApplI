# letsA(ppl)I ↔ applyAI  
## Phase 5 Relationship & Boundary Contract

**Status:** Design-locked  
**Applies to:** letsA(ppl)I Phase 5+, applyAI Phase X  
**Audience:** Maintainers, future contributors, reviewers

---

## Purpose

This document defines the **explicit, limited integration** between:

- **letsA(ppl)I** — a read-only job discovery and prioritization tool  
- **applyAI** — a project & evidence design assistant

The goal is to:
- reduce job-search cognitive load
- surface *explicit evidence gaps*
- empower users to **create proof**, not receive prescriptions

This integration must **not** turn either system into:
- a career decision engine
- an automated evaluator
- a personalization or profiling system

---

## High-Level Model

> **letsA(ppl)I identifies evidence gaps.**  
> **applyAI helps design evidence creation.**

No other responsibilities are shared.

There is **no automatic data flow**, **no shared memory**, and **no implicit inference** across systems.

---

## letsA(ppl)I Responsibilities (Phase 5)

letsA(ppl)I remains a **read-only, rule-based system**.

It may:

- Parse job postings
- Extract explicit job requirements
- Compare requirements to **explicit resume evidence**
- Surface **evidence gaps** when no clear proof is found
- Offer an *optional* handoff to applyAI

It must **never**:

- Judge the user’s fitness for a role
- Infer skill levels
- Recommend careers, jobs, or learning paths
- Auto-generate projects or tasks
- Persist user behavior or gap history

### Example Output


