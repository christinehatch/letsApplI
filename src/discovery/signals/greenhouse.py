# src/discovery/signals/greenhouse.py
from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict, List

from discovery.models import Signal, DiscoveredJob, assert_metadata_only
from discovery.signals.base import SignalAdapter


class GreenhouseAdapter(SignalAdapter):
    def poll(self, signal: Signal) -> List[DiscoveredJob]:
        board_token = signal.config.get("board_token")
        if not board_token:
            raise ValueError("Greenhouse signal missing config.board_token")

        url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
        req = urllib.request.Request(url, headers={"User-Agent": "letsApplI/phase4.5 (metadata-only)"})

        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")

        data = json.loads(raw)
        jobs = data.get("jobs", [])

        out: List[DiscoveredJob] = []
        for j in jobs:
            job_id = str(j.get("id", ""))
            title = str(j.get("title", "")).strip()
            location = str((j.get("location") or {}).get("name", "")).strip()
            job_url = str(j.get("absolute_url", "")).strip()

            raw_meta: Dict[str, Any] = {
                "departments": [d.get("name") for d in (j.get("departments") or []) if d.get("name")],
                "updated_at": j.get("updated_at"),
                "created_at": j.get("created_at"),
            }
            # Defensive strip if API ever includes content-ish keys
            for k in list(raw_meta.keys()):
                if raw_meta[k] is None:
                    raw_meta.pop(k, None)

            assert_metadata_only(raw_meta)

            job_uid = f"greenhouse:{board_token}:{job_id}"

            out.append(
                DiscoveredJob(
                    job_uid=job_uid,
                    company=signal.company,
                    source_signal_id=signal.signal_id,
                    external_job_id=job_id,
                    title=title,
                    location=location,
                    url=job_url,
                    first_seen_at=0.0,  # set in store
                    last_seen_at=0.0,   # set in store
                    status="active",
                    raw_meta=raw_meta,
                )
            )

        return out

