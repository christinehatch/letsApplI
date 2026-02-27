class EventsRepo:

    def __init__(self, conn):
        self.conn = conn

    def append_event(
        self,
        job_id: int | None,
        event_type: str,
        payload_json: str | None,
        created_at: str,
    ) -> None:

        self.conn.execute(
            """
            INSERT INTO events (
                job_id, event_type,
                payload_json, created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                job_id,
                event_type,
                payload_json,
                created_at,
            ),
        )
