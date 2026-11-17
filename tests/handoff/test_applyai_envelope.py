"""
letsA(ppl)I side of the applyAI role handoff (docs/APPLYAI_HANDOFF_CONTRACT.md §9).
"""

import importlib.util
import json
import sqlite3
import tempfile
from pathlib import Path

import pytest
from fastapi import HTTPException

import state as state_module
from handoff.applyai_envelope import (
    FRAMING,
    MAX_QUOTE_CHARS,
    EnvelopeBuildError,
    build_applyai_envelope,
)
from persistence.migrate import migrate
from persistence.repos.job_interpretation_repo import JobInterpretationRepo
from persistence.repos.job_user_state_repo import JobUserStateRepo

JOB_ID = "greenhouse:exampleco:42"

SPAN_MAP = {
    "span_1": "<p>We build and run the internal deployment platform used by every team.</p>",
    "span_2": "You will own our CI/CD pipelines end to end &amp; keep them fast.",
    "span_3": "We move fast and value ownership above all else in this team.",
}


def make_interpretation(**overrides):
    interp = {
        "schema_version": "5.2.0",
        "RoleSummary": {"summary_text": "Builds the deployment platform.", "evidence_span_ids": ["span_1"]},
        "RequirementsAnalysis": {
            "explicit_requirements": [
                {"requirement_text": "Kubernetes experience", "modality": "required", "source_span_id": "span_2"},
            ],
            "implicit_signals": [
                {"signal_text": "IMPLICIT-SIGNAL-MUST-NOT-LEAK", "evidence_span_ids": ["span_3"]},
            ],
        },
        "CapabilityEmphasisSignals": [
            {"domain_label": "Infrastructure automation", "description": "Automating deploys.", "evidence_span_ids": ["span_2"]},
        ],
        "ProjectOpportunitySignals": [
            {"capability_surface": "Deployment pipeline", "description": "A small pipelined service.", "evidence_span_ids": ["span_2", "span_1"]},
        ],
        "InterpretationResult": {"structural_notes": "Detailed on tooling."},
        "confidence": "HIGH",
    }
    interp.update(overrides)
    return interp


def build(**overrides):
    kwargs = dict(
        job_id=JOB_ID,
        company="ExampleCo",
        title="Platform Engineer",
        job_url="https://boards.example.com/exampleco/jobs/42",
        interpretation=make_interpretation(),
        span_map=SPAN_MAP,
        interpreted_at="2026-11-10 18:00:00",
    )
    kwargs.update(overrides)
    return build_applyai_envelope(**kwargs)


# ------------------------------------------------------------
# Builder
# ------------------------------------------------------------

def test_envelope_contains_only_allowlisted_fields():
    env = build()

    assert set(env) == {"handoff_version", "source", "role", "framing"}  # handoff_id added by UI
    assert set(env["source"]) == {
        "system", "job_id", "company", "title", "job_url",
        "interpretation_schema_version", "interpreted_at",
    }
    assert set(env["role"]) == {
        "summary_text", "explicit_requirements", "capability_emphasis",
        "project_opportunities", "structural_notes", "confidence",
    }
    assert set(env["role"]["explicit_requirements"][0]) == {"requirement_text", "modality"}
    assert set(env["role"]["capability_emphasis"][0]) == {"domain_label", "description", "evidence"}
    assert set(env["role"]["project_opportunities"][0]) == {"capability_surface", "description", "evidence"}
    assert env["handoff_version"] == "1.0"
    assert env["source"]["system"] == "letsappli"
    assert env["framing"] == FRAMING


def test_excluded_fields_never_appear():
    interp = make_interpretation()
    interp["ResumeAlignment"] = {"strength_matches": ["RESUME-MUST-NOT-LEAK"]}
    interp["pipeline_status"] = "applied"

    raw = json.dumps(build(interpretation=interp))

    assert "IMPLICIT-SIGNAL-MUST-NOT-LEAK" not in raw
    assert "RESUME-MUST-NOT-LEAK" not in raw
    assert "applied" not in raw
    assert "span_" not in raw  # span ids are resolved to text, never sent
    assert "source_span_id" not in raw
    assert "evidence_span_ids" not in raw


def test_spans_resolve_to_plain_text_quotes_in_order():
    env = build()

    assert env["role"]["capability_emphasis"][0]["evidence"] == [
        "You will own our CI/CD pipelines end to end & keep them fast.",
    ]
    assert env["role"]["project_opportunities"][0]["evidence"] == [
        "You will own our CI/CD pipelines end to end & keep them fast.",
        "We build and run the internal deployment platform used by every team.",
    ]


@pytest.mark.parametrize("raw, expected", [
    ('-start-pos="1337"> What You’ll Do: Build pipelines', "What You’ll Do: Build pipelines"),
    ("Make the research stack observable <p data-render", "Make the research stack observable"),
    ('os="2533">You are proficient in Python <li cla', "You are proficient in Python"),
    ("/p> Contribute high-quality code", "Contribute high-quality code"),
    ("Plain text with a > comparison inside", "Plain text with a > comparison inside"),
    ("<p>Whole <strong>tags</strong> are removed.</p>", "Whole tags are removed."),
])
def test_quotes_drop_tags_cut_by_span_boundaries(raw, expected):
    env = build(span_map={**SPAN_MAP, "span_2": raw})
    assert env["role"]["capability_emphasis"][0]["evidence"] == [expected]


