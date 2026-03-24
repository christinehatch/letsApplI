from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path


MIGRATIONS_DIR = Path("migrations")


def _is_postgres_url(value: str) -> bool:
    lowered = value.strip().lower()
    return lowered.startswith("postgres://") or lowered.startswith("postgresql://")


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _ensure_schema_table_sqlite(conn: sqlite3.Connection):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            checksum TEXT NOT NULL,
            applied_at TEXT NOT NULL
        );
        """
    )


def _applied_migrations_sqlite(conn):
    rows = conn.execute("SELECT filename, checksum FROM schema_migrations").fetchall()
    return {r[0]: r[1] for r in rows}


def _load_migration_files():
    return sorted(MIGRATIONS_DIR.glob("*.sql"))


def _migrate_sqlite(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("BEGIN")
        _ensure_schema_table_sqlite(conn)
        applied = _applied_migrations_sqlite(conn)
        files = _load_migration_files()

        for file in files:
            content = file.read_bytes()
            checksum = _sha256(content)

            if file.name in applied:
                if applied[file.name] != checksum:
                    raise RuntimeError(f"Migration checksum mismatch: {file.name}")
                continue

            sql = content.decode("utf-8")
            conn.executescript(sql)
            conn.execute(
                """
                INSERT INTO schema_migrations
                (filename, checksum, applied_at)
                VALUES (?, ?, datetime('now'))
                """,
                (file.name, checksum),
            )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _migrate_postgres(database_url: str) -> None:
    from psycopg import connect

    conn = connect(database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id BIGSERIAL PRIMARY KEY,
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
                    is_archived INTEGER NOT NULL DEFAULT 0,
                    first_seen_at TEXT
                );
                """
            )
            cur.execute(
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
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS job_interpretations (
                    job_id TEXT PRIMARY KEY,
                    interpretation_json TEXT NOT NULL,
                    model_version TEXT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    span_map_json TEXT
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS interpretation_attempts (
                    id BIGSERIAL PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    raw_llm_output TEXT,
                    validation_error TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS hydrations (
                    id BIGSERIAL PRIMARY KEY,
                    job_id BIGINT NOT NULL REFERENCES jobs(id) ON DELETE RESTRICT,
                    hydration_hash TEXT NOT NULL,
                    raw_content TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    hydrator_version TEXT NOT NULL,
                    hydrator_config_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE (job_id, hydration_hash)
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS interpretations (
                    id BIGSERIAL PRIMARY KEY,
                    job_id BIGINT NOT NULL REFERENCES jobs(id) ON DELETE RESTRICT,
                    hydration_id BIGINT NOT NULL REFERENCES hydrations(id) ON DELETE RESTRICT,
                    interpretation_hash TEXT NOT NULL,
                    schema_version TEXT NOT NULL,
                    validator_version TEXT NOT NULL,
                    interpreter_version TEXT NOT NULL,
                    interpreter_config_hash TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    shadow_log_ref TEXT,
                    is_shadow INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE (hydration_id, interpretation_hash)
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS fit_surfaces (
                    id BIGSERIAL PRIMARY KEY,
                    job_id BIGINT NOT NULL REFERENCES jobs(id) ON DELETE RESTRICT,
                    interpretation_id BIGINT NOT NULL REFERENCES interpretations(id) ON DELETE RESTRICT,
                    fit_surface_hash TEXT NOT NULL,
                    algorithm_version TEXT NOT NULL,
                    algorithm_config_hash TEXT NOT NULL,
                    surface_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE (interpretation_id, fit_surface_hash)
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS applications (
                    id BIGSERIAL PRIMARY KEY,
                    job_id BIGINT NOT NULL UNIQUE REFERENCES jobs(id) ON DELETE RESTRICT,
                    status TEXT NOT NULL,
                    status_updated_at TEXT NOT NULL,
                    notes TEXT,
                    last_touched_at TEXT NOT NULL
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id BIGSERIAL PRIMARY KEY,
                    job_id BIGINT REFERENCES jobs(id) ON DELETE RESTRICT,
                    event_type TEXT NOT NULL,
                    payload_json TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_interpretation_attempts_job_time
                ON interpretation_attempts(job_id, timestamp DESC);
                """
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def migrate(db_path: str):
    if _is_postgres_url(db_path):
        _migrate_postgres(db_path)
        return
    _migrate_sqlite(db_path)
