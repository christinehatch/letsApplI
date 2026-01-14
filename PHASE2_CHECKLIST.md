# letsA(ppl)I — Phase 2.0 Checklist
Goal: Deterministic, explainable “same-day” detection.

- [ ] Update source adapters to return `first_seen_at` (datetime)
- [ ] Remove `first_seen_hours_ago` from adapter contracts
- [ ] Add a single helper to compute hours-since
- [ ] Update prioritization rules to use derived hours
- [ ] Define “new today” as a date equality check
- [ ] Update output language to “First seen today at X”
- [ ] Verify output format remains unchanged
- [ ] Stop when recency is explainable, not perfect

