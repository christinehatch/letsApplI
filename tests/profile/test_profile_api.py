"""Milestone 6.1: profile sources, typed skills and preferences (local only, no AI)."""

import io
import sqlite3
import zipfile
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import state as state_module
from persistence.migrate import migrate
from user_profile.api import router
from user_profile.extract import ExtractionError, extract_text


# ------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------

def make_pdf(text: str) -> bytes:
    import pymupdf

    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def make_docx(paragraphs: list[str]) -> bytes:
    ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    body = "".join(f"<w:p><w:r><w:t>{p}</w:t></w:r></w:p>" for p in paragraphs)
    xml = f'<?xml version="1.0"?><w:document xmlns:w="{ns}"><w:body>{body}</w:body></w:document>'
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("word/document.xml", xml)
    return buf.getvalue()


@pytest.fixture
def client(tmp_path, monkeypatch):
    db = tmp_path / "test.sqlite3"
    migrate(str(db))
    monkeypatch.setattr(state_module, "DB_PATH", str(db))
    app = FastAPI()
    app.include_router(router)
    c = TestClient(app)
    c.db = db
    c.files_dir = tmp_path / "profile"
    return c


def upload(client, kind, filename, data):
    return client.post(
        "/api/profile/sources/upload",
        params={"kind": kind, "filename": filename},
        content=data,
        headers={"Content-Type": "application/octet-stream"},
    )


# ------------------------------------------------------------
# Text extraction
# ------------------------------------------------------------

def test_pdf_text_is_read_locally():
    kind, text = extract_text("resume.pdf", make_pdf("Senior Data Engineer at Acme"))
    assert kind == "pdf"
    assert "Senior Data Engineer at Acme" in text


def test_docx_text_keeps_paragraphs():
    kind, text = extract_text("resume.docx", make_docx(["Jane Doe", "Python, dbt, Airflow"]))
    assert kind == "docx"
    assert text == "Jane Doe\nPython, dbt, Airflow"


def test_plain_text_is_accepted():
    assert extract_text("notes.txt", b"  Skills:  Python \r\n\r\n\r\n\r\nSQL ") == ("txt", "Skills: Python\n\nSQL")


@pytest.mark.parametrize(
    "filename,data,message",
    [
        ("resume.pdf", b"", "empty"),
        ("photo.png", b"\x89PNG....", "PDF, a Word"),
        ("resume.pdf", b"%PDF-1.4 garbage", "couldn't be opened"),
        ("resume.docx", b"PK\x03\x04 not a zip", "couldn't be opened"),
        ("resume.pdf", b"%PDF" + b"x" * (10 * 1024 * 1024), "over 10 MB"),
    ],
)
def test_unreadable_files_get_a_plain_message(filename, data, message):
    with pytest.raises(ExtractionError, match=message):
        extract_text(filename, data)


def test_pdf_with_no_text_says_it_may_be_scanned():
    import pymupdf

    doc = pymupdf.open()
    doc.new_page()
    data = doc.tobytes()
    with pytest.raises(ExtractionError, match="scanned"):
        extract_text("scan.pdf", data)


# ------------------------------------------------------------
# Sources
# ------------------------------------------------------------

def test_upload_stores_file_and_text_and_shows_what_was_read(client):
    res = upload(client, "resume", "Jane Resume.pdf", make_pdf("Staff ML Engineer, Python"))
    assert res.status_code == 200
    source = res.json()["source"]
    assert source["kind"] == "resume"
    assert source["label"] == "Jane Resume.pdf"
    assert "Staff ML Engineer" in source["text_preview"]
    assert "file_path" not in source  # internal path never leaves the server
    assert len(list(client.files_dir.iterdir())) == 1

    full = client.get(f"/api/profile/sources/{source['id']}/text").json()["source"]
    assert "Staff ML Engineer, Python" in full["text"]

    profile = client.get("/api/profile").json()
    assert [s["id"] for s in profile["sources"]] == [source["id"]]


