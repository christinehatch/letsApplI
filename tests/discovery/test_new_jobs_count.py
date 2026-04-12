import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from persistence.migrate import migrate
from persistence.repos.jobs_repo import JobsRepo


def _create_db_with_discovered_jobs() -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False)
    db_path = tmp.name
    tmp.close()

    migrate(db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executemany(
        """
        INSERT INTO jobs (
            provider, external_id, provider_job_key,
            company, title, location_raw, url, discovered_at, is_archived
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            ("greenhouse", "1", "greenhouse:test:1", "A", "Role A", "Remote", "https://a", "2026-01-01T00:00:00Z", 0),
            ("greenhouse", "2", "greenhouse:test:2", "B", "Role B", "Remote", "https://b", "2026-01-03T00:00:00Z", 0),
            ("greenhouse", "3", "greenhouse:test:3", "C", "Role C", "Remote", "https://c", "2026-01-04T00:00:00Z", 0),
        ],
    )
    conn.commit()
    conn.close()
    return db_path


def test_repo_count_jobs_since_returns_correct_count():
    db_path = _create_db_with_discovered_jobs()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        repo = JobsRepo(conn)
        assert repo.count_jobs_since("2026-01-02T00:00:00Z") == 2
    finally:
        conn.close()


@pytest.mark.asyncio
async def test_new_jobs_count_endpoint_returns_json_shape(monkeypatch):
    import bridge_server
    from src import state as state_module
    from src import user_session

    db_path = _create_db_with_discovered_jobs()
    session_path = Path(tempfile.NamedTemporaryFile(delete=False).name)
    session_path.write_text(
        json.dumps({"last_seen_at": "2026-01-02T00:00:00Z"}),
        encoding="utf-8",
    )

    monkeypatch.setattr(state_module, "DB_PATH", db_path)
    monkeypatch.setattr(user_session, "DEFAULT_SESSION_PATH", session_path)

    payload = await bridge_server.new_jobs_count()

    assert isinstance(payload, dict)
    assert "new_jobs" in payload
    assert payload["new_jobs"] == 2
