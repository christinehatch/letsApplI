import sqlite3
import tempfile

from persistence.migrate import migrate
from persistence.repos.jobs_repo import JobsRepo


def _create_db_with_jobs() -> sqlite3.Connection:
    tmp = tempfile.NamedTemporaryFile(delete=False)
    db_path = tmp.name
    tmp.close()

    migrate(db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    rows = [
        (
            "greenhouse",
            "1",
            "greenhouse:stripe:1",
            "Stripe",
            "Senior Software Engineer",
            "San Francisco, CA",
            "san_francisco",
            "https://example.com/1",
            "2026-01-01T00:00:00Z",
        ),
        (
            "lever",
            "2",
            "lever:openai:2",
            "OpenAI",
            "Junior Backend Engineer",
            "Remote - US",
            "remote_us",
            "https://example.com/2",
            "2026-01-02T00:00:00Z",
        ),
        (
            "greenhouse",
            "3",
            "greenhouse:notion:3",
            "Notion",
            "Product Manager",
            "New York, NY",
            "new_york",
            "https://example.com/3",
            "2026-01-03T00:00:00Z",
        ),
        (
            "lever",
            "4",
            "lever:github:4",
            "GitHub",
            "Software Developer",
            "Bay Area",
            "san_francisco_bay_area",
            "https://example.com/4",
            "2026-01-04T00:00:00Z",
        ),
    ]

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


def test_discovery_feed_no_filters_returns_baseline_order():
    conn = _create_db_with_jobs()
    repo = JobsRepo(conn)

    jobs = repo.list_discovery_feed_jobs()

    assert [j["job_id"] for j in jobs] == [
        "lever:github:4",
        "greenhouse:notion:3",
        "lever:openai:2",
        "greenhouse:stripe:1",
    ]


def test_discovery_feed_filter_by_company():
    conn = _create_db_with_jobs()
    repo = JobsRepo(conn)

    jobs = repo.list_discovery_feed_jobs(company="stripe")

    assert len(jobs) == 1
    assert jobs[0]["company"] == "Stripe"


def test_discovery_feed_filter_by_role():
    conn = _create_db_with_jobs()
    repo = JobsRepo(conn)

    jobs = repo.list_discovery_feed_jobs(role="software")

    assert {j["job_id"] for j in jobs} == {
        "greenhouse:stripe:1",
        "lever:github:4",
    }


def test_discovery_feed_filter_by_location():
    conn = _create_db_with_jobs()
    repo = JobsRepo(conn)

    jobs = repo.list_discovery_feed_jobs(location="san francisco")

    assert {j["job_id"] for j in jobs} == {
        "greenhouse:stripe:1",
        "lever:github:4",
    }


def test_discovery_feed_multiple_filters_combined():
    conn = _create_db_with_jobs()
    repo = JobsRepo(conn)

    jobs = repo.list_discovery_feed_jobs(
        company="openai",
        role="backend",
        experience="junior",
        location="remote",
    )

    assert len(jobs) == 1
    assert jobs[0]["job_id"] == "lever:openai:2"