def test_long_quotes_are_capped():
    env = build(span_map={**SPAN_MAP, "span_2": "x" * 2000})
    quote = env["role"]["capability_emphasis"][0]["evidence"][0]
    assert len(quote) == MAX_QUOTE_CHARS
    assert quote.endswith("…")


def test_timestamp_is_normalized_to_iso_utc():
    assert build()["source"]["interpreted_at"] == "2026-11-10T18:00:00Z"
    assert build(interpreted_at="2026-11-10T20:00:00+02:00")["source"]["interpreted_at"] == "2026-11-10T18:00:00Z"


@pytest.mark.parametrize("kwargs, message", [
    ({"span_map": {"span_1": SPAN_MAP["span_1"]}}, "missing span"),
    ({"span_map": {**SPAN_MAP, "span_2": "<br/>  "}}, "empty span"),
    ({"job_url": "http://boards.example.com/42"}, "https"),
    ({"interpretation": make_interpretation(schema_version="4.0")}, "schema"),
    ({"interpretation": make_interpretation(CapabilityEmphasisSignals=[])}, "no capability"),
    ({"interpreted_at": ""}, "timestamp"),
])
def test_missing_or_bad_data_aborts(kwargs, message):
    with pytest.raises(EnvelopeBuildError, match=message):
        build(**kwargs)


def test_oversize_envelope_aborts():
    interp = make_interpretation(
        InterpretationResult={"structural_notes": "x" * 70_000},
    )
    with pytest.raises(EnvelopeBuildError, match="64 KB"):
        build(interpretation=interp)


# ------------------------------------------------------------
# Compatibility with applyAI's own validator (when checked out next door)
# ------------------------------------------------------------

def _load_applyai_handoff():
    path = Path(__file__).resolve().parents[2].parent / "career_explorer" / "phase6" / "handoff.py"
    if not path.exists():
        pytest.skip("career_explorer is not checked out next to letsApplI")
    spec = importlib.util.spec_from_file_location("applyai_phase6_handoff", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_envelope_passes_applyai_validator():
    applyai = _load_applyai_handoff()
    env = {**build(), "handoff_id": "0b0e6c2a-1d4e-4f55-9d1a-0e7a3c5d8f10"}

    clean = applyai.validate_envelope(env)

    assert clean["source"]["title"] == "Platform Engineer"


# ------------------------------------------------------------
# Endpoint: GET /api/applyai-envelope
# ------------------------------------------------------------

def _db(provider_description=None):
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".db").name
    migrate(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    payload = json.dumps({"description_text": provider_description}) if provider_description else None
    conn.execute(
        """
        INSERT INTO jobs (provider, external_id, provider_job_key, company, title,
                          location_raw, url, discovered_at, raw_provider_payload_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("greenhouse", "42", JOB_ID, "ExampleCo", "Platform Engineer", "Remote",
         "https://boards.example.com/exampleco/jobs/42", "2026-11-01T00:00:00Z", payload),
    )
    conn.commit()
    return path, conn


def _snapshot(conn):
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    return {t: [tuple(r) for r in conn.execute(f"SELECT * FROM {t}")] for t in tables}


@pytest.fixture
def db(monkeypatch):
    path, conn = _db(provider_description="\n\n".join(SPAN_MAP.values()))
    monkeypatch.setattr(state_module, "DB_PATH", path)
    yield conn
    conn.close()


async def _call(job_id=JOB_ID):
    import bridge_server
    return await bridge_server.applyai_envelope(job_id=job_id)


async def test_endpoint_returns_envelope_and_writes_nothing(db):
    JobInterpretationRepo(db).save_interpretation(JOB_ID, make_interpretation(), "test", span_map=SPAN_MAP)
    JobUserStateRepo(db).set_state(JOB_ID, "saved")
    db.commit()
    before = _snapshot(db)

    result = await _call()

    assert result["envelope"]["source"]["job_id"] == JOB_ID
    assert "handoff_id" not in result["envelope"]
    assert "saved" not in json.dumps(result)  # pipeline state is not sent
    assert _snapshot(db) == before


async def test_endpoint_404_without_interpretation(db):
    with pytest.raises(HTTPException) as exc:
        await _call()
    assert exc.value.status_code == 404


async def test_endpoint_404_for_unknown_job(db):
    with pytest.raises(HTTPException) as exc:
        await _call("greenhouse:nope:1")
    assert exc.value.status_code == 404


async def test_endpoint_409_when_stale_and_does_not_delete(monkeypatch):
    path, conn = _db(provider_description="A completely different posting with none of the original text at all.")
    monkeypatch.setattr(state_module, "DB_PATH", path)
    JobInterpretationRepo(conn).save_interpretation(JOB_ID, make_interpretation(), "test", span_map=SPAN_MAP)
    before = _snapshot(conn)

    with pytest.raises(HTTPException) as exc:
        await _call()

    assert exc.value.status_code == 409
    assert _snapshot(conn) == before
    conn.close()


async def test_endpoint_422_when_spans_missing(db):
    JobInterpretationRepo(db).save_interpretation(JOB_ID, make_interpretation(), "test", span_map={})

    with pytest.raises(HTTPException) as exc:
        await _call()

    assert exc.value.status_code == 422
    assert "missing span" in exc.value.detail
