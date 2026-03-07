# Contributing

## Development Workflow

### Development stack

Backend:

- FastAPI
- SQLite persistence
- Repository pattern

Frontend:

- React + Vite
- Three-pane layout
- `FeedSidebar`
- Job detail panel
- `Phase6SidePanel`

### Key conventions

- Repositories are deterministic artifact stores.
- Repositories never interpret job content.
- LLM outputs must pass validator checks.
- New migrations go in `migrations/`.

### Testing

Run before committing:

```bash
pytest -q
```

All tests must pass before committing.

### Commit structure

Prefer milestone-scoped commits, for example:

- `Milestone 4 — Pipeline UI`
- `Milestone 5 — Interpretation Engine`
