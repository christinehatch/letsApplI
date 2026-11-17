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


def _insert_job(conn: sqlite3.Connection, job_id: str) -> None:
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
            "1",
            job_id,
            "ExampleCo",
            "Backend Engineer",
            "Remote",
            f"https://example.com/{job_id}",
            "2026-03-01T00:00:00Z",
            "2026-03-01T00:00:00Z",
        ),
    )


def test_ignored_job_is_removed_from_discovery_feed() -> None:
    conn = _create_db()
    job_id = "greenhouse:example:1"
    _insert_job(conn, job_id)

    state_repo = JobUserStateRepo(conn)
    state_repo.set_state(job_id, "ignored")
    conn.commit()

    jobs_repo = JobsRepo(conn)
    jobs, total_jobs = jobs_repo.list_discovery_feed_jobs(page=1, page_size=50)

    assert total_jobs == 0
    assert jobs == []
