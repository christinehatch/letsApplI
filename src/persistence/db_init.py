from __future__ import annotations


def initialize_database(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS job_user_state (
            job_id TEXT PRIMARY KEY,
            state TEXT NOT NULL CHECK(
                state IN (
                    'discovered',
                    'saved',
                    'applied',
                    'interview',
                    'offer',
                    'rejected',
                    'archived',
                    'ignored'
                )
            ),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    conn.commit()