def test_upload_rejects_unknown_kind_and_bad_files(client):
    assert upload(client, "selfie", "a.pdf", make_pdf("x")).status_code == 400
    bad = upload(client, "resume", "a.png", b"\x89PNG")
    assert bad.status_code == 400
    assert "PDF" in bad.json()["detail"]
    assert not client.files_dir.exists() or not any(client.files_dir.iterdir())


def test_delete_removes_file_text_and_facts(client):
    source = upload(client, "transcript", "t.pdf", make_pdf("BS Computer Science")).json()["source"]
    conn = sqlite3.connect(client.db)
    conn.execute(
        "INSERT INTO profile_facts (source_id, kind, text, status, created_at, updated_at) "
        "VALUES (?, 'education', 'BS Computer Science', 'confirmed', 'now', 'now')",
        (source["id"],),
    )
    conn.commit()
    conn.close()

    assert client.delete(f"/api/profile/sources/{source['id']}").status_code == 200
    assert not any(client.files_dir.iterdir())
    conn = sqlite3.connect(client.db)
    assert conn.execute("SELECT COUNT(*) FROM profile_sources").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM profile_facts").fetchone()[0] == 0
    conn.close()
    assert client.delete(f"/api/profile/sources/{source['id']}").status_code == 404


def test_website_link_is_stored_but_not_fetched(client, monkeypatch):
    def no_network(*a, **k):
        raise AssertionError("6.1 must not fetch anything")

    monkeypatch.setattr("urllib.request.urlopen", no_network)
    res = client.post("/api/profile/sources/website", json={"url": "janedoe.dev"})
    assert res.status_code == 200
    source = res.json()["source"]
    assert source["url"] == "https://janedoe.dev"
    assert source["label"] == "janedoe.dev"
    assert source["text_chars"] == 0


@pytest.mark.parametrize("url", ["", "not a url", "ftp://x.com", "javascript:alert(1)"])
def test_website_rejects_non_web_addresses(client, url):
    assert client.post("/api/profile/sources/website", json={"url": url}).status_code == 400


@pytest.mark.parametrize("url", ["linkedin.com/in/jane", "https://www.linkedin.com/in/jane"])
def test_linkedin_links_point_to_save_to_pdf(client, url):
    res = client.post("/api/profile/sources/website", json={"url": url})
    assert res.status_code == 400
    assert "Save to PDF" in res.json()["detail"]


# ------------------------------------------------------------
# Skills and preferences
# ------------------------------------------------------------

def test_skills_are_cleaned_deduped_and_replaced(client):
    res = client.put("/api/profile/skills", json={"skills": [" Python ", "python", "", "dbt", "Kubernetes"]})
    assert res.json()["skills"] == ["Python", "dbt", "Kubernetes"]
    client.put("/api/profile/skills", json={"skills": ["SQL"]})
    assert client.get("/api/profile").json()["skills"] == ["SQL"]


def test_preferences_round_trip(client):
    prefs = {
        "location": ["San Francisco", "Remote"],
        "work_mode": ["Remote", "hybrid"],
        "level": ["senior", "staff"],
        "company_size": ["startup"],
        "industry_in": ["Health tech"],
        "industry_out": ["Gambling"],
    }
    res = client.put("/api/profile/preferences", json=prefs)
    assert res.status_code == 200
    saved = client.get("/api/profile").json()["preferences"]
    assert saved["work_mode"] == ["remote", "hybrid"]
    assert saved["location"] == ["San Francisco", "Remote"]
    assert saved["industry_out"] == ["Gambling"]


def test_preferences_reject_unknown_choices(client):
    res = client.put("/api/profile/preferences", json={"level": ["wizard"]})
    assert res.status_code == 400
    assert "wizard" in res.json()["detail"]


def test_upload_and_storage_never_call_ai_or_the_network():
    # AI and fetching live only behind "Read it" (facts.py, website.py, and the
    # /read endpoint). Uploading, storing and showing text must stay local.
    root = Path(__file__).resolve().parents[2] / "src"
    for path in (root / "user_profile" / "extract.py", root / "persistence" / "repos" / "profile_repo.py"):
        text = path.read_text()
        for banned in ("openai", "anthropic", "LLMAdapter", "urlopen", "httpx", "requests", "urllib"):
            assert banned not in text, f"{banned} in {path.name}"
