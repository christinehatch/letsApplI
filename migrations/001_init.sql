PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;

-- ============================================
-- JOBS
-- ============================================

CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    provider TEXT NOT NULL,
    external_id TEXT NOT NULL,
    provider_job_key TEXT NOT NULL UNIQUE,

    company TEXT NOT NULL,
    title TEXT NOT NULL,
    location_raw TEXT,
    location_norm TEXT,
    url TEXT NOT NULL,

    posted_at TEXT,
    discovered_at TEXT NOT NULL,

    raw_provider_payload_json TEXT,

    is_archived INTEGER NOT NULL DEFAULT 0 CHECK (is_archived IN (0,1))
);

-- Prevent unarchive (soft delete only)
CREATE TRIGGER prevent_unarchive
BEFORE UPDATE OF is_archived ON jobs
FOR EACH ROW
WHEN OLD.is_archived = 1 AND NEW.is_archived = 0
BEGIN
    SELECT RAISE(ABORT, 'SoftDeleteViolationError: Cannot unarchive job');
END;


-- ============================================
-- HYDRATIONS (IMMUTABLE)
-- ============================================

CREATE TABLE hydrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    job_id INTEGER NOT NULL,
    hydration_hash TEXT NOT NULL,
    raw_content TEXT NOT NULL,
    content_type TEXT NOT NULL,

    hydrator_version TEXT NOT NULL,
    hydrator_config_hash TEXT NOT NULL,

    created_at TEXT NOT NULL,

    FOREIGN KEY (job_id)
        REFERENCES jobs(id)
        ON DELETE RESTRICT,

    UNIQUE (job_id, hydration_hash),

    CHECK (length(hydration_hash) = 64),
    CHECK (length(hydrator_config_hash) = 64)
);

CREATE TRIGGER prevent_hydration_update
BEFORE UPDATE ON hydrations
BEGIN
    SELECT RAISE(ABORT, 'ImmutableArtifactError: Hydrations are immutable');
END;

CREATE TRIGGER prevent_hydration_delete
BEFORE DELETE ON hydrations
BEGIN
    SELECT RAISE(ABORT, 'ImmutableArtifactError: Cannot delete hydration');
END;


-- ============================================
-- INTERPRETATIONS (IMMUTABLE)
-- ============================================

CREATE TABLE interpretations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    job_id INTEGER NOT NULL,
    hydration_id INTEGER NOT NULL,

    interpretation_hash TEXT NOT NULL,

    schema_version TEXT NOT NULL,
    validator_version TEXT NOT NULL,
    interpreter_version TEXT NOT NULL,
    interpreter_config_hash TEXT NOT NULL,

    result_json TEXT NOT NULL,
    shadow_log_ref TEXT,
    is_shadow INTEGER NOT NULL CHECK (is_shadow IN (0,1)),

    created_at TEXT NOT NULL,

    FOREIGN KEY (job_id)
        REFERENCES jobs(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (hydration_id)
        REFERENCES hydrations(id)
        ON DELETE RESTRICT,

    UNIQUE (hydration_id, interpretation_hash),

    CHECK (length(interpretation_hash) = 64),
    CHECK (length(interpreter_config_hash) = 64)
);

-- Ensure hydration belongs to job
CREATE TRIGGER enforce_interpretation_job_alignment
BEFORE INSERT ON interpretations
FOR EACH ROW
BEGIN
    SELECT
        CASE
            WHEN (SELECT job_id FROM hydrations WHERE id = NEW.hydration_id) != NEW.job_id
            THEN RAISE(ABORT, 'ArtifactMismatchError: hydration does not belong to job')
        END;
END;

CREATE TRIGGER prevent_interpretation_update
BEFORE UPDATE ON interpretations
BEGIN
    SELECT RAISE(ABORT, 'ImmutableArtifactError: Interpretations are immutable');
END;

CREATE TRIGGER prevent_interpretation_delete
BEFORE DELETE ON interpretations
BEGIN
    SELECT RAISE(ABORT, 'ImmutableArtifactError: Cannot delete interpretation');
END;


-- ============================================
-- FIT SURFACES (IMMUTABLE)
-- ============================================

