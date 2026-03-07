CREATE TABLE job_user_state (
    job_id TEXT PRIMARY KEY,
    state TEXT NOT NULL CHECK (
        state IN (
            'saved',
            'applied',
            'interview',
            'offer',
            'rejected',
            'archived',
            'ignored'
        )
    ),
    updated_at TEXT NOT NULL
);
