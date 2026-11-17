"""
Profile API (Milestone 6). Mounted by bridge_server.py.

Uploads are stored under state/profile/ and their text is read on this
machine. The only step that leaves the machine is POST .../read, which the
user triggers per source after agreeing that the text goes to the AI service
(and, for a website, fetches that one page).
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from persistence.db import get_connection
from persistence.repos.profile_repo import ProfileRepo
from user_profile.extract import MAX_UPLOAD_BYTES, ExtractionError, extract_text
from user_profile.facts import FactReadError, propose_facts
from user_profile.website import WebsiteReadError, read_site

router = APIRouter(prefix="/api/profile", tags=["profile"])

UPLOAD_KINDS = ("resume", "linkedin", "transcript", "website")


def _db_path() -> str:
    from state import DB_PATH  # resolved per call so tests can point DB_PATH elsewhere

    return DB_PATH


def _files_dir() -> Path:
    path = Path(_db_path()).parent / "profile"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _public(source: dict) -> dict:
    return {k: v for k, v in source.items() if k != "file_path"}


def _remove_file(file_path: Optional[str]) -> None:
    if not file_path:
        return
    path = Path(file_path)
    # Only ever delete inside our own folder.
    if path.resolve().parent == _files_dir().resolve():
        path.unlink(missing_ok=True)


@router.get("")
async def get_profile():
    conn = get_connection(_db_path())
    try:
        repo = ProfileRepo(conn)
        return {
            "sources": [_public(s) for s in repo.list_sources()],
            "facts": repo.list_source_facts(),
            "skills": repo.list_skills(),
            "preferences": repo.get_preferences(),
        }
    finally:
        conn.close()


@router.post("/sources/upload")
async def upload_source(
    request: Request,
    kind: str = Query(..., description="resume | linkedin | transcript"),
    filename: str = Query(..., max_length=200),
):
    """The file is the raw request body (no multipart), read locally for text."""
    if kind not in UPLOAD_KINDS:
        raise HTTPException(status_code=400, detail="Upload a resume, LinkedIn PDF, transcript, or a PDF of your website.")

    data = await request.body()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="That file is over 10 MB. Upload a smaller copy.")
    try:
        file_type, text = extract_text(filename, data)
    except ExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    stored = _files_dir() / f"{uuid.uuid4().hex}.{file_type}"
    stored.write_bytes(data)

    conn = get_connection(_db_path())
    try:
        source = ProfileRepo(conn).add_source(
            kind=kind,
            label=Path(filename).name,
            file_path=str(stored),
            extracted_text=text,
        )
    except Exception:
        stored.unlink(missing_ok=True)
        raise
    finally:
        conn.close()
    return {"source": _public(source)}


def _clean_url(raw: str) -> tuple[str, str]:
    """Return (url, host) for a plain web address, or raise a 400."""
    url = raw.strip()
    if url and "://" not in url:
        url = f"https://{url}"
    parsed = urlparse(url)
    try:
        host = (parsed.hostname or "").lower()
        parsed.port  # raises on a malformed port, e.g. "javascript:alert(1)"
    except ValueError:
        host = ""
    looks_like_host = "." in host and all(part for part in host.split("."))
    if parsed.scheme not in ("http", "https") or not looks_like_host or " " in url or len(url) > 500:
        raise HTTPException(status_code=400, detail="Enter a website address, like yourname.com.")
    return url, host


def _is_linkedin(host: str) -> bool:
    return host == "linkedin.com" or host.endswith(".linkedin.com")


class WebsitePayload(BaseModel):
    url: str
    label: Optional[str] = None


@router.post("/sources/website")
async def add_website(payload: WebsitePayload):
    """Stores the link only. The page is read in 6.2, when the user presses Read it."""
    url, host = _clean_url(payload.url)
    if _is_linkedin(host):
        raise HTTPException(
            status_code=400,
            detail="That's a LinkedIn address. Add it in the LinkedIn section instead.",
        )

    conn = get_connection(_db_path())
    try:
        source = ProfileRepo(conn).add_source(
            kind="website", label=(payload.label or host.removeprefix("www.")), url=url
        )
    finally:
        conn.close()
    return {"source": _public(source)}


class LinkPayload(BaseModel):
    url: str


@router.post("/sources/linkedin-link")
async def save_linkedin_link(payload: LinkPayload):
    """
    Save the user's LinkedIn profile address. It is kept as a link only and is
    never fetched: LinkedIn blocks automated reading. Saving again replaces it.
    """
    url, host = _clean_url(payload.url)
    if not _is_linkedin(host):
        raise HTTPException(status_code=400, detail="Enter your LinkedIn profile address, like linkedin.com/in/yourname.")

    conn = get_connection(_db_path())
    try:
        repo = ProfileRepo(conn)
        for old in repo.list_sources():
            if old["kind"] == "linkedin" and old["url"] and not old["has_file"]:
                repo.delete_source(old["id"])
        source = repo.add_source(kind="linkedin", label="LinkedIn profile", url=url)
    finally:
        conn.close()
    return {"source": _public(source)}


@router.get("/sources/{source_id}/text")
async def source_text(source_id: int):
    """Exactly what was read from the source, so the user can check it."""
    conn = get_connection(_db_path())
    try:
        source = ProfileRepo(conn).get_source(source_id, with_text=True)
    finally:
        conn.close()
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found.")
    return {"source": _public(source)}


@router.delete("/sources/{source_id}")
async def delete_source(source_id: int):
    """Deletes the stored file, its text, and every fact that came from it."""
    conn = get_connection(_db_path())
    try:
        source = ProfileRepo(conn).delete_source(source_id)
    finally:
        conn.close()
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found.")
    _remove_file(source.get("file_path"))
    return {"deleted": source_id}


class SkillsPayload(BaseModel):
    skills: list[str]


@router.put("/skills")
async def put_skills(payload: SkillsPayload):
    conn = get_connection(_db_path())
    try:
        return {"skills": ProfileRepo(conn).set_skills(payload.skills)}
    finally:
        conn.close()


class PreferencesPayload(BaseModel):
    location: list[str] = []
    work_mode: list[str] = []
    level: list[str] = []
    company_size: list[str] = []
    industry_in: list[str] = []
    industry_out: list[str] = []


@router.put("/preferences")
async def put_preferences(payload: PreferencesPayload):
    conn = get_connection(_db_path())
    try:
        try:
            prefs = ProfileRepo(conn).set_preferences(payload.model_dump())
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return {"preferences": prefs}
    finally:
        conn.close()


# ------------------------------------------------------------
# 6.2 — Read it: propose facts from one source, then the user reviews them
# ------------------------------------------------------------

def _generate():
    """The model call. Tests replace this so they never touch the network."""
    from llm.adapter import LLMAdapter

    return LLMAdapter().generate_structured


class ReadPayload(BaseModel):
    consent: bool = False


@router.post("/sources/{source_id}/read")
async def read_source(source_id: int, payload: ReadPayload):
    if not payload.consent:
        raise HTTPException(
            status_code=400,
            detail="Reading sends this source's text to the AI service. Agree to that first.",
        )

    conn = get_connection(_db_path())
    try:
        repo = ProfileRepo(conn)
        source = repo.get_source(source_id, with_text=True)
        if source is None:
            raise HTTPException(status_code=404, detail="Source not found.")

        if source["kind"] == "linkedin" and not source["has_file"]:
            raise HTTPException(
                status_code=400,
                detail="LinkedIn links can't be read. Upload LinkedIn's “Save to PDF” file to add its details.",
            )

        text = source["text"]
        pages_read: list[str] = []
        if source["kind"] == "website" and source["url"]:
            try:
                text, pages_read = await run_in_threadpool(read_site, source["url"])
            except WebsiteReadError as e:
                raise HTTPException(status_code=400, detail=str(e))
            repo.set_source_text(source_id, text)

        try:
            generate = _generate()
        except Exception:
            raise HTTPException(
                status_code=503,
                detail="Reading needs an OpenAI API key. Set OPENAI_API_KEY and restart the API server.",
            )
        try:
            facts, dropped = await run_in_threadpool(propose_facts, text, source["kind"], generate)
        except FactReadError as e:
            raise HTTPException(status_code=502, detail=str(e))

        added = repo.replace_proposals(source_id, facts)
        return {
            "source": _public(repo.get_source(source_id)),
            "facts": [f for f in repo.list_source_facts() if f["source_id"] == source_id],
            "proposed": added,
            "dropped": len(dropped),
            "pages_read": pages_read,
        }
    finally:
        conn.close()


class FactPatch(BaseModel):
    status: Optional[str] = None
    text: Optional[str] = None


@router.patch("/facts/{fact_id}")
async def patch_fact(fact_id: int, payload: FactPatch):
    """Keep, edit, or reject one proposed fact."""
    conn = get_connection(_db_path())
    try:
        try:
            fact = ProfileRepo(conn).update_fact(fact_id, status=payload.status, text=payload.text)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        if fact is None:
            raise HTTPException(status_code=404, detail="Fact not found.")
        return {"fact": fact}
    finally:
        conn.close()


@router.post("/sources/{source_id}/confirm-all")
async def confirm_all(source_id: int):
    conn = get_connection(_db_path())
    try:
        repo = ProfileRepo(conn)
        if repo.get_source(source_id) is None:
            raise HTTPException(status_code=404, detail="Source not found.")
        confirmed = repo.confirm_all(source_id)
        return {
            "confirmed": confirmed,
            "facts": [f for f in repo.list_source_facts() if f["source_id"] == source_id],
        }
    finally:
        conn.close()


# ------------------------------------------------------------
# 6.3 — Suggested searches from the profile (deterministic, no AI)
# ------------------------------------------------------------

@router.get("/suggested-searches")
async def suggested_searches():
    from discovery.today import count_visible
    from persistence.repos.jobs_repo import JobsRepo
    from persistence.repos.saved_searches_repo import SavedSearchesRepo
    from user_profile.match import is_empty, load_profile, suggest_searches

    conn = get_connection(_db_path())
    try:
        jobs = JobsRepo(conn)
        profile = load_profile(conn)
        filters = None if is_empty(profile) else profile

        def count_open(search: dict) -> int:
            # Counted the way Today shows them: levels and industries you ruled out aren't counted.
            return count_visible(jobs, search, filters)

        suggestions = suggest_searches(profile, count_open, SavedSearchesRepo(conn).list())
        return {
            "suggestions": suggestions,
            "has_roles": bool(profile["titles"]),
            "has_locations": bool(profile["locations"] or profile["location_facts"] or "remote" in profile["work_mode"]),
            "levels": profile["levels"],
        }
    finally:
        conn.close()
