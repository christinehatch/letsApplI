import json


class JobInterpretationRepo:

    def __init__(self, conn):
        self.conn = conn

    def save_interpretation(
        self,
        job_id: str,
        interpretation: dict,
        model_version: str,
        span_map: dict | None = None,
    ):

        self.conn.execute(
            """
            INSERT OR REPLACE INTO job_interpretations
            (job_id, interpretation_json, model_version, span_map_json)
            VALUES (?, ?, ?, ?)
            """,
            (
                job_id,
                json.dumps(interpretation),
                model_version,
                json.dumps(span_map or {}),
            )
        )

        self.conn.commit()

    def get_interpretation(self, job_id: str):

        row = self.conn.execute(
            """
            SELECT interpretation_json
            FROM job_interpretations
            WHERE job_id = ?
            """,
            (job_id,)
        ).fetchone()

        if not row:
            return None

        return json.loads(row[0])

    def get_interpretation_record(self, job_id: str):
        row = self.conn.execute(
            """
            SELECT interpretation_json, span_map_json
            FROM job_interpretations
            WHERE job_id = ?
            """,
            (job_id,),
        ).fetchone()

        if not row:
            return None

        interpretation = json.loads(row[0]) if row[0] else None
        span_map = json.loads(row[1]) if row[1] else {}
        return {
            "interpretation": interpretation,
            "span_map": span_map,
        }

    def delete_interpretation(self, job_id: str) -> None:
        self.conn.execute(
            """
            DELETE FROM job_interpretations
            WHERE job_id = ?
            """,
            (job_id,),
        )
        self.conn.commit()
