# src/persistence/repos/hydrations_repo.py

from persistence.models import JobRecord
from persistence.errors import JobNotFoundError
from dataclasses import dataclass


@dataclass(frozen=True)
class HydrationRecord:
    id: int
    job_id: int
    hydration_hash: str
    raw_content: str
    content_type: str
    hydrator_version: str
    hydrator_config_hash: str
    created_at: str


class HydrationsRepo:

    def __init__(self, conn):
        self.conn = conn

    def create_hydration(
        self,
        job_id: int,
        hydration_hash: str,
        raw_content: str,
        content_type: str,
        hydrator_version: str,
        hydrator_config_hash: str,
        created_at: str,
    ) -> HydrationRecord:

        row = self.conn.execute(
            "SELECT id FROM jobs WHERE id = ?",
            (job_id,),
        ).fetchone()

        if not row:
            raise JobNotFoundError()

        self.conn.execute(
            """
            INSERT INTO hydrations (
                job_id, hydration_hash, raw_content, content_type,
                hydrator_version, hydrator_config_hash, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_id, hydration_hash) DO NOTHING
            """,
            (
                job_id,
                hydration_hash,
                raw_content,
                content_type,
                hydrator_version,
                hydrator_config_hash,
                created_at,
            ),
        )

        row = self.conn.execute(
            """
            SELECT * FROM hydrations
            WHERE job_id = ? AND hydration_hash = ?
            """,
            (job_id, hydration_hash),
        ).fetchone()

        return HydrationRecord(**row)
