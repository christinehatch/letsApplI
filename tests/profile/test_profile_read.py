"""Milestone 6.2: "Read it" proposes quoted facts; only confirmed ones count."""

import sqlite3

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import state as state_module
import user_profile.api as profile_api
from persistence.migrate import migrate
from user_profile.facts import FactReadError, propose_facts, validate_facts
from user_profile.website import WebsiteReadError, fetch_page_text, html_to_text

RESUME = """Jordan Lee
Senior Data Engineer, Acme Health (2022-2025)
Built Python ETL pipelines in dbt and Airflow for claims data.
B.S. Computer Science, State University. GPA 3.9/4.0
San Francisco, CA"""


def fact(kind, text, quote):
    return {"kind": kind, "text": text, "quote": quote}


# ------------------------------------------------------------
# Validator
# ------------------------------------------------------------

def test_keeps_facts_whose_quote_is_in_the_source():
    kept, dropped = validate_facts(
        {"facts": [
            fact("title", "Senior Data Engineer, Acme Health", "Senior Data Engineer, Acme Health (2022-2025)"),
            fact("skill", "dbt", "Python ETL pipelines in dbt and Airflow"),
            fact("location", "San Francisco", "San Francisco, CA"),
        ]},
        RESUME,
    )
    assert [f["text"] for f in kept] == ["Senior Data Engineer, Acme Health", "dbt", "San Francisco"]
    assert dropped == []


def test_quote_matching_ignores_case_and_line_breaks():
    kept, _ = validate_facts(
        {"facts": [fact("achievement", "Built ETL for claims data", "built python   ETL pipelines in dbt and airflow for claims data.")]},
        RESUME,
    )
    assert len(kept) == 1


@pytest.mark.parametrize(
    "item,reason",
    [
        (fact("skill", "Rust", "Wrote Rust services"), "quote not in source"),
        (fact("hobby", "Climbing", "Jordan Lee"), "unknown kind"),
        (fact("skill", "", "dbt"), "missing"),
        (fact("skill", "dbt", ""), "missing"),
        (fact("title", "Expert data engineer", "Senior Data Engineer"), "evaluative"),
        (fact("skill", "Strong Python", "Python ETL"), "evaluative"),
        (fact("title", "Good fit for staff roles", "Senior Data Engineer"), "fit language"),
        (fact("education", "B.S. Computer Science, GPA 3.9", "GPA 3.9/4.0"), "grades"),
        ("not a dict", "not an object"),
    ],
)
def test_drops_bad_facts_with_a_reason(item, reason):
    kept, dropped = validate_facts({"facts": [item]}, RESUME)
    assert kept == []
    assert reason in dropped[0]


def test_evaluative_word_is_fine_when_the_source_says_it():
    kept, _ = validate_facts(
        {"facts": [fact("achievement", "Strong record of on-time delivery", "strong record of on-time delivery")]},
        "Known for a strong record of on-time delivery.",
    )
    assert len(kept) == 1


def test_education_without_grades_is_kept():
    kept, _ = validate_facts(
        {"facts": [fact("education", "B.S. Computer Science, State University", "B.S. Computer Science, State University")]},
        RESUME,
    )
    assert len(kept) == 1


def test_duplicates_collapse():
    kept, _ = validate_facts(
        {"facts": [fact("skill", "dbt", "dbt"), fact("skill", "DBT", "dbt")]}, RESUME
    )
    assert len(kept) == 1


@pytest.mark.parametrize("raw", [None, [], {"facts": "x"}, {"other": []}])
def test_wrong_shape_is_an_error(raw):
    with pytest.raises(FactReadError):
        validate_facts(raw, RESUME)