CREATE TABLE fit_surfaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    job_id INTEGER NOT NULL,
    interpretation_id INTEGER NOT NULL,

    fit_surface_hash TEXT NOT NULL,
    algorithm_version TEXT NOT NULL,
    algorithm_config_hash TEXT NOT NULL,

    surface_json TEXT NOT NULL,

    created_at TEXT NOT NULL,

    FOREIGN KEY (job_id)
        REFERENCES jobs(id)
        ON DELETE RESTRICT,

    FOREIGN KEY (interpretation_id)
        REFERENCES interpretations(id)
        ON DELETE RESTRICT,

    UNIQUE (interpretation_id, fit_surface_hash),

    CHECK (length(fit_surface_hash) = 64),
    CHECK (length(algorithm_config_hash) = 64)
);

-- Ensure interpretation belongs to job
CREATE TRIGGER enforce_fit_job_alignment
BEFORE INSERT ON fit_surfaces
FOR EACH ROW
BEGIN
    SELECT
        CASE
            WHEN (SELECT job_id FROM interpretations WHERE id = NEW.interpretation_id) != NEW.job_id
            THEN RAISE(ABORT, 'ArtifactMismatchError: interpretation does not belong to job')
        END;
END;

CREATE TRIGGER prevent_fit_update
BEFORE UPDATE ON fit_surfaces
BEGIN
    SELECT RAISE(ABORT, 'ImmutableArtifactError: Fit surfaces are immutable');
END;

CREATE TRIGGER prevent_fit_delete
BEFORE DELETE ON fit_surfaces
BEGIN
    SELECT RAISE(ABORT, 'ImmutableArtifactError: Cannot delete fit surface');
END;


-- ============================================
-- APPLICATIONS (CONTROLLED MUTABLE)
-- ============================================

CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    job_id INTEGER NOT NULL UNIQUE,

    status TEXT NOT NULL,
    status_updated_at TEXT NOT NULL,
    notes TEXT,
    last_touched_at TEXT NOT NULL,

    FOREIGN KEY (job_id)
        REFERENCES jobs(id)
        ON DELETE RESTRICT,

    CHECK (status IN (
        'NOT_STARTED',
        'SAVED',
        'APPLIED',
        'INTERVIEWING',
        'OFFER',
        'REJECTED',
        'WITHDRAWN'
    ))
);

-- Enforce legal transitions
CREATE TRIGGER enforce_application_transition
BEFORE UPDATE OF status ON applications
FOR EACH ROW
BEGIN
    SELECT
        CASE
            WHEN OLD.status = 'OFFER' AND NEW.status != 'WITHDRAWN'
            THEN RAISE(ABORT, 'IllegalTransitionError')

            WHEN OLD.status = 'REJECTED' AND NEW.status NOT IN ('WITHDRAWN')
            THEN RAISE(ABORT, 'IllegalTransitionError')

            WHEN OLD.status = 'NOT_STARTED' AND NEW.status NOT IN ('SAVED','APPLIED','WITHDRAWN')
            THEN RAISE(ABORT, 'IllegalTransitionError')

            WHEN OLD.status = 'SAVED' AND NEW.status NOT IN ('APPLIED','WITHDRAWN')
            THEN RAISE(ABORT, 'IllegalTransitionError')

            WHEN OLD.status = 'APPLIED' AND NEW.status NOT IN ('INTERVIEWING','REJECTED','WITHDRAWN')
            THEN RAISE(ABORT, 'IllegalTransitionError')

            WHEN OLD.status = 'INTERVIEWING' AND NEW.status NOT IN ('OFFER','REJECTED','WITHDRAWN')
            THEN RAISE(ABORT, 'IllegalTransitionError')
        END;
END;


-- ============================================
-- EVENTS (APPEND ONLY)
-- ============================================

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    job_id INTEGER,
    event_type TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL,

    FOREIGN KEY (job_id)
        REFERENCES jobs(id)
        ON DELETE RESTRICT
);

CREATE TRIGGER prevent_event_update
BEFORE UPDATE ON events
BEGIN
    SELECT RAISE(ABORT, 'ImmutableArtifactError: Events are append-only');
END;

CREATE TRIGGER prevent_event_delete
BEFORE DELETE ON events
BEGIN
    SELECT RAISE(ABORT, 'ImmutableArtifactError: Events are append-only');
END;
