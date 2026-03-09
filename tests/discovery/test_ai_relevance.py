import json
import sqlite3
import tempfile

from discovery.models import DiscoveredJob
from discovery.signals.ai_relevance import compute_ai_relevance
from discovery.store import DiscoveryStore
from persistence.migrate import migrate


def test_strong_ai_role_scores_high():
    result = compute_ai_relevance(
        title="Senior Applied AI Engineer",
        description=(
            "Build LLM systems, prompt engineering workflows, and an "
            "evaluation pipeline for production quality."
        ),
        metadata=None,
        tags=None,
    )

    assert result["ai_relevance_score"] >= 0.75
    assert "direct_ai_language" in result["ai_signal_categories"]


def test_ai_adjacent_infra_role_scores_adjacent():
    result = compute_ai_relevance(
        title="Platform Engineer",
        description="Own model serving and inference platform reliability.",
        metadata=None,
        tags=None,
    )

    assert result["ai_relevance_score"] >= 0.40
    assert "ai_infrastructure" in result["ai_signal_categories"]


def test_ai_product_role_categorized_correctly():
    result = compute_ai_relevance(
        title="Product Manager",
        description="Own conversational interface and human-in-the-loop review flows.",
        metadata=None,
        tags=None,
    )

    assert "ai_product" in result["ai_signal_categories"]


def test_weak_only_role_stays_low():
    result = compute_ai_relevance(
        title="Software Engineer",
        description="Strong python and analytics background required.",
        metadata=None,
        tags=None,
    )

    assert result["ai_relevance_score"] < 0.40


def test_no_ai_signals_scores_zero():
    result = compute_ai_relevance(
        title="Office Manager",
        description="Coordinate calendars and onsite meetings.",
        metadata=None,
        tags=None,
    )

    assert result["ai_relevance_score"] == 0.0
    assert result["ai_signal_categories"] == []
    assert result["ai_signal_reasons"] == []
    assert result["ai_signal_matches"] == []


def test_description_only_ai_terms_produce_non_zero_score():
    result = compute_ai_relevance(
        title="Software Engineer",
        description="Build infrastructure for large language model evaluation pipelines.",
        metadata=None,
        tags=None,
    )

    assert result["ai_relevance_score"] > 0.0
    assert "large language model" in result["ai_signal_matches"]


def test_discovery_store_persists_ai_relevance_metadata():
    tmp = tempfile.NamedTemporaryFile(delete=False)
    db_path = tmp.name
    tmp.close()

    migrate(db_path)
    store = DiscoveryStore(db_path)

    job = DiscoveredJob(
        job_uid="lever:demo:123",
        company="DemoCo",
        source_signal_id="sig-1",
        external_job_id="123",
        title="Applied AI Engineer",
        location="Remote",
        url="https://example.com/jobs/123",
        first_seen_at=0.0,
        last_seen_at=0.0,
        status="active",
        raw_meta={"departments": ["AI Platform"]},
    )

    store.upsert_jobs([job])

    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT raw_provider_payload_json FROM jobs WHERE provider_job_key = ?",
        ("lever:demo:123",),
    ).fetchone()
    conn.close()

    payload = json.loads(row[0])
    assert "ai_relevance_score" in payload
    assert "ai_signal_categories" in payload
    assert "ai_signal_reasons" in payload
    assert "ai_signal_matches" in payload
