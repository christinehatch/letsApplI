CREATE TABLE interpretation_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    raw_llm_output TEXT,
    validation_error TEXT NOT NULL,
    timestamp TEXT NOT NULL
);

CREATE INDEX idx_interpretation_attempts_job_time
ON interpretation_attempts(job_id, timestamp DESC);
