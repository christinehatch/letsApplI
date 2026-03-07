# Repository Map

## Entry Points

- `main.py`: Discovery CLI bootstrap.
- `phase5_main.py`: Phase 5 CLI bootstrap.
- `bridge_server.py`: FastAPI bridge for UI/API workflows.

## Core Modules

- `src/discovery/`
  - Signal registration, polling, and summary generation.
  - Adapters for Greenhouse/Lever discovery.
- `src/phase5/`
  - Requirement extraction, evidence matching, proposal shaping.
  - `phase5_1`: hydrate job posting content under explicit user consent.
  - `phase5_2`: structured role interpretation pipeline with strict validation.
  - `phase5_3`: fit analysis guards.
- `src/persistence/`
  - SQLite DB connection, migrations, repositories, and model records.
- `src/ui/`
  - `app/`: Vite/React shell.
  - `phase6/`: stateful side panel and consent flow.

## State and Data

- `state/`: runtime artifacts (SQLite DB + JSON state files).
- `migrations/`: SQL schema migrations.
- `tests/fixtures/`: fixture payloads for deterministic tests.

## Documentation Anchors

- `README.md`: project overview and design principles.
- `PHASES.md`: phase roadmap.
- `docs/ARCHITECTURE_LOCK.md`: architecture constraints.
- `docs/PHASE*_*.md`: phase-specific contracts/checklists.

## Recommended Change Workflow

1. Identify contract/phase boundaries impacted by your change.
2. Implement minimal edits in the relevant module.
3. Add or update tests nearest the changed behavior.
4. Update docs/checklists when behavior or contracts shift.
