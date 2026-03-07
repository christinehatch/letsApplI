import sqlite3
import tempfile

from persistence.migrate import migrate
from persistence.repos.job_user_state_repo import JobUserStateRepo
from persistence.repos.jobs_repo import JobsRepo


def _create_db() -> sqlite3.Connection:
    tmp = tempfile.NamedTemporaryFile(delete=False)
    db_path = tmp.name
    tmp.close()

    migrate(db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _insert_job(conn: sqlite3.Connection, key: str, discovered_at: str = "2026-03-01T00:00:00Z"):
    conn.execute(
        """
        INSERT INTO jobs (
            provider, external_id, provider_job_key,
            company, title, location_raw, url, posted_at, discovered_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "greenhouse_job_board_api",
            key.split(":")[-1],
            key,
            "Stripe",
            "Software Engineer",
            "San Francisco, CA",
            f"https://example.com/{key}",
            "2026-02-20T00:00:00Z",
            discovered_at,
        ),
    )


def test_set_state_inserts_new_record():
    conn = _create_db()
    repo = JobUserStateRepo(conn)

    repo.set_state("greenhouse:stripe:1", "saved")
    conn.commit()

    assert repo.get_state("greenhouse:stripe:1") == "saved"


def test_set_state_updates_existing_record():
    conn = _create_db()
    repo = JobUserStateRepo(conn)

    repo.set_state("greenhouse:stripe:1", "saved")
    repo.set_state("greenhouse:stripe:1", "applied")
    conn.commit()

    assert repo.get_state("greenhouse:stripe:1") == "applied"


def test_feed_query_returns_joined_state():
    conn = _create_db()
    _insert_job(conn, "greenhouse:stripe:1")
    JobUserStateRepo(conn).set_state("greenhouse:stripe:1", "ignored")
    conn.commit()

    jobs, total = JobsRepo(conn).list_discovery_feed_jobs(page=1, page_size=50)

    assert total == 1
    assert len(jobs) == 1
    assert jobs[0]["state"] == "ignored"


def test_list_saved_jobs_returns_saved_only():
    conn = _create_db()
    repo = JobUserStateRepo(conn)

    repo.set_state("greenhouse:stripe:1", "saved")
    repo.set_state("greenhouse:stripe:2", "applied")
    repo.set_state("greenhouse:stripe:3", "saved")
    conn.commit()

    saved = repo.list_saved_jobs()

    assert set(saved) == {"greenhouse:stripe:1", "greenhouse:stripe:3"}
