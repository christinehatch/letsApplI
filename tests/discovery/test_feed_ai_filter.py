import json
import sqlite3
import tempfile
from typing import Optional

from persistence.migrate import migrate
from persistence.repos.jobs_repo import JobsRepo


def _create_db() -> sqlite3.Connection:
    tmp = tempfile.NamedTemporaryFile(delete=False)
    db_path = tmp.name
    tmp.close()

    migrate(db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _insert_job(
    conn: sqlite3.Connection,
    *,
    provider_job_key: str,
    company: str,
    title: str,
    location_raw: str,
    discovered_at: str,
    ai_relevance_score: Optional[float],
) -> None:
    payload = None
    if ai_relevance_score is not None:
        payload = json.dumps({"ai_relevance_score": ai_relevance_score})

    conn.execute(
        """
        INSERT INTO jobs (
            provider, external_id, provider_job_key,
            company, title, location_raw, location_norm,
            url, discovered_at, raw_provider_payload_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "greenhouse",
            provider_job_key.split(":")[-1],
            provider_job_key,
            company,
            title,
            location_raw,
            None,
            f"https://example.com/{provider_job_key}",
            discovered_at,
            payload,
        ),
    )


def test_ai_only_filter_returns_only_jobs_with_positive_ai_score():
    conn = _create_db()
    repo = JobsRepo(conn)

    _insert_job(
        conn,
        provider_job_key="greenhouse:demo:1",
        company="Alpha",
        title="Applied AI Engineer",
        location_raw="Remote",
        discovered_at="2026-03-01T00:00:01Z",
        ai_relevance_score=0.8,
    )
    _insert_job(
        conn,
        provider_job_key="greenhouse:demo:2",
        company="Beta",
        title="Office Manager",
        location_raw="Remote",
        discovered_at="2026-03-01T00:00:02Z",
        ai_relevance_score=0.0,
    )
    _insert_job(
        conn,
        provider_job_key="greenhouse:demo:3",
        company="Gamma",
        title="Recruiter",
        location_raw="Remote",
        discovered_at="2026-03-01T00:00:03Z",
        ai_relevance_score=None,
    )
    conn.commit()

    jobs, total_jobs = repo.list_discovery_feed_jobs(ai_filter="ai_only")

    assert total_jobs == 1
    assert [j["job_id"] for j in jobs] == ["greenhouse:demo:1"]


def test_ai_only_filter_keeps_pagination_and_total_jobs_correct():
    conn = _create_db()
    repo = JobsRepo(conn)

    for i in range(25):
        _insert_job(
            conn,
            provider_job_key=f"greenhouse:bulk:{i}",
            company="BulkCo",
            title="Engineer",
            location_raw="Remote",
            discovered_at=f"2026-03-01T00:00:{i:02d}Z",
            ai_relevance_score=0.3 if i % 2 == 0 else 0.0,
        )
    conn.commit()

    jobs, total_jobs = repo.list_discovery_feed_jobs(
        page=2,
        page_size=10,
        ai_filter="ai_only",
    )

    assert total_jobs == 13
    assert len(jobs) == 3


def test_ai_only_filter_composes_with_existing_filters():
    conn = _create_db()
    repo = JobsRepo(conn)

    _insert_job(
        conn,
        provider_job_key="greenhouse:combo:1",
        company="Stripe",
        title="Software Engineer",
        location_raw="Remote - US",
        discovered_at="2026-03-01T00:00:01Z",
        ai_relevance_score=0.6,
    )
    _insert_job(
        conn,
        provider_job_key="greenhouse:combo:2",
        company="Stripe",
        title="Software Engineer",
        location_raw="Remote - US",
        discovered_at="2026-03-01T00:00:02Z",
        ai_relevance_score=0.0,
    )
    _insert_job(
        conn,
        provider_job_key="greenhouse:combo:3",
        company="OpenAI",
        title="Software Engineer",
        location_raw="Remote - US",
        discovered_at="2026-03-01T00:00:03Z",
        ai_relevance_score=0.9,
    )
    conn.commit()

    jobs, total_jobs = repo.list_discovery_feed_jobs(
        company="stripe",
        role="software",
        location="remote",
        ai_filter="ai_only",
    )

    assert total_jobs == 1
    assert len(jobs) == 1
    assert jobs[0]["job_id"] == "greenhouse:combo:1"
