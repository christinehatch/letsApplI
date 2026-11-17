"""Roles that vanish from their company's board are closed and hidden."""

import sqlite3
import tempfile

import pytest

from discovery.models import DiscoveredJob, Signal
from discovery.loop import board_prefix
from discovery.store import DiscoveryStore
from discovery import today
from persistence.migrate import migrate
from persistence.repos.jobs_repo import JobsRepo
from persistence.repos.saved_searches_repo import SavedSearchesRepo


def job(board: str, job_id: str, title: str = "Engineer", provider: str = "greenhouse") -> DiscoveredJob:
    return DiscoveredJob(
        job_uid=f"{provider}:{board}:{job_id}",
        company=board.title(),
        source_signal_id=f"{provider}:{board}",
        external_job_id=job_id,
        title=title,
        location="San Francisco, CA",
        url=f"https://example.com/{job_id}",
        first_seen_at=0.0,
        last_seen_at=0.0,
        status="active",
        raw_meta={},
    )


@pytest.fixture
def db():
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".db").name
    migrate(path)
    return path


def feed_ids(db, **filters):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    try:
        jobs, total = JobsRepo(conn).list_discovery_feed_jobs(page_size=100, **filters)
        assert total == len(jobs)
        return {j["job_id"] for j in jobs}
    finally:
        conn.close()


def closed(db):
    conn = sqlite3.connect(db)
    try:
        return {r[0] for r in conn.execute("SELECT provider_job_key FROM jobs WHERE closed_at IS NOT NULL")}
    finally:
        conn.close()


def check_board(store, board, jobs):
    store.upsert_jobs(incoming=jobs)
    return store.close_missing(f"greenhouse:{board}:", [j.job_uid for j in jobs])


def test_role_missing_from_next_check_is_closed_and_hidden(db):
    store = DiscoveryStore(db)
    check_board(store, "stripe", [job("stripe", "1"), job("stripe", "2")])
    assert check_board(store, "stripe", [job("stripe", "1")]) == 1
    assert closed(db) == {"greenhouse:stripe:2"}
    assert feed_ids(db) == {"greenhouse:stripe:1"}


def test_other_boards_are_untouched(db):
    store = DiscoveryStore(db)
    check_board(store, "stripe", [job("stripe", "1")])
    check_board(store, "figma", [job("figma", "9")])
    check_board(store, "stripe", [job("stripe", "1")])
    assert closed(db) == set()


def test_board_name_prefix_does_not_leak_to_similar_names(db):
    store = DiscoveryStore(db)
    check_board(store, "stripe", [job("stripe", "1")])
    check_board(store, "stripe2", [job("stripe2", "5")])
    check_board(store, "stripe", [job("stripe", "1")])
    assert closed(db) == set()


def test_empty_check_closes_nothing(db):
    store = DiscoveryStore(db)
    check_board(store, "stripe", [job("stripe", "1")])
    assert check_board(store, "stripe", []) == 0
    assert closed(db) == set()


def test_role_that_reappears_is_reopened(db):
    store = DiscoveryStore(db)
    check_board(store, "stripe", [job("stripe", "1"), job("stripe", "2")])
    check_board(store, "stripe", [job("stripe", "1")])
    check_board(store, "stripe", [job("stripe", "1"), job("stripe", "2")])
    assert closed(db) == set()


def test_jobs_from_boards_no_longer_checked_are_closed(db):
    store = DiscoveryStore(db)
    check_board(store, "stripe", [job("stripe", "1")])
    store.upsert_jobs(incoming=[job("anthropic", "7", provider="lever")])
    store.close_unchecked_boards(["greenhouse:stripe:"])
    assert closed(db) == {"lever:anthropic:7"}


def test_saved_role_stays_in_saved_jobs_marked_closed(db):
    store = DiscoveryStore(db)
    check_board(store, "stripe", [job("stripe", "1"), job("stripe", "2")])
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO job_user_state (job_id, state, updated_at) VALUES ('greenhouse:stripe:2', 'saved', '2026-11-01')"
    )
    conn.commit()
    conn.close()
    check_board(store, "stripe", [job("stripe", "1")])

    conn = sqlite3.connect(db)
    saved = JobsRepo(conn).list_saved_jobs()
    conn.close()
    assert [(j["job_id"], bool(j["closed_at"])) for j in saved] == [("greenhouse:stripe:2", True)]


def test_today_skips_closed_roles(db):
    store = DiscoveryStore(db)
    check_board(store, "stripe", [job("stripe", "1", "Engineer A"), job("stripe", "2", "Engineer B")])
    check_board(store, "stripe", [job("stripe", "1", "Engineer A")])

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    searches = SavedSearchesRepo(conn)
    searches.create(name="Eng", role="engineer", include_existing=True)
    conn.commit()
    result = today.build_today(JobsRepo(conn), searches.list())
    conn.close()
    keys = {k for item in result["items"] for k in item["job_ids"]}
    assert "greenhouse:stripe:2" not in keys
    assert "greenhouse:stripe:1" in keys


def test_provider_is_filled_from_the_job_key(db):
    DiscoveryStore(db).upsert_jobs(incoming=[job("linear", "a1", provider="ashby")])
    conn = sqlite3.connect(db)
    assert conn.execute("SELECT provider FROM jobs").fetchone()[0] == "ashby"
    conn.close()


@pytest.mark.parametrize(
    "method,config,expected",
    [
        ("greenhouse_job_board_api", {"board_token": "stripe"}, "greenhouse:stripe:"),
        ("lever_job_board_api", {"company_slug": "plaid"}, "lever:plaid:"),
        ("ashby_job_board_api", {"board_name": "linear"}, "ashby:linear:"),
        ("ashby_job_board_api", {}, ""),
        ("unknown", {"board_token": "x"}, ""),
    ],
)
def test_board_prefix(method, config, expected):
    assert board_prefix(Signal(signal_id="s", company="C", method=method, config=config)) == expected


@pytest.mark.parametrize(
    "title,has_ai",
    [
        ("Senior Art Director - Campaigns", False),
        ("Maintenance Coordinator", False),
        ("Applied AI Engineer", True),
        ("AI/ML Platform Engineer", True),
        ("Staff Product Manager - AI & Data Foundations", True),
    ],
)
def test_title_signals_match_whole_words(title, has_ai):
    from discovery.title_signal_extractor import extract_title_signals

    assert ("ai" in extract_title_signals(title)) is has_ai


def test_html_is_not_ml():
    from discovery.title_signal_extractor import extract_title_signals

    assert "ml" not in extract_title_signals("HTML Email Developer")
