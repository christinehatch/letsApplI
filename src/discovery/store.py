# src/discovery/store.py
from __future__ import annotations

import json
import os
from typing import Dict, Any, List, Tuple
from discovery.models import DiscoveredJob


DEFAULT_JOBS_PATH = os.path.join("state", "discovered_jobs.json")


def _load_raw(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {"jobs": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_jobs(path: str = DEFAULT_JOBS_PATH) -> List[DiscoveredJob]:
    data = _load_raw(path)
    return [DiscoveredJob(**j) for j in data.get("jobs", [])]


def save_jobs(jobs: List[DiscoveredJob], path: str = DEFAULT_JOBS_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {"jobs": [j.to_dict() for j in jobs]}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)


def upsert_jobs(
    incoming: List[DiscoveredJob],
    now: float,
    path: str = DEFAULT_JOBS_PATH,
    mark_stale_for_signal_id: str | None = None,
) -> Tuple[int, int, int]:
    """
    Upsert rules:
    - new job: first_seen_at=now, last_seen_at=now
    - existing: preserve first_seen_at, update last_seen_at=now
    Optionally mark stale for a signal if jobs disappear.
    Returns: (new_count, updated_count, stale_count)
    """
    existing = load_jobs(path)
    by_uid = {j.job_uid: j for j in existing}

    seen_uids = set()
    new_count = 0
    updated_count = 0

    for j in incoming:
        seen_uids.add(j.job_uid)
        if j.job_uid not in by_uid:
            j.first_seen_at = now
            j.last_seen_at = now
            by_uid[j.job_uid] = j
            new_count += 1
        else:
            old = by_uid[j.job_uid]
            old.last_seen_at = now
            # safe metadata refresh (still metadata-only)
            old.title = j.title
            old.location = j.location
            old.url = j.url
            old.raw_meta = j.raw_meta
            old.status = "active"
            updated_count += 1

    stale_count = 0
    if mark_stale_for_signal_id:
        for job in by_uid.values():
            if job.source_signal_id == mark_stale_for_signal_id and job.job_uid not in seen_uids:
                if job.status != "stale":
                    job.status = "stale"
                    stale_count += 1

    save_jobs(list(by_uid.values()), path)
    return new_count, updated_count, stale_count

