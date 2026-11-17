-- Milestone 6.1: the user's profile (docs/PROFILE_PLAN.md §5).
-- Everything here was added by the user. Deleting a source deletes its
-- file, its text and every fact that came from it (ON DELETE CASCADE).

CREATE TABLE profile_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL CHECK (kind IN ('resume', 'linkedin', 'website', 'transcript')),
    label TEXT NOT NULL,
    file_path TEXT,            -- stored copy under state/profile/, for uploads
    url TEXT,                  -- for websites
    extracted_text TEXT,       -- plain text read locally (no AI)
    added_at TEXT NOT NULL,
    read_at TEXT,              -- set in 6.2 when the user presses "Read it"
    CHECK ((file_path IS NOT NULL) OR (url IS NOT NULL))
);

CREATE TABLE profile_facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER REFERENCES profile_sources(id) ON DELETE CASCADE,  -- NULL = typed by the user
    kind TEXT NOT NULL CHECK (kind IN ('title', 'skill', 'domain', 'education', 'location', 'achievement')),
    text TEXT NOT NULL,
    quote TEXT,                -- exact span from the source (6.2)
    status TEXT NOT NULL CHECK (status IN ('proposed', 'confirmed', 'rejected')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX idx_profile_facts_source ON profile_facts(source_id);

CREATE TABLE profile_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL CHECK (kind IN (
        'location', 'work_mode', 'level', 'company_size', 'industry_in', 'industry_out'
    )),
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (kind, value)
);
