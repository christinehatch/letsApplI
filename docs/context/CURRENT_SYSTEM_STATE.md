# CURRENT_SYSTEM_STATE

## SYSTEM OVERVIEW

letsA(ppl)I is a job exploration system with the following pipeline:

Discovery  
→ Hydration  
→ Phase 5.2 Interpretation  
→ Validation  
→ UI exploration

## CURRENT WORKING COMPONENTS

### Discovery Engine
- Provider adapters ingest job metadata.
- Jobs stored in JobsRepo.
- Discovery feed API: `/api/discovery-feed`.

### Hydration (Phase 5.1)
- Endpoint: `/api/hydrate-job`.
- Retrieves full job content.
- Stores hydrated content.

### Interpretation (Phase 5.2)
- Endpoint: `/api/interpret-manual`.
- Interpreter builds `span_map`.
- LLM produces structured interpretation.
- Validators enforce rules:
  - schema
  - grounding
  - actor neutrality

### AI Relevance
- Extracted from interpretation signals.
- Returned with job interpretation.
- Used for UI badges and filtering.

### Saved Jobs
- Save button in feed.
- Saved jobs board.
- Status transitions:
  - saved
  - applied
  - ignored
  - archived

### Market Alignment
- Resume signals stored in:
  - `state/resume_signals.json`
- Endpoint:
  - `/api/market-alignment`
- Counts how many discovery jobs contain resume signals.

## CURRENT UI STRUCTURE

### Left Panel
- Filters.
- Feed controls.
- No longer renders job cards.

### Center Panel
- Market Alignment dashboard.
- Clicking a signal filters the discovery feed.
- Job cards appear when a signal filter is active.

### Right Panel
- Job interpretation view.
