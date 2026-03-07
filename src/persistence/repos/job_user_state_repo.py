from __future__ import annotations

from typing import Optional


VALID_STATES = {
    "saved",
    "applied",
    "interview",
    "offer",
    "rejected",
    "archived",
    "ignored",  # backward compatibility
}


class JobUserStateRepo:

    def __init__(self, conn):
        self.conn = conn

    def set_state(self, job_id: str, state: str) -> None:
        normalized = state.strip().lower()
        if normalized not in VALID_STATES:
            raise ValueError(f"Invalid state: {state}")

        self.conn.execute(
            """
            INSERT INTO job_user_state (job_id, state, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(job_id)
            DO UPDATE SET
                state = excluded.state,
                updated_at = datetime('now')
            """,
            (job_id, normalized),
        )

    def get_state(self, job_id: str) -> Optional[str]:
        row = self.conn.execute(
            "SELECT state FROM job_user_state WHERE job_id = ?",
            (job_id,),
        ).fetchone()
        if not row:
            return None
        return row[0]

    def clear_state(self, job_id: str) -> None:
        self.conn.execute(
            "DELETE FROM job_user_state WHERE job_id = ?",
            (job_id,),
        )

    def list_saved_jobs(self) -> list[str]:
        rows = self.conn.execute(
            "SELECT job_id FROM job_user_state WHERE state = 'saved' ORDER BY updated_at DESC"
        ).fetchall()
        return [row[0] for row in rows]
