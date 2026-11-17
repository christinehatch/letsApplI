"""Milestone 6.3: recommendations from the profile are deterministic and explain themselves."""

import json
import sqlite3

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import state as state_module
import user_profile.api as profile_api
from discovery.search_query import role_term_patterns
from discovery.today import build_today, count_visible
from persistence.migrate import migrate
from persistence.repos.jobs_repo import JobsRepo
from user_profile import match

# ------------------------------------------------------------
# Title helpers
# ------------------------------------------------------------


@pytest.mark.parametrize(
    "title,core",
    [
        ("Senior Data Engineer at Acme Health (2022-2025)", "Data Engineer"),
        ("Software Developer", "Software Developer"),
        ("Swim Instructor at Menlo Swim & Sport (2018 - Present)", "Swim Instructor"),
        ("Data Analyst, Brightpath Payments", "Data Analyst"),
        ("Software Engineer II", "Software Engineer"),
        ("Jr. Product Designer - Figma", "Product Designer"),
    ],
)
def test_core_title(title, core):
    assert match.core_title(title) == core


@pytest.mark.parametrize(
    "title,level",
    [
        ("Senior Software Engineer", "senior"),
        ("Staff ML Engineer", "staff"),
        ("Principal Engineer", "principal"),
        ("Engineering Manager, Payments", "manager"),
        ("Head of Data", "director"),
        ("Software Engineer Intern (Summer 2027)", "intern"),
        ("Software Engineer - New Grad", "entry"),
        ("Software Engineer I", "entry"),
        ("Software Engineer II", "mid"),
        ("Product Manager", None),  # IC product role: level not stated
        ("Software Engineer, Platform", None),
    ],
)
def test_title_level(title, level):
    assert match.title_level(title) == level


def test_software_developer_finds_software_engineer_titles():
    patterns = role_term_patterns("software developer")
    assert all(__import__("re").search(p, "Software Engineer, Payments", __import__("re").I) for p in patterns)


# ------------------------------------------------------------
# Database fixture
# ------------------------------------------------------------

JOBS = [
    # key, company, title, location, departments
    ("greenhouse:a:1", "Acme", "Software Engineer - New Grad", "San Francisco, CA", ["Engineering"]),
    ("greenhouse:a:2", "Acme", "Senior Software Engineer", "San Francisco, CA", ["Engineering"]),
    ("greenhouse:a:3", "Acme", "Software Engineer, Payments", "San Francisco, CA", ["Engineering"]),
    ("greenhouse:b:1", "BetCo", "Software Engineer", "San Francisco, CA", ["Gambling Products"]),
    ("greenhouse:c:1", "Cloudy", "Software Engineer Intern", "London, UK", ["Engineering"]),
    ("greenhouse:c:2", "Cloudy", "Python Software Engineer", "Remote - US", ["Engineering"]),
    ("greenhouse:d:1", "Dataco", "Data Analyst", "San Francisco, CA", ["Analytics"]),
]


@pytest.fixture
def conn(tmp_path):
    path = tmp_path / "db.sqlite3"
    migrate(str(path))
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    for i, (key, company, title, loc, depts) in enumerate(JOBS):
        c.execute(
            """INSERT INTO jobs (provider, external_id, provider_job_key, company, title, location_raw,
                                 url, discovered_at, first_seen_at, posted_at, raw_provider_payload_json)
               VALUES ('greenhouse', ?, ?, ?, ?, ?, 'https://x', ?, ?, ?, ?)""",
            (key, key, company, title, loc, f"2026-11-{10 + i:02d}T00:00:00+00:00",
             f"2026-11-{10 + i:02d}T00:00:00+00:00", f"2026-11-{10 + i:02d}T00:00:00+00:00",
             json.dumps({"departments": depts})),
        )
    c.execute(
        "INSERT INTO profile_sources (kind, label, file_path, extracted_text, added_at) "
        "VALUES ('resume', 'resume.pdf', '/x/resume.pdf', 'text', 'now')"
    )
    facts = [
        ("title", "Software Developer", "confirmed"),
        ("title", "Swim Instructor at Menlo Swim & Sport", "confirmed"),
        ("title", "Data Analyst at Brightpath", "proposed"),  # not confirmed: ignored
        ("skill", "Python", "confirmed"),
        ("skill", "Rust", "rejected"),
    ]
    for kind, text, status in facts:
        c.execute(
            "INSERT INTO profile_facts (source_id, kind, text, status, created_at, updated_at) VALUES (1, ?, ?, ?, 'now', 'now')",
            (kind, text, status),
        )
    c.commit()
    yield c
    c.close()


def set_prefs(conn, **prefs):
    conn.execute("DELETE FROM profile_preferences")
    for kind, values in prefs.items():
        for v in values:
            conn.execute("INSERT INTO profile_preferences (kind, value, updated_at) VALUES (?, ?, 'now')", (kind, v))
    conn.commit()


def search(role="software developer", location=""):
    return {"id": 1, "name": "Software Developer", "role": role, "location": location, "company": "", "new_since": ""}


