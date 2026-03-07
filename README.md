# letsA(ppl)I

*Read as “let’s apply.” AI at the edges, people at the center.*

**letsA(ppl)I** is a human-in-the-loop application support agent designed to reduce job-search friction by surfacing newly posted roles, prioritizing early opportunities, and surfacing newly posted roles, prioritizing early opportunities, and supporting application preparation — without automating submission or impersonating the user.

The system narrows the search space, prepares drafts, and highlights potential referral connections, while keeping all decisions and actions under explicit human control.

## Design Principles

- Human-in-the-loop by default  
- Explicit, inspectable rules (no hidden inference)  
- Reduce cognitive load without removing agency  
- Read-only data access  
- Small, reversible steps

## What This Version Does (v0)

This version generates a daily, prioritized job feed from a mix of demo inputs and one real, read-only job source using explicit, rule-based logic.

It:
- Groups roles by attention priority (🔥 / 🟡 / 🧊)
- Uses first-seen timestamps to identify same-day postings
- Surfaces referral signals without taking action
- Explains *why* each role appears in the feed

It does not:
- Continuously poll or automate live data collection
- Submit applications
- Make career decisions
- Act on the user’s behalf
- Track user behavior or personalize recommendations


---

## State & Memory

letsA(ppl)I maintains a small, local record of previously observed jobs to ensure that  
“first observed” timestamps remain accurate across runs.

This memory:
- Stores only `(source, source_job_id → first_seen_at)`
- Reflects when the system first saw a role, not when the employer posted it
- Is fully local, human-readable, and inspectable
- Can be reset at any time by deleting the state file

No user behavior, preferences, or actions are recorded.

## Quickstart

1. Install Python dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
2. Install UI dependencies:
   ```bash
   npm install
   ```
3. Install Playwright browser:
   ```bash
   python -m playwright install chromium
   ```
4. Run backend bridge API:
   ```bash
   python bridge_server.py
   ```
5. Run UI:
   ```bash
   npm run dev
   ```

## Developer Support Files

- `AGENTS.md`: repo-specific instructions for AI coding agents.
- `CONTRIBUTING.md`: contributor workflow and expectations.
- `docs/REPO_MAP.md`: module-level map of architecture and entrypoints.
- `.env.example`: environment variable template.
- `requirements-dev.txt`: Python development dependencies.
- `Makefile`: common setup/run/test commands.
