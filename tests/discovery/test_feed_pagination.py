import sqlite3
import tempfile

from persistence.migrate import migrate
from persistence.repos.jobs_repo import JobsRepo


def _create_db_with_many_jobs(total: int = 120) -> sqlite3.Connection:
    tmp = tempfile.NamedTemporaryFile(delete=False)
    db_path = tmp.name
    tmp.close()

    migrate(db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    rows = []
    for i in range(total):
        company = "Stripe" if i % 2 == 0 else "OpenAI"
        title = "Senior Software Engineer" if i % 3 == 0 else "Product Manager"
        location_raw = "San Francisco, CA" if i % 4 < 2 else "Remote - US"
        location_norm = "san_francisco" if i % 4 < 2 else "remote_us"

        rows.append(
            (
                "greenhouse",
                str(i),
                f"greenhouse:test:{i}",
                company,
                title,
                location_raw,
                location_norm,
                f"https://example.com/{i}",
                f"2026-01-01T00:00:{i:04d}Z",
            )
        )

    conn.executemany(
        """
        INSERT INTO jobs (
            provider, external_id, provider_job_key,
            company, title, location_raw, location_norm,
            url, discovered_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    return conn


def test_page_1_returns_expected_count():
    conn = _create_db_with_many_jobs()
    repo = JobsRepo(conn)

    jobs, total_jobs = repo.list_discovery_feed_jobs(page=1, page_size=50)

    assert len(jobs) == 50
    assert total_jobs == 120


def test_page_2_returns_different_results():
    conn = _create_db_with_many_jobs()
    repo = JobsRepo(conn)

    page1_jobs, _ = repo.list_discovery_feed_jobs(page=1, page_size=25)
    page2_jobs, _ = repo.list_discovery_feed_jobs(page=2, page_size=25)

    assert len(page1_jobs) == 25
    assert len(page2_jobs) == 25
    assert page1_jobs[0]["job_id"] != page2_jobs[0]["job_id"]


def test_page_size_is_respected():
    conn = _create_db_with_many_jobs()
    repo = JobsRepo(conn)

    jobs, _ = repo.list_discovery_feed_jobs(page=1, page_size=30)

    assert len(jobs) == 30


def test_pagination_works_with_filters():
    conn = _create_db_with_many_jobs()
    repo = JobsRepo(conn)

    jobs, total_jobs = repo.list_discovery_feed_jobs(
        page=2,
        page_size=20,
        company="stripe",
    )

    assert total_jobs == 60
    assert len(jobs) == 20
    assert all(j["company"] == "Stripe" for j in jobs)


def test_total_jobs_value_is_correct():
    conn = _create_db_with_many_jobs()
    repo = JobsRepo(conn)

    jobs, total_jobs = repo.list_discovery_feed_jobs(
        page=1,
        page_size=10,
        role="software",
    )

    assert len(jobs) == 10
    assert total_jobs == 40
