CREATE TABLE job_interpretations (
    job_id TEXT PRIMARY KEY,
    interpretation_json TEXT NOT NULL,
    model_version TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_job_interpretations_job_id
ON job_interpretations(job_id);
