# AGENTS.md

This file defines repository-specific guidance for AI coding agents (ChatGPT/Codex) working in `letsApplI`.

## Mission

Build and evolve a human-in-the-loop job application support tool with explicit guardrails:
- Read-only discovery/hydration of job postings.
- Deterministic interpretation and fit surfacing.
- No auto-apply, no impersonation, no hidden authority.

## Architecture Snapshot

- Python backend and orchestration in `src/`.
- FastAPI bridge server in `bridge_server.py`.
- Discovery CLI entrypoint in `main.py`.
- Phase 5 CLI entrypoint in `phase5_main.py`.
- React + Vite UI in `src/ui/app` and `src/ui/phase6`.
- SQLite persistence in `state/letsappli_v1.sqlite3` via `src/persistence/`.

## High-Value Paths

- `src/discovery/`: signal registry, polling loop, summaries.
- `src/phase5/phase5_1`: controlled job hydration.
- `src/phase5/phase5_2`: interpretation pipeline and validators.
- `src/phase5/phase5_3`: fit analysis and safety guards.
- `src/persistence/`: migrations, DB helpers, repositories.
- `tests/`: behavior and invariant coverage.
- `docs/`: phase contracts, locks, and checklists.

## Local Dev Commands

- Install Python deps: `pip install -r requirements-dev.txt`
- Install Node deps: `npm install`
- Run backend API: `python bridge_server.py`
- Run discovery CLI: `python main.py <subcommand>`
- Run phase5 CLI: `python phase5_main.py --help`
- Run UI: `npm run dev`
- Run tests: `pytest -q`

## Invariants To Preserve

- Keep human approval explicit at all decision points.
- Avoid introducing autonomous actions (especially apply/submit behavior).
- Preserve deterministic behavior where contracts require it (see Phase 5.2 docs/tests).
- Maintain read-only posture for external job sources.
- Add tests for behavior changes, especially around consent/authorization and validation guards.

### Authority and Consent Boundaries

- Hydration (Phase 5.1) must only occur with explicit user authorization.
- Interpretation (Phase 5.2) must never execute automatically after hydration.
- Interpretation must only occur when Phase 6 emits explicit consent.

No component may implicitly escalate authority across phases.

### Artifact Discipline

All analysis must operate on explicit artifacts.

Valid artifacts include:

- Hydrated job content (Phase 5.1)
- Structured interpretation output (Phase 5.2)
- Fit signals (Phase 5.3)

Agents must not introduce reasoning that bypasses these artifacts.

## Working Style Expectations

- Prefer minimal, targeted edits over broad rewrites.
- Update or add docs when changing contracts or phase behavior.
- When changing bridge endpoints, verify both backend tests and UI integration assumptions.
- Respect existing checklists and lock docs in `docs/` before widening scope.

## Done Criteria For Agent Changes

- Relevant tests pass locally (`pytest -q` at minimum).
- New behavior is covered by tests in `tests/`.
- Any contract change is reflected in docs.
- No secrets committed; use `.env` and `.env.example`.
