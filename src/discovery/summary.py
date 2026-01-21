# src/discovery/summary.py
from __future__ import annotations

import time
from typing import List, Dict
from discovery.store import load_jobs


def summarize_since(since_ts: float) -> str:
    jobs = load_jobs()
    new_jobs = [j for j in jobs if j.first_seen_at > since_ts and j.status == "active"]

    by_company: Dict[str, List] = {}
    for j in new_jobs:
        by_company.setdefault(j.company, []).append(j)

    lines = []
    total = len(new_jobs)
    lines.append(f"{total} new roles appeared since last check.")
    lines.append("I have not read them. Click one if you want to hydrate.")
    lines.append("")

    for company in sorted(by_company.keys()):
        lines.append(f"{company}:")
        for j in sorted(by_company[company], key=lambda x: x.first_seen_at, reverse=True):
            loc = f" — {j.location}" if j.location else ""
            lines.append(f"- {j.title}{loc}")
            lines.append(f"  {j.url}")
        lines.append("")

    return "\n".join(lines).strip()

