# letsA(ppl)I — Phase 2.0 Checklist
Goal: Deterministic, explainable “same-day” detection.

- [x] Update source adapters to return `first_seen_at` (datetime)
- [x] Remove `first_seen_hours_ago` from adapter contracts
- [x] Add a single helper to compute hours-since
- [x] Update prioritization rules to use derived hours
- [x] Define “new today” as a date equality check
- [x] Update output language to “First seen today at X”
- [x] Verify output format remains unchanged
- [x] Stop when recency is explainable, not perfect

