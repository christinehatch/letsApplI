# src/discovery/store.py

from __future__ import annotations
import json

from typing import List, Tuple
from persistence.db import get_connection, transactional
from persistence.repos.jobs_repo import JobsRepo
from discovery.models import DiscoveredJob
from discovery.signals.ai_relevance import compute_ai_relevance
from datetime import datetime, timezone

class DiscoveryStore:

    def __init__(self, db_path: str):
        self.db_path = db_path

    def upsert_jobs(
        self,
        incoming: List[DiscoveredJob],
    ) -> Tuple[int, int]:
        """
        Upsert discovered jobs into SQL persistence.

        Returns:
            (new_count, updated_count)

        Deduplication is enforced by UNIQUE(provider_job_key).
        No stale marking.
        No file persistence.
        """

        new_count = 0
        updated_count = 0

        conn = get_connection(self.db_path)

        try:
            with transactional(conn):
                repo = JobsRepo(conn)

                for job in incoming:
                    provider_job_key = (
                        getattr(job, "provider_job_key", None)
                        or getattr(job, "job_uid", "")
                    )
                    before = conn.execute(
                        "SELECT id FROM jobs WHERE provider_job_key = ?",
                        (provider_job_key,),
                    ).fetchone()

                    provider = getattr(job, "provider", "")
                    external_id = getattr(job, "external_job_id", "")
                    location_raw = getattr(job, "location_raw", None)
                    if location_raw is None:
                        location_raw = getattr(job, "location", "")
                    discovered_at = getattr(job, "discovered_at", None)

                    # Deterministic timestamp (UTC ISO)
                    now_iso = datetime.now(timezone.utc).isoformat()
                    if not discovered_at:
                        discovered_at = now_iso

                    raw_meta = getattr(job, "raw_meta", None)
                    enriched_meta = dict(raw_meta) if isinstance(raw_meta, dict) else {}
                    tags = enriched_meta.get("tags")
                    description_text = getattr(job, "description_text", None)
                    description = getattr(job, "description", None) or description_text
                    ai_relevance = compute_ai_relevance(
                        title=job.title,
                        description=description,
                        metadata=enriched_meta,
                        tags=tags if isinstance(tags, list) else None,
                    )
                    enriched_meta.update(ai_relevance)
                    if isinstance(description_text, str):
                        enriched_meta["description_text"] = description_text
                    job_signals = getattr(job, "signals", None)
                    if isinstance(job_signals, list):
                        enriched_meta["signals"] = job_signals
                    else:
                        enriched_meta["signals"] = []

                    repo.upsert_discovered_job(
                        provider=provider,
                        external_id=external_id,
                        provider_job_key=provider_job_key,
                        company=job.company,
                        title=job.title,
                        location_raw=location_raw,
                        location_norm=None,
                        url=job.url,
                        posted_at=None,
                        discovered_at=discovered_at,
                        raw_provider_payload_json=json.dumps(enriched_meta) if enriched_meta else None,
                    )

                    after = conn.execute(
                        "SELECT id FROM jobs WHERE provider_job_key = ?",
                        (provider_job_key,),
                    ).fetchone()

                    if before is None:
                        new_count += 1
                    else:
                        updated_count += 1

        finally:
            conn.close()

        return new_count, updated_count
