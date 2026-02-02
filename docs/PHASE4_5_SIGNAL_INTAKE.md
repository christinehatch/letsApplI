
## Purpose

Phase 4.5 introduces **job discovery and monitoring** without interpretation.

It exists to:
- remove repetitive searching from users
- preserve determinism
- respect site boundaries

---

## Scope

Phase 4.5 includes:
- Job discovery
- Change detection
- User notification

Phase 4.5 explicitly excludes:
- Resume analysis
- Fit assessment
- AI generation

---

## Entry Conditions

[🟡] User explicitly subscribes to:
- a company
- a domain
- or a role category

[🟡] No discovery occurs without user intent
🟡 Functionally met, UX not locked

---

## Allowed Inputs

[x] Sitemap files  
[x] Public job search APIs  
[x] Aggregator feeds  
[x] HTTP HEAD existence checks  

---

## Prohibited Inputs

[x] JS-rendered content  
[x] Authenticated endpoints  
[x] Scraped descriptions  
[x] Browser automation  

---

## Output Guarantees

[x] Jobs are recorded as **Discovered only**  
[x] No interpretation is attached  
[x] No AI involvement  
[x] No ranking or filtering beyond user criteria  

---

## Failure Handling

[x] If a source blocks access → mark unavailable  
[x] No spoofing, retries, or circumvention  
[x] Failures are logged, not hidden  

---

## User Experience

[x] User is notified of new discoveries  
[x] Notification includes:
- company
- title
- link

[x] User must explicitly request hydration

---

## Design Lock

Phase 4.5 **must remain deterministic**.

If discovery fails, the system:
> does nothing rather than guessing.


# Phase 4.5 — Role Archetypes Checklist

## Specification
- [x] Archetype purpose defined (pre-hydration only)
- [x] Explicit non-goals documented
- [x] Canonical archetype set defined
- [x] Archetypes describe modes of work, not domains
- [x] UNKNOWN behavior explicitly specified
- [x] Relationship to Phase 5 documented

## Matching Logic
- [x] Deterministic, ordered rules
- [x] First-match-wins behavior defined
- [x] Title-only input enforced
- [x] No probabilistic or AI-based matching
- [x] Matching rules implemented in code
- [x] Unknown titles handled explicitly

## UI / Output
- [x] Archetypes are optional / expandable
- [x] Archetypes do not appear as recommendations
- [x] Copy explicitly states “I have not read this job”
- [x] Summary output wired to archetype lookup
- [x] Archetype text hidden after hydration

## Guardrails
- [x] No job content read before hydration
- [x] No seniority or fit inference
- [x] No personalization
- [x] No silent behavior

