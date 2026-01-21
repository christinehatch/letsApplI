# src/discovery/summary.py
from __future__ import annotations

from typing import List, Dict
from discovery.store import load_jobs
from discovery.archetypes import match_archetype



def summarize_since(since_ts: float, *, explain_roles: bool = False) -> str:
    jobs = load_jobs()
    from discovery.location_filters import is_sf_bay_area

    new_jobs = [
        j
        for j in jobs
        if j.first_seen_at > since_ts
           and j.status == "active"
           and is_sf_bay_area(j.location)
    ]

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

            # Optional archetype orientation (title-only, pre-hydration safe)
            if explain_roles:
                match = match_archetype(j.title)

                if match.archetype != "UNKNOWN":
                    lines.append("  ")
                    lines.append("  What is this role generally?")
                    lines.append("  I have not read this job.")
                    lines.append(f"  {match.label} roles are generally associated with:")

                    for line in match.orientation_lines:
                        lines.append(f"   - {line}")

        lines.append("")

    return "\n".join(lines).strip()
