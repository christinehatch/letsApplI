-- Track whether a posting is still on its company's board.
-- last_seen_at: the last successful board check that listed this job.
-- closed_at: set when a successful check of the same board no longer lists
--            it; cleared again if the job reappears. NULL means open.
ALTER TABLE jobs ADD COLUMN last_seen_at TEXT;
ALTER TABLE jobs ADD COLUMN closed_at TEXT;

UPDATE jobs SET last_seen_at = COALESCE(first_seen_at, discovered_at);

CREATE INDEX IF NOT EXISTS idx_jobs_closed_at ON jobs(closed_at);
