# Contributing

## Scope

This repository prioritizes human-in-the-loop workflows for job discovery and application support. Contributions must preserve explicit user control and safety constraints.

## Setup

1. Create and activate a Python virtual environment.
2. Install Python dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
3. Install UI dependencies:
   ```bash
   npm install
   ```
4. Install Playwright browser binaries (required for hydration/preview paths):
   ```bash
   playwright install chromium
   ```

## Run Locally

1. Backend API:
   ```bash
   python bridge_server.py
   ```
2. Frontend UI:
   ```bash
   npm run dev
   ```
3. Discovery CLI examples:
   ```bash
   python main.py init
   python main.py list
   python main.py poll
   python main.py summary
   ```

## Testing

- Run all tests:
  ```bash
  pytest -q
  ```
- Prefer adding tests in the same domain folder as the changed module:
  - `tests/phase5_1`
  - `tests/phase5_2`
  - `tests/phase5_3`
  - `tests/ui`

## Pull Request Expectations

- Keep changes scoped and intentional.
- Preserve safety and consent gates.
- Include tests for behavior changes.
- Update docs when contracts or phase boundaries change.
- Avoid adding hidden inference or authority in model-facing logic.

## Coding Notes

- Python import paths are expected to work from repo root (`main.py`/`phase5_main.py` add `src` to `sys.path`).
- Use existing repository abstractions in `src/persistence/repos/` rather than direct SQL spread across modules.
- Keep source integrations read-only.
