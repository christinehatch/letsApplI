# src/persistence/repos/jobs_repo.py

from sqlite3 import IntegrityError
from typing import Optional
from persistence.models import JobRecord
from persistence.errors import JobNotFoundError


class JobsRepo:

    def __init__(self, conn):
        self.conn = conn

    def list_new_jobs_since(self, since_iso: str) -> list[JobRecord]:
        rows = self.conn.execute(
            """
            SELECT *
            FROM jobs
            WHERE first_seen_at IS NOT NULL
              AND first_seen_at > ?
              AND is_archived = 0
            ORDER BY first_seen_at DESC
            """,
            (since_iso,),
        ).fetchall()

        return [JobRecord(**row) for row in rows]

    def upsert_discovered_job(
        self,
        provider: str,
        external_id: str,
        provider_job_key: str,
        company: str,
        title: str,
        location_raw: Optional[str],
        location_norm: Optional[str],
        url: str,
        posted_at: Optional[str],
        discovered_at: str,
        raw_provider_payload_json: Optional[str],
    ) -> JobRecord:

        try:
            self.conn.execute(
                """
                INSERT INTO jobs (
                    provider, external_id, provider_job_key,
                    company, title, location_raw, location_norm,
                    url, posted_at, discovered_at,
                    raw_provider_payload_json,
                    first_seen_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    provider,
                    external_id,
                    provider_job_key,
                    company,
                    title,
                    location_raw,
                    location_norm,
                    url,
                    posted_at,
                    discovered_at,
                    raw_provider_payload_json,
                    discovered_at,  # first_seen_at set only on insert
                ),
            )
        except IntegrityError:
            # update metadata only
            self.conn.execute(
                """
                UPDATE jobs
                SET company = ?,
                    title = ?,
                    location_raw = ?,
                    location_norm = ?,
                    url = ?,
                    posted_at = ?,
                    raw_provider_payload_json = ?
                WHERE provider_job_key = ?
                """,
                (
                    company,
                    title,
                    location_raw,
                    location_norm,
                    url,
                    posted_at,
                    raw_provider_payload_json,
                    provider_job_key,
                ),
            )

        row = self.conn.execute(
            "SELECT * FROM jobs WHERE provider_job_key = ?",
            (provider_job_key,),
        ).fetchone()

        return JobRecord(**row)
