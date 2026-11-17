"""
Profile API (Milestone 6.1). Mounted by bridge_server.py.

Everything here is local: uploads are stored under state/profile/ and read
on this machine. Nothing in this module calls an AI service or fetches a URL.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from persistence.db import get_connection
from persistence.repos.profile_repo import ProfileRepo
from user_profile.extract import MAX_UPLOAD_BYTES, ExtractionError, extract_text

router = APIRouter(prefix="/api/profile", tags=["profile"])

UPLOAD_KINDS = ("resume", "linkedin", "transcript")


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
        raise HTTPException(status_code=400, detail="Upload a resume, LinkedIn PDF, or transcript.")

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


class WebsitePayload(BaseModel):
    url: str
    label: Optional[str] = None


@router.post("/sources/website")
async def add_website(payload: WebsitePayload):
    """Stores the link only. The page is read in 6.2, when the user presses Read it."""
    url = payload.url.strip()
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
    if parsed.netloc.lower().removeprefix("www.").endswith("linkedin.com"):
        raise HTTPException(
            status_code=400,
            detail="LinkedIn pages can't be read. Use “Save to PDF” on your LinkedIn profile and upload that instead.",
        )

    conn = get_connection(_db_path())
    try:
        source = ProfileRepo(conn).add_source(
            kind="website", label=(payload.label or parsed.netloc), url=url
        )
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
