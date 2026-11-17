# src/discovery/signals/ashby.py
from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict, List

from discovery.models import Signal, DiscoveredJob, assert_metadata_only, to_utc_iso
from discovery.signals.base import SignalAdapter


def _locations(job: Dict[str, Any]) -> str:
    """Primary + secondary locations, plus 'Remote' when the role allows it."""
    names: List[str] = []
    primary = str(job.get("location") or "").strip()
    if primary:
        names.append(primary)
    for extra in job.get("secondaryLocations") or []:
        name = str((extra or {}).get("location") or "").strip()
        if name and name not in names:
            names.append(name)
    if job.get("isRemote") and not any("remote" in n.lower() for n in names):
        names.append("Remote")
    return "; ".join(names)


class AshbyAdapter(SignalAdapter):
    """
    Ashby public job board API. Metadata only: the API also returns full
    description text, which discovery deliberately drops (hydration reads
    postings later, with consent).
    """

    def fetch(self, board_name: str) -> Dict[str, Any]:
        url = f"https://api.ashbyhq.com/posting-api/job-board/{board_name}"
        req = urllib.request.Request(url, headers={"User-Agent": "letsApplI/phase4.5 (metadata-only)"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def poll(self, signal: Signal) -> List[DiscoveredJob]:
        board_name = signal.config.get("board_name")
        if not board_name:
            raise ValueError("Ashby signal missing config.board_name")
        return self.parse(signal, board_name, self.fetch(board_name))

    def parse(self, signal: Signal, board_name: str, data: Dict[str, Any]) -> List[DiscoveredJob]:
        out: List[DiscoveredJob] = []
        for j in data.get("jobs") or []:
            if j.get("isListed") is False:
                continue

            job_id = str(j.get("id", "")).strip()
            title = str(j.get("title", "")).strip()
            if not job_id or not title:
                continue

            raw_meta: Dict[str, Any] = {
                "department": j.get("department"),
                "team": j.get("team"),
                "workplace_type": j.get("workplaceType"),
                "employment_type": j.get("employmentType"),
                "published_at": j.get("publishedAt"),
            }
            for k in list(raw_meta.keys()):
                if raw_meta[k] in (None, ""):
                    raw_meta.pop(k, None)

            assert_metadata_only(raw_meta)

            out.append(
                DiscoveredJob(
                    job_uid=f"ashby:{board_name}:{job_id}",
                    company=signal.company,
                    source_signal_id=signal.signal_id,
                    external_job_id=job_id,
                    title=title,
                    location=_locations(j),
                    url=str(j.get("jobUrl") or j.get("applyUrl") or "").strip(),
                    first_seen_at=0.0,  # set in store
                    last_seen_at=0.0,   # set in store
                    status="active",
                    raw_meta=raw_meta,
                    posted_at=to_utc_iso(j.get("publishedAt")),
                )
            )
        return out
