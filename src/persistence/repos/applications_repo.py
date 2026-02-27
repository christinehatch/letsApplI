from dataclasses import dataclass
from persistence.errors import JobNotFoundError


@dataclass(frozen=True)
class ApplicationRecord:
    id: int
    job_id: int
    status: str
    status_updated_at: str
    notes: str | None
    last_touched_at: str


class ApplicationsRepo:

    def __init__(self, conn):
        self.conn = conn

    def set_status(
        self,
        job_id: int,
        new_status: str,
        timestamp: str,
        notes: str | None = None,
    ) -> ApplicationRecord:

        job = self.conn.execute(
            "SELECT id FROM jobs WHERE id = ?",
            (job_id,),
        ).fetchone()

        if not job:
            raise JobNotFoundError()

        existing = self.conn.execute(
            "SELECT * FROM applications WHERE job_id = ?",
            (job_id,),
        ).fetchone()

        if not existing:
            self.conn.execute(
                """
                INSERT INTO applications (
                    job_id, status,
                    status_updated_at,
                    notes, last_touched_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    new_status,
                    timestamp,
                    notes,
                    timestamp,
                ),
            )
        else:
            self.conn.execute(
                """
                UPDATE applications
                SET status = ?,
                    status_updated_at = ?,
                    notes = ?,
                    last_touched_at = ?
                WHERE job_id = ?
                """,
                (
                    new_status,
                    timestamp,
                    notes,
                    timestamp,
                    job_id,
                ),
            )

        row = self.conn.execute(
            "SELECT * FROM applications WHERE job_id = ?",
            (job_id,),
        ).fetchone()

        return ApplicationRecord(**row)
