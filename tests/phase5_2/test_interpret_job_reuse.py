"""
POST /api/interpret-job reuses a saved interpretation that still matches the
posting, and only runs the interpreter when there is none or it is stale.
"""

import json
import sqlite3
import tempfile

import pytest

import state as state_module
from persistence.migrate import migrate
from persistence.repos.job_interpretation_repo import JobInterpretationRepo

JOB_ID = "greenhouse:exampleco:7"

POSTING = (
    "You will own our CI/CD pipelines end to end and keep them fast.\n\n"
    "We build and run the internal deployment platform used by every team."
)
SAVED_SPAN_MAP = {
    "span_1": "You will own our CI/CD pipelines end to end and keep them fast.",
    "span_2": "We build and run the internal deployment platform used by every team.",
}
SAVED = {"schema_version": "5.2.0", "RoleSummary": {"summary_text": "SAVED-INTERPRETATION"}}


def _db(posting):
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".db").name
    migrate(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        """
        INSERT INTO jobs (provider, external_id, provider_job_key, company, title,
                          location_raw, url, discovered_at)
        VALUES ('greenhouse', '7', ?, 'ExampleCo', 'Platform Engineer', 'Remote',
                'https://boards.example.com/7', '2026-11-01T00:00:00Z')
        """,
        (JOB_ID,),
    )
    conn.execute(
        """
        INSERT INTO hydrations (job_id, hydration_hash, raw_content, content_type,
                                hydrator_version, hydrator_config_hash, created_at)
        VALUES (?, ?, ?, 'text/plain', 'test', ?, '2026-11-01T00:00:00Z')
        """,
        (cur.lastrowid, "a" * 64, posting, "b" * 64),
    )
    conn.commit()
    return path, conn


def _payload():
    import bridge_server
    return bridge_server.HandoffPayload(
        job_id=JOB_ID,
        consent={"granted": True, "scope": "interpret_job_posting", "granted_at": "2026-11-17T00:00:00Z"},
    )


@pytest.fixture
def interpreter_calls(monkeypatch):
    import bridge_server
    calls = []
    original = bridge_server.Phase52Interpreter.interpret

    def spy(self):
        calls.append(1)
        return original(self)

    monkeypatch.setattr(bridge_server.Phase52Interpreter, "interpret", spy)
    return calls


async def test_saved_interpretation_is_reused_without_running_the_interpreter(monkeypatch, interpreter_calls):
    import bridge_server
    path, conn = _db(POSTING)
    monkeypatch.setattr(state_module, "DB_PATH", path)
    JobInterpretationRepo(conn).save_interpretation(JOB_ID, SAVED, "saved", span_map=SAVED_SPAN_MAP)
    before = conn.execute("SELECT interpretation_json, created_at FROM job_interpretations").fetchall()

    result = await bridge_server.handle_interpret_job(_payload())

    assert interpreter_calls == []
    assert result["reused"] is True
    assert result["interpretation"] == SAVED
    assert result["span_map"] == SAVED_SPAN_MAP
    after = conn.execute("SELECT interpretation_json, created_at FROM job_interpretations").fetchall()
    assert [tuple(r) for r in after] == [tuple(r) for r in before]
    conn.close()


async def test_stale_saved_interpretation_is_replaced(monkeypatch, interpreter_calls):
    import bridge_server
    path, conn = _db("An entirely different posting that shares none of the saved span text at all.")
    monkeypatch.setattr(state_module, "DB_PATH", path)
    JobInterpretationRepo(conn).save_interpretation(JOB_ID, SAVED, "saved", span_map=SAVED_SPAN_MAP)

    result = await bridge_server.handle_interpret_job(_payload())

    assert interpreter_calls == [1]
    assert result["reused"] is False
    stored = json.loads(conn.execute("SELECT interpretation_json FROM job_interpretations").fetchone()[0])
    assert stored != SAVED
    conn.close()


async def test_no_saved_interpretation_runs_the_interpreter(monkeypatch, interpreter_calls):
    import bridge_server
    path, conn = _db(POSTING)
    monkeypatch.setattr(state_module, "DB_PATH", path)

    result = await bridge_server.handle_interpret_job(_payload())

    assert interpreter_calls == [1]
    assert result["reused"] is False
    assert conn.execute("SELECT COUNT(*) FROM job_interpretations").fetchone()[0] == 1
    conn.close()


async def test_legacy_saved_interpretation_without_span_map_gets_spans_rebuilt(monkeypatch, interpreter_calls):
    import bridge_server
    path, conn = _db(POSTING)
    monkeypatch.setattr(state_module, "DB_PATH", path)
    JobInterpretationRepo(conn).save_interpretation(JOB_ID, SAVED, "saved", span_map=None)

    result = await bridge_server.handle_interpret_job(_payload())

    assert interpreter_calls == []
    assert result["reused"] is True
    assert result["span_map"]["span_1"].startswith("You will own our CI/CD pipelines")
    conn.close()
