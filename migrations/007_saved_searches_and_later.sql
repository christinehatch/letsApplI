-- Saved searches drive the Today view: each one shows roles discovered after
-- its baseline that the user hasn't decided on yet.
CREATE TABLE saved_searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT '',
    location TEXT NOT NULL DEFAULT '',
    company TEXT NOT NULL DEFAULT '',
    -- Roles discovered after this ISO-8601 timestamp count as new.
    -- '' means every role open when the search was saved counts as new.
    new_since TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Add 'later' (and the existing 'discovered') to job_user_state.
-- SQLite can't alter a CHECK constraint, so the table is rebuilt.
CREATE TABLE job_user_state_new (
    job_id TEXT PRIMARY KEY,
    state TEXT NOT NULL CHECK (
        state IN (
            'discovered',
            'saved',
            'later',
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

INSERT INTO job_user_state_new (job_id, state, updated_at)
SELECT job_id, state, updated_at FROM job_user_state;

DROP TABLE job_user_state;

ALTER TABLE job_user_state_new RENAME TO job_user_state;
