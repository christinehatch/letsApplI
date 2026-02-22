# Phase 5.2 Unlock Plan
## Consent-Gated Interpretation Layer

---

# Status

Current state: **HARD LOCKED**

- `Phase52Interpreter.interpret()` raises `NotImplementedError`
- All guard tests pass
- Phase 5.3 expects legacy `InterpretationResult` schema
- No interpretation endpoint exists
- No interpretation consent scope exists

Unlocking Phase 5.2 requires coordinated schema + boundary changes.

This document defines the migration path.

---

# Objective

Enable structured, consent-gated reasoning over hydrated job content.

Phase 5.2 must:

- Accept only Phase 5.1 output
- Require explicit interpretation consent
- Perform no reading or fetching
- Perform no persistence
- Remain traceable to a Phase 5.1 read event
- Maintain invariant enforcement

---

# Architectural Principles

1. **Hydration ≠ Interpretation**
2. **Interpretation requires explicit new consent**
3. **No implicit reasoning**
4. **No cross-phase leakage**
5. **Schema migrations must be atomic**
6. **Tests must enforce boundary contracts**

---

# Required Changes

---

## 1. Introduce Explicit Interpretation Scope

Add new consent scope:

"interpret_job_posting"


Scope matrix:

| Scope                     | Authority                         |
|---------------------------|-----------------------------------|
| hydrate                   | Fetch + return raw content        |
| interpret_job_posting     | Structured reasoning over content |

Hydration does NOT imply interpretation.

---

## 2. Create New Endpoint

Add:

POST /api/interpret-job


Requirements:

- Reject any scope != "interpret_job_posting"
- Require Phase 5.1 read timestamp
- Require raw_content
- No conditional routing
- No fallback to hydrate

Separation must be absolute.

---

## 3. Schema Migration (Atomic)

Current schema:

InterpretationResult(
   role_summary,
   requirements_analysis,
   resume_alignment,
   project_opportunities,
   confidence,
   limitations
)	


This change requires:

- Updating Phase 5.3 to consume new structure
- Updating all Phase 5.2 tests
- Updating FitAnalyzer expectations
- Removing `artifacts` field entirely
- Updating shadow tests if required

Schema change must happen in one commit.

---

## 4. Unlock Interpreter Implementation

Replace:

raise NotImplementedError


With:

Guard validation (unchanged):

- No input → InterpretationNotAuthorizedError
- Empty content → InvalidInputSourceError
- Missing read_at → InvalidInputSourceError

Then:

Deterministic extraction layer

Then:

Optional LLM reasoning layer (explicitly non-authoritative)

The interpreter must:

- Produce structured output
- Not recommend
- Not judge fit
- Not instruct user
- Not persist

---

## 5. Phase 5.3 Compatibility Update

Phase 5.3 must:

- Accept new InterpretationResult structure
- Use `requirements_analysis.explicit_requirements`
- Never infer beyond provided fields
- Remain non-prescriptive
- Continue to require explicit user material

All Phase 5.3 guard tests must be updated accordingly.

---

## 6. UI Changes

UI must:

- Add "Enable Structured Interpretation" action
- Require new consent click
- Call `/api/interpret-job`
- Render structured sections:
  - What is this role?
  - Core mission
  - Requirements breakdown
  - Resume alignment insights
  - Project ideas

UI must not:
- Automatically interpret after hydration
- Hide consent boundary

---

## 7. Revocation Semantics

Revoking interpretation consent must:

- Clear structured results
- Not clear hydrated raw content
- Reset interpretation state
- Not persist any reasoning artifacts

Future extension:
Server-side ephemeral interpretation cache purge.

---

# Testing Requirements

Before unlock:

All tests pass in hard-lock mode.

During migration:

- Phase 5.2 guard tests updated
- New interpretation tests added
- Fit analyzer tests updated
- Invariant tests must remain green
- Shadow mode tests must remain green

After unlock:

Full test suite must pass.

No skipped tests.
No partial states.

---

# Unlock Order

1. Write schema migration commit.
2. Update Phase 5.3 to new structure.
3. Update tests to reflect new schema.
4. Add new consent scope.
5. Add `/api/interpret-job` endpoint (initially locked).
6. Unlock interpreter implementation.
7. Add UI structured rendering.
8. Add integration tests.

No steps may be merged out of order.

---

# Risks

- Partial schema migration
- Scope drift
- Hidden implicit interpretation
- Fit analyzer relying on old artifacts
- LLM layer introducing prescriptive language
- UI conflating hydrate and interpret

---

# Definition of Done

Phase 5.2 is considered unlocked when:

- Interpretation requires explicit consent
- Hydration and interpretation are separate endpoints
- New structured schema is fully adopted
- Phase 5.3 is compatible
- No legacy `artifacts` references remain
- All tests pass
- Revocation works correctly
- No implicit interpretation paths exist

---

# Post-Unlock Goals

After unlock:

- Introduce structured LLM reasoning layer
- Add deterministic + model hybrid approach
- Add resume parsing phase (future Phase 5.4)
- Add project ideation engine (applyAI integration)

But those are out of scope for this unlock.

---

END OF PLAN