def test_propose_retries_once_on_bad_shape_then_succeeds():
    calls = []

    def generate(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return {"nope": True}
        return {"facts": [fact("skill", "Airflow", "dbt and Airflow")]}

    kept, _ = propose_facts(RESUME, "resume", generate)
    assert [f["text"] for f in kept] == ["Airflow"]
    assert len(calls) == 2
    assert calls[0]["temperature"] == 0.0
    assert "a resume" in calls[0]["user_prompt"]
    assert RESUME in calls[0]["user_prompt"]


def test_propose_explains_a_missing_api_key():
    def generate(**kwargs):
        raise RuntimeError("OPENAI_API_KEY not set")

    with pytest.raises(FactReadError, match="OPENAI_API_KEY"):
        propose_facts(RESUME, "resume", generate)


def test_prompt_forbids_grades_and_judging():
    from user_profile.facts import system_prompt

    prompt = system_prompt().lower()
    assert "never include grades" in prompt
    assert "do not describe the person" in prompt
    assert "copied exactly" in prompt


# ------------------------------------------------------------
# Website
# ------------------------------------------------------------

def test_html_to_text_drops_scripts_and_styles():
    html = "<html><style>.x{}</style><script>alert(1)</script><h1>Jordan</h1><p>I build  data tools.</p></html>"
    assert html_to_text(html) == "Jordan\nI build data tools."


@pytest.mark.parametrize("url", ["http://localhost/", "http://127.0.0.1:8000/", "http://10.0.0.5/", "http://192.168.1.1/", "file:///etc/passwd"])
def test_website_reader_refuses_local_addresses(url):
    with pytest.raises(WebsiteReadError):
        fetch_page_text(url)


# ------------------------------------------------------------
# API
# ------------------------------------------------------------

@pytest.fixture
def client(tmp_path, monkeypatch):
    db = tmp_path / "test.sqlite3"
    migrate(str(db))
    monkeypatch.setattr(state_module, "DB_PATH", str(db))
    app = FastAPI()
    app.include_router(profile_api.router)
    c = TestClient(app)
    c.db = db
    c.calls = []

    def fake_generate(**kwargs):
        c.calls.append(kwargs)
        return {"facts": [
            fact("title", "Senior Data Engineer, Acme Health", "Senior Data Engineer, Acme Health"),
            fact("skill", "dbt", "dbt"),
            fact("skill", "Kubernetes", "Kubernetes"),  # not in the resume: dropped
        ]}

    monkeypatch.setattr(profile_api, "_generate", lambda: fake_generate)
    return c


def add_resume(client):
    res = client.post(
        "/api/profile/sources/upload",
        params={"kind": "resume", "filename": "resume.txt"},
        content=RESUME.encode(),
    )
    return res.json()["source"]["id"]


def test_read_needs_consent_and_sends_nothing_without_it(client):
    sid = add_resume(client)
    res = client.post(f"/api/profile/sources/{sid}/read", json={})
    assert res.status_code == 400
    assert "AI service" in res.json()["detail"]
    assert client.calls == []


def test_read_proposes_facts_and_drops_invented_ones(client):
    sid = add_resume(client)
    res = client.post(f"/api/profile/sources/{sid}/read", json={"consent": True})
    assert res.status_code == 200
    body = res.json()
    assert body["proposed"] == 2
    assert body["dropped"] == 1
    assert {f["text"] for f in body["facts"]} == {"Senior Data Engineer, Acme Health", "dbt"}
    assert all(f["status"] == "proposed" for f in body["facts"])
    assert body["source"]["read_at"]


def test_keep_edit_reject_and_confirm_all(client):
    sid = add_resume(client)
    facts = client.post(f"/api/profile/sources/{sid}/read", json={"consent": True}).json()["facts"]
    title = next(f for f in facts if f["kind"] == "title")
    skill = next(f for f in facts if f["kind"] == "skill")

    edited = client.patch(f"/api/profile/facts/{title['id']}", json={"text": "Senior Data Engineer", "status": "confirmed"})
    assert edited.json()["fact"]["text"] == "Senior Data Engineer"
    assert edited.json()["fact"]["quote"] == "Senior Data Engineer, Acme Health"  # evidence kept

    client.patch(f"/api/profile/facts/{skill['id']}", json={"status": "rejected"})
    profile = client.get("/api/profile").json()
    assert [(f["text"], f["status"]) for f in profile["facts"]] == [("Senior Data Engineer", "confirmed")]


def test_reading_again_keeps_decisions_and_does_not_repropose_them(client):
    sid = add_resume(client)
    facts = client.post(f"/api/profile/sources/{sid}/read", json={"consent": True}).json()["facts"]
    skill = next(f for f in facts if f["kind"] == "skill")
    client.patch(f"/api/profile/facts/{skill['id']}", json={"status": "rejected"})
    client.post(f"/api/profile/sources/{sid}/confirm-all")

    again = client.post(f"/api/profile/sources/{sid}/read", json={"consent": True}).json()
    assert again["proposed"] == 0
    assert [(f["text"], f["status"]) for f in again["facts"]] == [("Senior Data Engineer, Acme Health", "confirmed")]


def test_typed_skills_cannot_be_patched_as_source_facts(client):
    client.put("/api/profile/skills", json={"skills": ["SQL"]})
    conn = sqlite3.connect(client.db)
    typed_id = conn.execute("SELECT id FROM profile_facts WHERE source_id IS NULL").fetchone()[0]
    conn.close()
    assert client.patch(f"/api/profile/facts/{typed_id}", json={"status": "rejected"}).status_code == 404


def test_missing_key_gives_a_clear_message(client, monkeypatch):
    def no_key():
        raise RuntimeError("OPENAI_API_KEY not set")

    monkeypatch.setattr(profile_api, "_generate", no_key)
    sid = add_resume(client)
    res = client.post(f"/api/profile/sources/{sid}/read", json={"consent": True})
    assert res.status_code == 503
    assert "OPENAI_API_KEY" in res.json()["detail"]


def test_website_read_fetches_then_proposes(client, monkeypatch):
    page = "Jordan Lee. Senior Data Engineer, Acme Health. I write about dbt. " * 5
    monkeypatch.setattr(profile_api, "fetch_page_text", lambda url: page)
    sid = client.post("/api/profile/sources/website", json={"url": "jordan.dev"}).json()["source"]["id"]
    body = client.post(f"/api/profile/sources/{sid}/read", json={"consent": True}).json()
    assert body["source"]["text_chars"] == len(page)
    assert {f["text"] for f in body["facts"]} == {"Senior Data Engineer, Acme Health", "dbt"}


def test_deleting_a_source_deletes_its_facts(client):
    sid = add_resume(client)
    client.post(f"/api/profile/sources/{sid}/read", json={"consent": True})
    client.post(f"/api/profile/sources/{sid}/confirm-all")
    client.delete(f"/api/profile/sources/{sid}")
    assert client.get("/api/profile").json()["facts"] == []
