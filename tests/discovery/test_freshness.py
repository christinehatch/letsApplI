"""Posted dates come from the boards, and lists show the newest roles first."""

import sqlite3
import tempfile

import pytest

from discovery import today
from discovery.models import DiscoveredJob, Signal, to_utc_iso
from discovery.signals.ashby import AshbyAdapter
from discovery.signals.greenhouse import GreenhouseAdapter
from discovery.signals.lever import LeverAdapter
from discovery.store import DiscoveryStore
from persistence.migrate import migrate
from persistence.repos.jobs_repo import JobsRepo
from persistence.repos.saved_searches_repo import SavedSearchesRepo


@pytest.mark.parametrize(
    "value,expected",
    [
        ("2026-09-03T13:30:34-04:00", "2026-09-03T17:30:34+00:00"),
        ("2026-11-10T00:00:00Z", "2026-11-10T00:00:00+00:00"),
        ("2021-04-27T20:13:45.158+00:00", "2021-04-27T20:13:45+00:00"),
        ("2026-11-10T08:00:00", "2026-11-10T08:00:00+00:00"),
        (1762992000000, "2025-11-13T00:00:00+00:00"),
        (None, None),
        ("", None),
        ("not a date", None),
        (True, None),
    ],
)
def test_to_utc_iso(value, expected):
    assert to_utc_iso(value) == expected


class _Fake:
    """Feed a canned board response to an adapter without the network."""

    def __init__(self, payload):
        self.payload = payload

    def read(self):
        import json

        return json.dumps(self.payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _poll(monkeypatch, adapter, signal, payload):
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: _Fake(payload))
    return adapter.poll(signal)


def test_greenhouse_uses_first_published(monkeypatch):
    sig = Signal(signal_id="greenhouse:stripe", company="Stripe", method="greenhouse_job_board_api",
                 config={"board_token": "stripe"})
    payload = {"jobs": [{"id": 1, "title": "Engineer", "location": {"name": "SF"}, "absolute_url": "https://x",
                         "updated_at": "2026-10-29T10:42:09-04:00", "first_published": "2026-09-03T13:30:34-04:00"}]}
    [job] = _poll(monkeypatch, GreenhouseAdapter(), sig, payload)
    assert job.posted_at == "2026-09-03T17:30:34+00:00"


def test_lever_uses_created_at(monkeypatch):
    sig = Signal(signal_id="lever:plaid", company="Plaid", method="lever_job_board_api",
                 config={"company_slug": "plaid"})
    payload = [{"id": "a", "text": "Engineer", "hostedUrl": "https://x", "createdAt": 1762992000000}]
    [job] = _poll(monkeypatch, LeverAdapter(), sig, payload)
    assert job.posted_at == "2025-11-13T00:00:00+00:00"


def test_ashby_uses_published_at():
    sig = Signal(signal_id="ashby:linear", company="Linear", method="ashby_job_board_api",
                 config={"board_name": "linear"})
    [job] = AshbyAdapter().parse(sig, "linear", {"jobs": [
        {"id": "a1", "title": "Engineer", "jobUrl": "https://x", "publishedAt": "2026-11-10T00:00:00Z"}]})
    assert job.posted_at == "2026-11-10T00:00:00+00:00"


def test_missing_date_stays_empty():
    sig = Signal(signal_id="ashby:linear", company="Linear", method="ashby_job_board_api",
                 config={"board_name": "linear"})
    [job] = AshbyAdapter().parse(sig, "linear", {"jobs": [{"id": "a1", "title": "Engineer", "jobUrl": "https://x"}]})
    assert job.posted_at is None


# ------------------------------------------------------------
# Stored and sorted
# ------------------------------------------------------------

def job(job_id, title, posted_at):
    return DiscoveredJob(
        job_uid=f"greenhouse:acme:{job_id}", company="Acme", source_signal_id="greenhouse:acme",
        external_job_id=job_id, title=title, location="San Francisco", url="https://x",
        first_seen_at=0.0, last_seen_at=0.0, posted_at=posted_at,
    )


@pytest.fixture
def db():
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".db").name
    migrate(path)
    DiscoveryStore(path).upsert_jobs(incoming=[
        job("old", "Engineer Old", "2026-01-05T00:00:00+00:00"),
        job("new", "Engineer New", "2026-11-15T00:00:00+00:00"),
        job("mid", "Engineer Mid", "2026-06-01T00:00:00+00:00"),
    ])
    return path


def test_posted_date_is_stored_and_returned(db):
    conn = sqlite3.connect(db)
    jobs, _ = JobsRepo(conn).list_discovery_feed_jobs()
    conn.close()
    assert {j["job_id"]: j["posted_at"] for j in jobs}["greenhouse:acme:new"] == "2026-11-15T00:00:00+00:00"


def test_feed_lists_newest_posting_first(db):
    conn = sqlite3.connect(db)
    jobs, _ = JobsRepo(conn).list_discovery_feed_jobs()
    conn.close()
    assert [j["job_id"].split(":")[-1] for j in jobs] == ["new", "mid", "old"]


def test_keyword_relevance_still_wins_over_freshness(db):
    DiscoveryStore(db).upsert_jobs(incoming=[job("ml", "ML Engineer", "2020-01-01T00:00:00+00:00")])
    conn = sqlite3.connect(db)
    jobs, _ = JobsRepo(conn).list_discovery_feed_jobs(role="ml engineer")
    conn.close()
    assert jobs[0]["job_id"] == "greenhouse:acme:ml"


def test_today_shows_newest_first_with_posted_date(db):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    searches = SavedSearchesRepo(conn)
    searches.create(role="engineer", include_existing=True)
    conn.commit()
    result = today.build_today(JobsRepo(conn), searches.list())
    conn.close()
    items = [i for i in result["items"] if i["source"].get("type") != "later"]
    assert [i["title"] for i in items] == ["Engineer New", "Engineer Mid", "Engineer Old"]
    assert items[0]["posted_at"] == "2026-11-15T00:00:00+00:00"
