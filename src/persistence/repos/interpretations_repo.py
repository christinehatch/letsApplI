from dataclasses import dataclass
from persistence.errors import (
    JobNotFoundError,
    HydrationNotFoundError,
)
from sqlite3 import IntegrityError


@dataclass(frozen=True)
class InterpretationRecord:
    id: int
    job_id: int
    hydration_id: int
    interpretation_hash: str
    schema_version: str
    validator_version: str
    interpreter_version: str
    interpreter_config_hash: str
    result_json: str
    shadow_log_ref: str | None
    is_shadow: int
    created_at: str


class InterpretationsRepo:

    def __init__(self, conn):
        self.conn = conn

    def create_interpretation(
        self,
        job_id: int,
        hydration_id: int,
        interpretation_hash: str,
        schema_version: str,
        validator_version: str,
        interpreter_version: str,
        interpreter_config_hash: str,
        result_json: str,
        shadow_log_ref: str | None,
        is_shadow: int,
        created_at: str,
    ) -> InterpretationRecord:

        # ensure hydration exists
        hydration = self.conn.execute(
            "SELECT job_id FROM hydrations WHERE id = ?",
            (hydration_id,),
        ).fetchone()

        if not hydration:
            raise HydrationNotFoundError()

        if hydration["job_id"] != job_id:
            raise IntegrityError("ArtifactMismatchError")

        self.conn.execute(
            """
            INSERT INTO interpretations (
                job_id, hydration_id,
                interpretation_hash,
                schema_version, validator_version,
                interpreter_version, interpreter_config_hash,
                result_json, shadow_log_ref,
                is_shadow, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(hydration_id, interpretation_hash) DO NOTHING
            """,
            (
                job_id,
                hydration_id,
                interpretation_hash,
                schema_version,
                validator_version,
                interpreter_version,
                interpreter_config_hash,
                result_json,
                shadow_log_ref,
                is_shadow,
                created_at,
            ),
        )

        row = self.conn.execute(
            """
            SELECT * FROM interpretations
            WHERE hydration_id = ? AND interpretation_hash = ?
            """,
            (hydration_id, interpretation_hash),
        ).fetchone()

        return InterpretationRecord(**row)
