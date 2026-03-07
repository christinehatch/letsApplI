# Architecture

## System Pipeline

Discovery
↓
Persistence
↓
Hydration
↓
Interpretation
↓
User pipeline

## Key Modules

- `src/discovery/`
  - Job source adapters and discovery orchestration
- `src/persistence/`
  - Database access, migrations, repositories
- `src/ui/`
  - React UI and user workflow surfaces
- `bridge_server.py`
  - API bridge between frontend and backend

## Phase System

- Phase 5.1 — Hydration
- Phase 5.2 — Structured Interpretation
- Phase 6 — Exploration UI

## Interpretation Architecture

Hydrated content
↓
Phase52Interpreter (LLM)
↓
Phase52Validator
↓
job_interpretations table
↓
UI rendering

Validation must fail closed.

Do not auto-correct model output.
