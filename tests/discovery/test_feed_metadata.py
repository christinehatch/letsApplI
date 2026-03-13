import sqlite3
import tempfile
import json

from persistence.migrate import migrate
from persistence.repos.jobs_repo import JobsRepo


def _create_db_with_metadata() -> sqlite3.Connection:
    tmp = tempfile.NamedTemporaryFile(delete=False)
    db_path = tmp.name
    tmp.close()

    migrate(db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

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
            "greenhouse:demo:1",
            "Stripe",
            "Staff Software Engineer",
            "San Francisco, CA",
            "https://example.com/job/1",
            "2026-02-20T00:00:00Z",
            "2026-02-21T00:00:00Z",
        ),
    )
    conn.commit()
    return conn


def test_discovery_feed_returns_provider_and_posted_at_fields():
    conn = _create_db_with_metadata()
    repo = JobsRepo(conn)

    jobs, total_jobs = repo.list_discovery_feed_jobs(page=1, page_size=50)

    assert total_jobs == 1
    assert len(jobs) == 1
    assert jobs[0]["provider"] == "greenhouse_job_board_api"
    assert jobs[0]["posted_at"] == "2026-02-20T00:00:00Z"


def test_discovery_feed_returns_ai_relevance_explanation_from_interpretation_signals():
    conn = _create_db_with_metadata()

    conn.execute(
        """
        UPDATE jobs
        SET raw_provider_payload_json = ?
        WHERE provider_job_key = ?
        """,
        (
            json.dumps({"ai_relevance_score": 0.82}),
            "greenhouse:demo:1",
        ),
    )
    conn.execute(
        """
        INSERT INTO job_interpretations (job_id, interpretation_json, model_version)
        VALUES (?, ?, ?)
        """,
        (
            "greenhouse:demo:1",
            json.dumps(
                {
                    "CapabilityEmphasisSignals": [
                        {"domain_label": "GenAI Product Development"},
                        {"domain_label": "LLM Experience"},
                    ],
                    "ProjectOpportunitySignals": [
                        {"capability_surface": "AI-powered customer workflows"},
                    ],
                }
            ),
            "phase52-test",
        ),
    )
    conn.commit()

    repo = JobsRepo(conn)
    jobs, total_jobs = repo.list_discovery_feed_jobs(page=1, page_size=50)

    assert total_jobs == 1
    assert len(jobs) == 1
    assert jobs[0]["ai_relevance_score"] == 0.82
    assert jobs[0]["ai_relevance_explanation"]["level"] == "High"
    assert jobs[0]["ai_relevance_explanation"]["signals"] == [
        "GenAI Product Development",
        "LLM Experience",
        "AI-powered customer workflows",
    ]
