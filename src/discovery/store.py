# src/discovery/store.py

from __future__ import annotations
import json

from typing import List, Tuple
from persistence.db import get_connection, transactional
from persistence.repos.jobs_repo import JobsRepo
from discovery.models import DiscoveredJob
import time
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
                    before = conn.execute(
                        "SELECT id FROM jobs WHERE provider_job_key = ?",
                        (job.job_uid,),
                    ).fetchone()
                    # Derive provider from job_uid (format: greenhouse:<board_token>:<id>)
                    provider = job.job_uid.split(":")[0]

                    # Deterministic timestamp (UTC ISO)
                    now_iso = datetime.now(timezone.utc).isoformat()

                    repo.upsert_discovered_job(
                        provider=provider,
                        external_id=job.external_job_id,
                        provider_job_key=job.job_uid,
                        company=job.company,
                        title=job.title,
                        location_raw=job.location,
                        location_norm=None,
                        url=job.url,
                        posted_at=None,
                        discovered_at=now_iso,
                        raw_provider_payload_json=json.dumps(job.raw_meta) if job.raw_meta else None,
                    )

                    after = conn.execute(
                        "SELECT id FROM jobs WHERE provider_job_key = ?",
                        (job.job_uid,),
                    ).fetchone()

                    if before is None:
                        new_count += 1
                    else:
                        updated_count += 1

        finally:
            conn.close()

        return new_count, updated_count