# ------------------------------------------------------------
# Profile loading
# ------------------------------------------------------------


def test_profile_uses_only_confirmed_facts(conn):
    p = match.load_profile(conn)
    assert [t for t, _ in p["titles"]] == ["Software Developer", "Swim Instructor at Menlo Swim & Sport"]
    assert p["skills"] == [("Python", "resume")]


# ------------------------------------------------------------
# Suggestions
# ------------------------------------------------------------


def test_suggests_held_roles_that_have_open_matches_only(conn):
    set_prefs(conn, location=["San Francisco"])
    p = match.load_profile(conn)
    jobs = JobsRepo(conn)
    out = match.suggest_searches(p, lambda s: count_visible(jobs, s, p), [])
    assert [(s["name"], s["open_count"]) for s in out] == [("Software Developer · San Francisco", 4)]
    assert out[0]["why"] == ["Software Developer (your resume)", "San Francisco (your preferences)"]


def test_remote_preference_adds_a_remote_suggestion(conn):
    set_prefs(conn, location=["San Francisco"], work_mode=["remote"])
    p = match.load_profile(conn)
    jobs = JobsRepo(conn)
    names = [s["name"] for s in match.suggest_searches(p, lambda s: count_visible(jobs, s, p), [])]
    assert names == ["Software Developer · San Francisco", "Software Developer · Remote"]


def test_existing_saved_searches_are_not_suggested_again(conn):
    set_prefs(conn, location=["San Francisco"])
    p = match.load_profile(conn)
    count = lambda s: 5 if s["role"] == "software developer" else 0
    out = match.suggest_searches(p, count, [{"role": "software developer", "location": "san francisco"}])
    assert out == []


def test_suggestion_counts_respect_level_preferences(conn):
    set_prefs(conn, location=["San Francisco"], level=["entry"])
    p = match.load_profile(conn)
    jobs = JobsRepo(conn)
    [s] = match.suggest_searches(p, lambda s: count_visible(jobs, s, p), [])
    assert s["open_count"] == 3  # the Senior role is not counted


# ------------------------------------------------------------
# Today
# ------------------------------------------------------------


def test_today_hides_levels_and_industries_the_user_ruled_out(conn):
    set_prefs(conn, level=["entry", "intern"], industry_out=["gambling"])
    p = match.load_profile(conn)
    result = build_today(JobsRepo(conn), [search()], profile=p)
    titles = {i["title"] for i in result["items"]}
    assert "Senior Software Engineer" not in titles
    assert all(i["company"] != "BetCo" for i in result["items"])
    assert result["hidden"] == {
        "level": {"count": 1, "terms": ["senior"]},
        "industry": {"count": 1, "terms": ["gambling"]},
    }
    assert "Software Engineer, Payments" in titles  # level not stated: kept


def test_today_items_say_why_they_showed_up(conn):
    set_prefs(conn, location=["San Francisco"], level=["entry"])
    p = match.load_profile(conn)
    items = {i["title"]: i["why"] for i in build_today(JobsRepo(conn), [search()], profile=p)["items"]}
    assert items["Software Engineer - New Grad"] == [
        "Software Developer (your resume)",
        "San Francisco (your preferences)",
        "Entry level (your preferences)",
    ]
    assert items["Python Software Engineer"] == ["Software Developer (your resume)", "Python (your resume)"]


def test_today_puts_closer_matches_first_and_spreads_companies(conn):
    set_prefs(conn, location=["San Francisco"], level=["entry", "intern"])
    p = match.load_profile(conn)
    items = build_today(JobsRepo(conn), [search()], profile=p)["items"]
    assert items[0]["title"] == "Software Engineer - New Grad"  # three reasons
    companies = [i["company"] for i in items]
    assert all(a != b for a, b in zip(companies, companies[1:]) if companies.count(a) < len(companies))


def test_today_without_profile_is_unchanged(conn):
    result = build_today(JobsRepo(conn), [search()])
    assert result["hidden"] == {}
    assert all(i["why"] == [] for i in result["items"])
    assert all("_payload" not in i for i in result["items"])


# ------------------------------------------------------------
# API
# ------------------------------------------------------------


def test_suggested_searches_endpoint(conn, tmp_path, monkeypatch):
    set_prefs(conn, location=["San Francisco"])
    db = conn.execute("PRAGMA database_list").fetchone()["file"]
    monkeypatch.setattr(state_module, "DB_PATH", db)
    app = FastAPI()
    app.include_router(profile_api.router)
    body = TestClient(app).get("/api/profile/suggested-searches").json()
    assert body["has_roles"] is True
    assert body["has_locations"] is True
    assert [s["name"] for s in body["suggestions"]] == ["Software Developer · San Francisco"]


def test_matching_never_calls_ai():
    from pathlib import Path

    text = (Path(match.__file__)).read_text()
    for banned in ("openai", "LLMAdapter", "urllib", "generate"):
        assert banned not in text
