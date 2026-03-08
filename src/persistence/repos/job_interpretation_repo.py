import json


class JobInterpretationRepo:

    def __init__(self, conn):
        self.conn = conn

    def save_interpretation(self, job_id: str, interpretation: dict, model_version: str):

        self.conn.execute(
            """
            INSERT OR REPLACE INTO job_interpretations
            (job_id, interpretation_json, model_version)
            VALUES (?, ?, ?)
            """,
            (job_id, json.dumps(interpretation), model_version)
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
