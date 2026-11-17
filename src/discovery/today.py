"""
The Today view: a short, finite set of roles to decide on.

* A role is **new** for a saved search when it was discovered after the
  search's `new_since` and the user hasn't decided on it yet (no state, or
  'discovered').
* Save, Skip ('ignored'), and Later ('later') are the only decisions. Later
  roles come back at the end of the next Today, until decided.
* Postings with the same company and title (one per city) are one item, and a
  decision applies to all of them.
* Searches take turns so one busy search can't fill the whole day.

Deterministic: no ranking by fit, no LLM, no background work.
"""

from __future__ import annotations

import json
from collections import Counter, OrderedDict
from typing import Iterable, Optional

from persistence.repos.jobs_repo import JobsRepo

UNDECIDED = "(job_user_state.state IS NULL OR job_user_state.state = 'discovered')"
DEFAULT_LIMIT = 15


def _group_key(company: str, title: str) -> tuple[str, str]:
    return (" ".join((company or "").lower().split()), " ".join((title or "").lower().split()))


def _signals(repo: JobsRepo, raw_payload: Optional[str], title: str) -> list[str]:
    try:
        return repo._extract_persisted_signals(raw_provider_payload_json=raw_payload, title=title)
    except Exception:
        return []


def _matching_rows(repo: JobsRepo, search: dict, *, only_new: bool) -> list:
    where, params = repo._build_discovery_where_and_params(
        location=search.get("location") or None,
        role=search.get("role") or None,
        experience=None,
        company=search.get("company") or None,
        ai_filter=None,
        signal=None,
        signals=None,
    )
    where = [f"jobs.{w}" if w in ("is_archived = 0", "closed_at IS NULL") else w for w in where]
    where.append(UNDECIDED)
    if only_new:
        where.append("jobs.discovered_at > ?")
        params = [*params, search.get("new_since") or ""]

    return repo.conn.execute(
        f"""
        SELECT jobs.provider_job_key, jobs.company, jobs.title, jobs.location_raw,
               jobs.url, jobs.discovered_at, jobs.raw_provider_payload_json
        FROM jobs
        LEFT JOIN job_user_state ON jobs.provider_job_key = job_user_state.job_id
        WHERE {' AND '.join(where)}
        ORDER BY jobs.discovered_at DESC, jobs.provider_job_key
        """,
        tuple(params),
    ).fetchall()


def _group(repo: JobsRepo, rows: Iterable, source: dict) -> "OrderedDict[tuple, dict]":
    groups: "OrderedDict[tuple, dict]" = OrderedDict()
    for r in rows:
        key = _group_key(r[1], r[2])
        item = groups.get(key)
        if item is None:
            item = groups[key] = {
                "job_id": r[0],
                "job_ids": [],
                "company": r[1],
                "title": r[2],
                "locations": [],
                "url": r[4],
                "first_seen_at": r[5],
                "signals": _signals(repo, r[6], r[2]),
                "source": source,
            }
        item["job_ids"].append(r[0])
        if r[3] and r[3] not in item["locations"]:
            item["locations"].append(r[3])
        if r[5] and (not item["first_seen_at"] or r[5] < item["first_seen_at"]):
            item["first_seen_at"] = r[5]
    return groups


def summarize_search(repo: JobsRepo, search: dict) -> dict:
    open_groups = _group(repo, _matching_rows(repo, search, only_new=False), {})
    new_groups = _group(repo, _matching_rows(repo, search, only_new=True), {})
    companies = Counter(g["company"] for g in open_groups.values())
    return {
        **{k: search[k] for k in ("id", "name", "role", "location", "company", "created_at")},
        "open_count": len(open_groups),
        "new_count": len(new_groups),
        "top_companies": [c for c, _ in companies.most_common(3)],
        "company_count": len(companies),
    }


def build_today(repo: JobsRepo, searches: list[dict], *, limit: int = DEFAULT_LIMIT) -> dict:
    per_search: list[list[dict]] = []
    for s in searches:
        source = {"type": "search", "search_id": s["id"], "name": s["name"]}
        per_search.append(list(_group(repo, _matching_rows(repo, s, only_new=True), source).values()))

    total_new_keys = {(_group_key(i["company"], i["title"])) for items in per_search for i in items}

    # Take turns across searches; skip items another search already queued.
    queue: list[dict] = []
    seen: set = set()
    cursors = [0] * len(per_search)
    while len(queue) < limit and any(c < len(items) for c, items in zip(cursors, per_search)):
        for idx, items in enumerate(per_search):
            while cursors[idx] < len(items):
                item = items[cursors[idx]]
                cursors[idx] += 1
                key = _group_key(item["company"], item["title"])
                if key in seen:
                    continue
                seen.add(key)
                queue.append(item)
                break
            if len(queue) >= limit:
                break

    # Roles the user set aside last time come back at the end.
    later_rows = repo.conn.execute(
        """
        SELECT jobs.provider_job_key, jobs.company, jobs.title, jobs.location_raw,
               jobs.url, jobs.discovered_at, jobs.raw_provider_payload_json
        FROM jobs
        JOIN job_user_state ON jobs.provider_job_key = job_user_state.job_id
        WHERE jobs.is_archived = 0 AND jobs.closed_at IS NULL AND job_user_state.state = 'later'
        ORDER BY job_user_state.updated_at
        """
    ).fetchall()
    later_items = [
        i for k, i in _group(repo, later_rows, {"type": "later", "name": "Set aside last time"}).items()
        if k not in seen
    ]

    return {
        "items": queue + later_items,
        "new_total": len(total_new_keys),
        "new_shown": len(queue),
        "later_count": len(later_items),
        "limit": limit,
    }
