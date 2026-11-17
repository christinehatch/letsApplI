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


def _insert_job(conn: sqlite3.Connection, key: str, discovered_at: str) -> None:
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
            "ExampleCo",
            "Software Engineer",
            "Remote",
            f"https://example.com/{key}",
            "2026-03-01T00:00:00Z",
            discovered_at,
        ),
    )


def test_feed_excludes_ignored_jobs() -> None:
    conn = _create_db()
    _insert_job(conn, "greenhouse:example:1", "2026-03-01T00:00:01Z")
    JobUserStateRepo(conn).set_state("greenhouse:example:1", "ignored")
    conn.commit()

    jobs, total_jobs = JobsRepo(conn).list_discovery_feed_jobs(page=1, page_size=50)

    assert total_jobs == 0
    assert jobs == []


def test_feed_includes_discovered_jobs() -> None:
    conn = _create_db()
    _insert_job(conn, "greenhouse:example:2", "2026-03-01T00:00:02Z")
    _insert_job(conn, "greenhouse:example:4", "2026-03-01T00:00:04Z")
    JobUserStateRepo(conn).set_state("greenhouse:example:4", "ignored")
    conn.commit()

    jobs, total_jobs = JobsRepo(conn).list_discovery_feed_jobs(page=1, page_size=50)

    assert total_jobs == 1
    assert len(jobs) == 1
    assert jobs[0]["job_id"] == "greenhouse:example:2"
    assert jobs[0]["state"] is None


def test_feed_includes_jobs_without_state() -> None:
    conn = _create_db()
    _insert_job(conn, "greenhouse:example:3", "2026-03-01T00:00:03Z")
    conn.commit()

    jobs, total_jobs = JobsRepo(conn).list_discovery_feed_jobs(page=1, page_size=50)

    assert total_jobs == 1
    assert len(jobs) == 1
    assert jobs[0]["job_id"] == "greenhouse:example:3"
    assert jobs[0]["state"] is None
