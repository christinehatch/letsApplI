"""Saved searches and the Today queue (src/discovery/today.py)."""

import sqlite3
import tempfile

import pytest

import state as state_module
from discovery.today import build_today, summarize_search
from persistence.migrate import migrate
from persistence.repos.job_user_state_repo import JobUserStateRepo
from persistence.repos.jobs_repo import JobsRepo
from persistence.repos.saved_searches_repo import SavedSearchesRepo

OLD = "2026-03-01T00:00:00+00:00"
NEW = "2099-01-01T00:00:00+00:00"  # after any search's new_since

JOBS = [
    # key, company, title, location, discovered_at
    ("a1", "Stripe", "Machine Learning Engineer", "San Francisco", NEW),
    ("a2", "Stripe", "Machine Learning Engineer", "Seattle", NEW),  # same role, other city
    ("a3", "Gusto", "Staff ML Engineer", "San Francisco", NEW),
    ("a4", "Plaid", "ML Engineer", "San Francisco", OLD),  # open before the search was saved
    ("b1", "Datadog", "Product Manager", "New York", NEW),
    ("b2", "Datadog", "Senior Product Manager", "New York", NEW),
    ("b3", "Notion", "Product Manager", "New York", NEW),
    ("c1", "Asana", "Recruiter", "San Francisco", NEW),  # matches no search
]


@pytest.fixture
def db(monkeypatch):
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".db").name
    migrate(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executemany(
        """
        INSERT INTO jobs (provider, external_id, provider_job_key, company, title,
                          location_raw, url, discovered_at)
        VALUES ('greenhouse', ?, ?, ?, ?, ?, 'https://example.com', ?)
        """,
        [(k, k, c, t, l, d) for k, c, t, l, d in JOBS],
    )
    conn.commit()
    monkeypatch.setattr(state_module, "DB_PATH", path)
    yield conn
    conn.close()


def _keys(today):
    return [i["job_id"] for i in today["items"]]


# ------------------------------------------------------------
# Saved searches
# ------------------------------------------------------------

def test_create_names_search_and_counts_only_roles_after_it(db):
    search = SavedSearchesRepo(db).create(role="ml engineer", location="sf")

    assert search["name"] == "ML engineer · SF"
    summary = summarize_search(JobsRepo(db), search)
    assert summary["open_count"] == 3  # a1/a2 grouped, a3, a4
    assert summary["company_count"] == 3


def test_include_existing_counts_open_roles_as_new(db):
    repo = SavedSearchesRepo(db)
    from_now = repo.create(role="ml engineer", location="sf", name="new only")
    everything = repo.create(role="ml engineer", location="sf", include_existing=True)

    jobs = JobsRepo(db)
    assert summarize_search(jobs, from_now)["new_count"] == 2  # a1/a2, a3 (NEW is in the future)
    assert summarize_search(jobs, everything)["new_count"] == 3  # plus a4


def test_empty_search_is_rejected(db):
    with pytest.raises(ValueError):
        SavedSearchesRepo(db).create(role="  ", location="")


def test_delete(db):
    repo = SavedSearchesRepo(db)
    s = repo.create(company="Stripe")
    assert repo.delete(s["id"]) is True
    assert repo.delete(s["id"]) is False
    assert repo.list() == []


# ------------------------------------------------------------
# Today queue
# ------------------------------------------------------------

def test_same_role_in_two_cities_is_one_item(db):
    s = SavedSearchesRepo(db).create(role="ml engineer", location="")
    today = build_today(JobsRepo(db), [s])

    stripe = next(i for i in today["items"] if i["company"] == "Stripe")
    assert sorted(stripe["job_ids"]) == ["a1", "a2"]
    assert stripe["locations"] == ["San Francisco", "Seattle"] or stripe["locations"] == ["Seattle", "San Francisco"]


def test_searches_take_turns(db):
    repo = SavedSearchesRepo(db)
    pm = repo.create(role="product manager", location="new york")
    ml = repo.create(role="ml engineer", location="sf")

    today = build_today(JobsRepo(db), [pm, ml], limit=4)
    sources = [i["source"]["name"] for i in today["items"]]

    assert sources[:2] == [pm["name"], ml["name"]]
    assert today["new_shown"] == 4
    assert today["new_total"] == 5


def test_role_matching_two_searches_appears_once(db):
    repo = SavedSearchesRepo(db)
    a = repo.create(company="Stripe")
    b = repo.create(role="machine learning")
    today = build_today(JobsRepo(db), [a, b])
    assert [i["company"] for i in today["items"]].count("Stripe") == 1


def test_decided_roles_leave_today_and_later_returns_at_the_end(db):
    s = SavedSearchesRepo(db).create(role="product manager", location="new york")
    states = JobUserStateRepo(db)

    first = build_today(JobsRepo(db), [s])
    assert len(first["items"]) == 3

    states.set_state("b1", "saved")
    states.set_state("b2", "ignored")
    states.set_state("b3", "later")
    db.commit()

    second = build_today(JobsRepo(db), [s])
    assert _keys(second) == ["b3"]
    assert second["items"][0]["source"]["type"] == "later"
    assert second["new_shown"] == 0
    assert second["later_count"] == 1


def test_no_searches_means_empty_today(db):
    today = build_today(JobsRepo(db), [])
    assert today["items"] == [] and today["new_total"] == 0


def test_limit_caps_new_items(db):
    s = SavedSearchesRepo(db).create(role="engineer", include_existing=True)
    today = build_today(JobsRepo(db), [s], limit=1)
    assert today["new_shown"] == 1
    assert today["new_total"] == 3


# ------------------------------------------------------------
# Migration and API
# ------------------------------------------------------------

def test_migration_keeps_existing_states_and_allows_later(db):
    states = JobUserStateRepo(db)
    states.set_state("c1", "applied")
    states.set_state("a4", "later")
    db.commit()
    rows = dict(db.execute("SELECT job_id, state FROM job_user_state").fetchall())
    assert rows == {"c1": "applied", "a4": "later"}


async def test_api_decide_applies_to_every_posting_of_a_role(db):
    import bridge_server
    s = SavedSearchesRepo(db).create(role="ml engineer", location="")

    await bridge_server.today_decide(bridge_server.TodayDecisionPayload(job_ids=["a1", "a2"], decision="saved"))

    states = dict(db.execute("SELECT job_id, state FROM job_user_state").fetchall())
    assert states == {"a1": "saved", "a2": "saved"}
    today = await bridge_server.today(limit=15)
    assert all(i["company"] != "Stripe" for i in today["items"])


async def test_api_rejects_unknown_decision(db):
    import bridge_server
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc:
        await bridge_server.today_decide(bridge_server.TodayDecisionPayload(job_ids=["a1"], decision="applied"))
    assert exc.value.status_code == 400


async def test_api_saved_search_round_trip(db):
    import bridge_server
    created = await bridge_server.create_saved_search(
        bridge_server.SavedSearchPayload(role="product manager", location="new york", include_existing=True)
    )
    listed = await bridge_server.list_saved_searches()
    assert listed["searches"][0]["id"] == created["search"]["id"]
    assert listed["searches"][0]["new_count"] == 3
    await bridge_server.delete_saved_search(created["search"]["id"])
    assert (await bridge_server.list_saved_searches())["searches"] == []
