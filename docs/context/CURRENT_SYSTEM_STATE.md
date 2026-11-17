# CURRENT_SYSTEM_STATE

## System Overview

letsA(ppl)I currently runs as a deterministic job exploration product with this user-driven flow:

Discovery ingestion  
→ Feed exploration and triage  
→ Hydrated job view  
→ Optional Phase 5.2 interpretation (explicit user action only)

Core behavior remains consent-first and user-triggered for interpretation.

## Current Working Components

### Discovery and Feed
- Discovery feed endpoint: `/api/discovery-feed`.
- Optional signal filter: `/api/discovery-feed?signal=<signal>`.
- Feed search/filtering uses backend query params (role/location/experience/company/page/page_size).
- UI applies additional deterministic client filters for signals and AI toggle.

### Hydrated Job Content
- Job detail loads from discovery payload first (`description_html` / `description_text`) when available.
- Hydration is fallback when discovery content is missing.
- HTML descriptions are rendered in UI (`dangerouslySetInnerHTML`).
- In-description links are rewritten to open in a new tab with `rel="noopener noreferrer"`.

### Interpretation (Phase 5.2)
- UI uses `GET /api/job-interpretation?job_id=<id>` for analysis.
- Interpretation is no longer auto-triggered by consent or hydration state.
- Interpretation artifacts are cached in UI (`interpretationCache`, `spanMapCache`).
- Revoke flow clears interpretation state/cache and resets view to raw content.
- API includes structured handling for validation-failure responses.

### Job User State / Pipeline
- `job_user_state` drives triage and saved pipeline states.
- Discovery feed excludes non-discovery states (`ignored`, `applied`, etc.) per repository filtering.
- Saved pipeline board supports:
  - status dropdown updates
  - drag/drop status moves
  - star toggle behavior
- Skip action supported via `/api/job-ignore`.

### Deterministic Signal Infrastructure
- Greenhouse board parser uses official boards API.
- Deterministic signal classification module exists (`AI`, `DATA`, `BACKEND`, `PLATFORM`, `INFRA`).
- Signals are attached during adapter ingestion and persisted in discovery payload.

## Current UI Structure

### Left Panel (Contextual)
- `viewMode="feed"` and no selected job: filter-focused sidebar.
- `viewMode="feed"` with selected job: inbox-style job list for navigation context.
- `viewMode="saved"`: saved-job inbox list, now with local sidebar search (`company` + `title`).

### Center Panel
- Feed mode without selected job: market/discovery exploration surface with role cards and grid.
- Feed mode with selected job: sticky job header + full description view + triage controls.
- Saved mode: Saved Jobs Pipeline board with framing header and full-card drag interaction.

### Right Panel
- Phase 6 side panel for interpretation state and structured role analysis.

## Known Active Areas

- Exploration workflow polish (feed orientation, keyboard flow, reduced context loss).
- Saved pipeline UX smoothness (drag/drop feel and review ergonomics).
- Search quality improvements (token relevance + stable query wiring across UI states).
