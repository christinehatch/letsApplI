
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

[ ] User explicitly subscribes to:
- a company
- a domain
- or a role category

[ ] No discovery occurs without user intent

---

## Allowed Inputs

[ ] Sitemap files  
[ ] Public job search APIs  
[ ] Aggregator feeds  
[ ] HTTP HEAD existence checks  

---

## Prohibited Inputs

[ ] JS-rendered content  
[ ] Authenticated endpoints  
[ ] Scraped descriptions  
[ ] Browser automation  

---

## Output Guarantees

[ ] Jobs are recorded as **Discovered only**  
[ ] No interpretation is attached  
[ ] No AI involvement  
[ ] No ranking or filtering beyond user criteria  

---

## Failure Handling

[ ] If a source blocks access → mark unavailable  
[ ] No spoofing, retries, or circumvention  
[ ] Failures are logged, not hidden  

---

## User Experience

[ ] User is notified of new discoveries  
[ ] Notification includes:
- company
- title
- link

[ ] User must explicitly request hydration

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
- [ ] Matching rules implemented in code
- [ ] Unknown titles handled explicitly

## UI / Output
- [x] Archetypes are optional / expandable
- [x] Archetypes do not appear as recommendations
- [x] Copy explicitly states “I have not read this job”
- [ ] Summary output wired to archetype lookup
- [ ] Archetype text hidden after hydration

## Guardrails
- [x] No job content read before hydration
- [x] No seniority or fit inference
- [x] No personalization
- [x] No silent behavior

