# src/discovery/signals/lever.py
from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict, List

from discovery.models import Signal, DiscoveredJob, assert_metadata_only
from discovery.signals.base import SignalAdapter


class LeverAdapter(SignalAdapter):
    def poll(self, signal: Signal) -> List[DiscoveredJob]:
        company_slug = signal.config.get("company_slug")
        if not company_slug:
            raise ValueError("Lever signal missing config.company_slug")

        url = f"https://api.lever.co/v0/postings/{company_slug}?mode=json"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "letsApplI/phase4.5 (metadata-only)"},
        )

        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")

        data = json.loads(raw)
        jobs = data if isinstance(data, list) else []

        out: List[DiscoveredJob] = []

        for j in jobs:
            job_id = str(j.get("id", "")).strip()
            title = str(j.get("text", "")).strip()
            location = str(
                ((j.get("categories") or {}).get("location", "")) or ""
            ).strip()
            job_url = str(j.get("hostedUrl", "")).strip()

            raw_meta: Dict[str, Any] = {
                "created_at": j.get("createdAt"),
                "updated_at": j.get("updatedAt"),
            }

            # Remove None values (mirror Greenhouse pattern)
            for k in list(raw_meta.keys()):
                if raw_meta[k] is None:
                    raw_meta.pop(k, None)

            assert_metadata_only(raw_meta)

            job_uid = f"lever:{company_slug}:{job_id}"

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
