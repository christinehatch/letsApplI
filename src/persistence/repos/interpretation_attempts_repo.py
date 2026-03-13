from dataclasses import dataclass


@dataclass(frozen=True)
class InterpretationAttemptRecord:
    id: int
    job_id: str
    raw_llm_output: str | None
    validation_error: str
    timestamp: str


class InterpretationAttemptsRepo:

    def __init__(self, conn):
        self.conn = conn

    def create_attempt(
        self,
        *,
        job_id: str,
        raw_llm_output: str | None,
        validation_error: str,
        timestamp: str,
    ) -> InterpretationAttemptRecord:
        self.conn.execute(
            """
            INSERT INTO interpretation_attempts (
                job_id,
                raw_llm_output,
                validation_error,
                timestamp
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                job_id,
                raw_llm_output,
                validation_error,
                timestamp,
            ),
        )

        row = self.conn.execute(
            """
            SELECT * FROM interpretation_attempts
            WHERE id = last_insert_rowid()
            """
        ).fetchone()

        return InterpretationAttemptRecord(**row)
