# src/discovery/summary.py
from __future__ import annotations

from typing import List, Dict
from persistence.db import get_connection
from persistence.repos.jobs_repo import JobsRepo
from state import DB_PATH
from discovery.location_filters import is_sf_bay_area


def summarize_since(
    since_iso: str,
    location_mode: str = "bay_area",
) -> str:
    conn = get_connection(DB_PATH)

    try:
        repo = JobsRepo(conn)
        jobs = repo.list_new_jobs_since(since_iso)
    finally:
        conn.close()

    if location_mode == "bay_area":
        jobs = [
            j for j in jobs
            if j.location_raw and is_sf_bay_area(j.location_raw)
        ]
    elif location_mode == "all":
        pass
    elif location_mode.startswith("contains:"):
        needle = location_mode.split(":", 1)[1].lower()
        jobs = [
            j for j in jobs
            if j.location_raw and needle in j.location_raw.lower()
        ]

    by_company: Dict[str, List] = {}
    for j in jobs:
        by_company.setdefault(j.company, []).append(j)

    lines = []
    total = len(jobs)

    lines.append(f"{total} new roles appeared since last check.")
    lines.append("I have not read them. Click one if you want to hydrate.")
    lines.append("")

    for company in sorted(by_company.keys()):
        lines.append(f"{company}:")

        for j in by_company[company]:
            loc = f" — {j.location_raw}" if j.location_raw else ""
            lines.append(f"- {j.title}{loc}")
            lines.append(f"  {j.url}")

        lines.append("")

    return "\n".join(lines).strip()