# letsA(ppl)I

*Read as “let’s apply.” AI at the edges, people at the center.*

**letsA(ppl)I** is a human-in-the-loop application support agent designed to reduce job-search friction by surfacing newly posted roles, prioritizing early opportunities, and assisting with application preparation — without automating submission or impersonating the user.

The system narrows the search space, prepares drafts, and highlights potential referral connections, while keeping all decisions and actions under explicit human control.

## Design Principles

- Human-in-the-loop by default  
- Explicit, inspectable rules (no hidden inference)  
- Reduce cognitive load without removing agency  
- Read-only data access  
- Small, reversible steps

## What This Version Does (v0)

This version generates a daily, prioritized job feed from predefined inputs using explicit, rule-based logic.

It:
- Groups roles by attention priority (🔥 / 🟡 / 🧊)
- Uses first-seen timestamps to identify same-day postings
- Surfaces referral signals without taking action
- Explains *why* each role appears in the feed

It does not:
- Fetch live data
- Submit applications
- Make career decisions
- Act on the user’s behalf
