import sqlite3
import tempfile
from pathlib import Path
import pytest

from persistence.migrate import migrate


def create_test_db():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    db_path = tmp.name
    tmp.close()

    migrate(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def insert_minimal_job(conn):
    conn.execute(
        """
        INSERT INTO jobs (
            provider, external_id, provider_job_key,
            company, title, url, discovered_at
        )
        VALUES ('greenhouse', '123', 'greenhouse:123',
                'TestCo', 'Engineer', 'http://x', '2024-01-01')
        """
    )
    return conn.execute("SELECT id FROM jobs").fetchone()[0]


# ---------------------------------------------------------
# Immutable Artifact Tests
# ---------------------------------------------------------

def test_hydration_is_immutable():
    conn = create_test_db()
    job_id = insert_minimal_job(conn)

    conn.execute(
        """
        INSERT INTO hydrations (
            job_id, hydration_hash, raw_content,
            content_type, hydrator_version,
            hydrator_config_hash, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            job_id,
            "a" * 64,
            "content",
            "text",
            "v1",
            "b" * 64,
            "2024-01-01",
        ),
    )

    with pytest.raises(sqlite3.DatabaseError):
        conn.execute(
            "UPDATE hydrations SET raw_content = 'changed'"
        )


def test_interpretation_requires_matching_job():
    conn = create_test_db()
    job_id = insert_minimal_job(conn)

    conn.execute(
        """
        INSERT INTO hydrations (
            job_id, hydration_hash, raw_content,
            content_type, hydrator_version,
            hydrator_config_hash, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            job_id,
            "a" * 64,
            "content",
            "text",
            "v1",
            "b" * 64,
            "2024-01-01",
        ),
    )

    hydration_id = conn.execute(
        "SELECT id FROM hydrations"
    ).fetchone()[0]

    with pytest.raises(sqlite3.DatabaseError):
        conn.execute(
            """
            INSERT INTO interpretations (
                job_id, hydration_id,
                interpretation_hash,
                schema_version, validator_version,
                interpreter_version, interpreter_config_hash,
                result_json, is_shadow, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id + 1,  # wrong job
                hydration_id,
                "c" * 64,
                "1",
                "1",
                "1",
                "d" * 64,
                "{}",
                0,
                "2024-01-01",
            ),
        )


def test_soft_delete_prevents_unarchive():
    conn = create_test_db()
    job_id = insert_minimal_job(conn)

    conn.execute(
        "UPDATE jobs SET is_archived = 1 WHERE id = ?",
        (job_id,),
    )

    with pytest.raises(sqlite3.DatabaseError):
        conn.execute(
            "UPDATE jobs SET is_archived = 0 WHERE id = ?",
            (job_id,),
        )


def test_hash_length_enforced():
    conn = create_test_db()
    job_id = insert_minimal_job(conn)

    with pytest.raises(sqlite3.DatabaseError):
        conn.execute(
            """
            INSERT INTO hydrations (
                job_id, hydration_hash, raw_content,
                content_type, hydrator_version,
                hydrator_config_hash, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                "short",
                "content",
                "text",
                "v1",
                "b" * 64,
                "2024-01-01",
            ),
        )


def test_application_illegal_transition():
    conn = create_test_db()
    job_id = insert_minimal_job(conn)

    conn.execute(
        """
        INSERT INTO applications (
            job_id, status,
            status_updated_at, last_touched_at
        )
        VALUES (?, 'APPLIED', '2024-01-01', '2024-01-01')
        """,
        (job_id,),
    )

    with pytest.raises(sqlite3.DatabaseError):
        conn.execute(
            """
            UPDATE applications
            SET status = 'NOT_STARTED'
            WHERE job_id = ?
            """,
            (job_id,),
        )


# ---------------------------------------------------------
# Discovery Provider-Agnostic Invariants
# ---------------------------------------------------------

def test_provider_matches_job_uid_prefix():
    conn = create_test_db()

    # Insert multiple providers deterministically
    conn.execute(
        """
        INSERT INTO jobs (
            provider, external_id, provider_job_key,
            company, title, url, discovered_at
        )
        VALUES
        ('greenhouse', '1', 'greenhouse:abc:1', 'CoA', 'T1', 'u', '2024-01-01'),
        ('lever', '2', 'lever:def:2', 'CoB', 'T2', 'u', '2024-01-01')
        """
    )

    rows = conn.execute(
        "SELECT provider, provider_job_key FROM jobs"
    ).fetchall()

    for provider, provider_job_key in rows:
        expected = provider_job_key.split(":")[0]
        assert provider == expected


def test_posted_at_remains_null():
    conn = create_test_db()

    conn.execute(
        """
        INSERT INTO jobs (
            provider, external_id, provider_job_key,
            company, title, url, discovered_at
        )
        VALUES ('lever', '123', 'lever:x:123',
                'TestCo', 'Engineer', 'http://x', '2024-01-01')
        """
    )

    row = conn.execute(
        "SELECT posted_at FROM jobs"
    ).fetchone()

    assert row[0] is None


def test_provider_job_key_uniqueness():
    conn = create_test_db()

    conn.execute(
        """
        INSERT INTO jobs (
            provider, external_id, provider_job_key,
            company, title, url, discovered_at
        )
        VALUES ('greenhouse', '1', 'greenhouse:abc:1',
                'TestCo', 'Engineer', 'http://x', '2024-01-01')
        """
    )

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO jobs (
                provider, external_id, provider_job_key,
                company, title, url, discovered_at
            )
            VALUES ('greenhouse', '1', 'greenhouse:abc:1',
                    'TestCo', 'Engineer', 'http://x', '2024-01-01')
            """
        )


def test_no_provider_specific_columns():
    conn = create_test_db()

    cols = conn.execute(
        "PRAGMA table_info(jobs)"
    ).fetchall()

    col_names = {c[1] for c in cols}

    # Ensure schema remains provider-neutral
    assert "greenhouse_specific_field" not in col_names
    assert "lever_specific_field" not in col_names