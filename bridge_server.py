import sys
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from fastapi.responses import Response
from urllib.parse import urlparse
from src.phase5.phase5_2.validator_schema import validate_schema

from src.phase5.phase5_2.determinism import compute_structural_hash
from phase5.phase5_2.interpreter import Phase52Interpreter
from phase5.phase5_2.types import InterpretationInput
from phase5.phase5_2.errors import (
    InterpretationNotAuthorizedError,
    InvalidInputSourceError,
)
from discovery.summary import summarize_since
from discovery.run_state import load_last_run

# Adds the project root to the Python path so 'src' is discoverable
sys.path.append(os.path.join(os.getcwd(), "src"))

from ui.read_job import read_job_for_ui, get_fetcher
from phase5.phase5_1.types import ConsentPayload

import time
from playwright.async_api import async_playwright, Browser, Playwright
from typing import Optional, Dict, Tuple
import asyncio
_preview_inflight: dict[str, asyncio.Task] = {}
_preview_lock = asyncio.Lock()
_context = None
# Playwright singletons
_playwright: Optional[Playwright] = None
_browser: Optional[Browser] = None

# Preview cache: url -> (timestamp, pdf_bytes)
_preview_cache: Dict[str, Tuple[float, bytes]] = {}
PREVIEW_TTL_SECONDS = 300  # 5 minutes

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    global _playwright, _browser, _context
    from persistence.db import get_connection
    from persistence.db_init import initialize_database
    from persistence.migrate import migrate
    from state import DB_PATH

    migrate(DB_PATH)

    conn = get_connection(DB_PATH)
    try:
        initialize_database(conn)
        print("Database schema initialized")
    finally:
        conn.close()

    _playwright = await async_playwright().start()
    _browser = await _playwright.chromium.launch()
    _context = await _browser.new_context()


@app.on_event("shutdown")
async def shutdown_event():
    global _playwright, _browser, _context

    # Close pages/context first
    if _context:
        try:
            await _context.close()
        except Exception:
            pass
        _context = None

    # Close browser next
    if _browser:
        try:
            await _browser.close()
        except Exception:
            pass
        _browser = None

    # Stop playwright last
    if _playwright:
        try:
            await _playwright.stop()
        except Exception:
            pass
        _playwright = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HandoffPayload(BaseModel):
    job_id: str
    consent: dict


class JobStatePayload(BaseModel):
    job_id: str
    state: str

VALID_STATES = {
    "saved",
    "applied",
    "interview",
    "offer",
    "rejected",
    "archived",
}



ALLOWED_PREVIEW_HOSTS = {
    "boards.greenhouse.io",
    "jobs.lever.co",
    "www.figma.com",  # optional if you want it
    "careers.airbnb.com",   # 👈 add this

}

async def _render_pdf(url: str) -> bytes:
    if _context is None:
        raise RuntimeError("Browser context not initialized")

    page = await _context.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        await page.wait_for_timeout(800)
        print(f"[RENDER] real render for {url}")
        return await page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "12mm", "bottom": "12mm", "left": "12mm", "right": "12mm"},
        )
    finally:
        await page.close()



def _prune_cache(now: float) -> None:
    expired = [k for k, (ts, _) in _preview_cache.items() if (now - ts) >= PREVIEW_TTL_SECONDS]
    for k in expired:
        _preview_cache.pop(k, None)


def _normalize_filter(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if normalized.lower() == "all":
        return None
    return normalized


@app.get("/api/discovery-feed")
async def discovery_feed(
    page: int = Query(1, ge=1, description="1-based page number"),
    page_size: int = Query(50, ge=1, le=500, description="Page size"),
    location: Optional[str] = Query(None, description="Optional location substring"),
    role: Optional[str] = Query(None, description="Optional title keyword"),
    experience: Optional[str] = Query(
        None, description="Optional experience filter: junior | mid | senior"
    ),
    company: Optional[str] = Query(None, description="Optional company substring"),
):
    from persistence.db import get_connection
    from persistence.repos.jobs_repo import JobsRepo
    from state import DB_PATH

    conn = get_connection(DB_PATH)
    try:
        repo = JobsRepo(conn)
        jobs, total_jobs = repo.list_discovery_feed_jobs(
            page=page,
            page_size=page_size,
            location=_normalize_filter(location),
            role=_normalize_filter(role),
            experience=_normalize_filter(experience),
            company=_normalize_filter(company),
        )
    finally:
        conn.close()

    return {
        "page": page,
        "page_size": page_size,
        "total_jobs": total_jobs,
        "jobs": jobs,
    }

@app.get("/api/discovery-summary")
async def discovery_summary(
    location: str = Query("bay_area", description="Location filter: bay_area | all")
):
    try:
        since = load_last_run()

        text = summarize_since(
            since_iso=since,
            location_mode=location,
        )

        return {
            "summary": text
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/saved-jobs")
async def saved_jobs():
    from persistence.db import get_connection
    from persistence.repos.jobs_repo import JobsRepo
    from state import DB_PATH

    conn = get_connection(DB_PATH)
    try:
        jobs_repo = JobsRepo(conn)
        jobs = jobs_repo.list_saved_jobs()
    finally:
        conn.close()

    return {"jobs": jobs}


@app.get("/api/job-interpretation")
async def job_interpretation(
    job_id: str = Query(..., description="Canonical job id"),
):
    from persistence.db import get_connection
    from persistence.repos.job_interpretation_repo import JobInterpretationRepo
    from state import DB_PATH

    conn = get_connection(DB_PATH)
    try:
        repo = JobInterpretationRepo(conn)
        interpretation = repo.get_interpretation(job_id)
    finally:
        conn.close()

    return {
        "job_id": job_id,
        "interpretation": interpretation,
    }


@app.post("/api/job-state")
async def set_job_state(payload: JobStatePayload):
    from persistence.db import get_connection
    from persistence.repos.job_user_state_repo import JobUserStateRepo
    from state import DB_PATH

    conn = get_connection(DB_PATH)
    try:
        if payload.state not in VALID_STATES:
            raise HTTPException(status_code=400, detail="Invalid job state")
        repo = JobUserStateRepo(conn)
        repo.set_state(payload.job_id, payload.state)
        conn.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

    return {"success": True}


@app.delete("/api/job-state")
async def clear_job_state(job_id: str = Query(..., description="Job id to clear user state")):
    from persistence.db import get_connection
    from persistence.repos.job_user_state_repo import JobUserStateRepo
    from state import DB_PATH

    conn = get_connection(DB_PATH)
    try:
        repo = JobUserStateRepo(conn)
        repo.clear_state(job_id)
        conn.commit()
    finally:
        conn.close()

    return {"success": True}

@app.get("/api/user-preview")
async def user_preview(url: str = Query(..., description="Job listing URL")):
    # --- Validate URL ---
    print(f"[REQ] url param = {repr(url)}")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Invalid URL scheme.")
    if parsed.netloc not in ALLOWED_PREVIEW_HOSTS:
        raise HTTPException(status_code=400, detail=f"Host not allowed: {parsed.netloc}")

    # --- Server-side cache (fast path) ---
    now = time.time()
    _prune_cache(now)
    cached = _preview_cache.get(url)
    if cached and (now - cached[0]) < PREVIEW_TTL_SECONDS:
        print(f"[PREVIEW] {url} (cached=True)")
        return Response(
            content=cached[1],
            media_type="application/pdf",
            headers={
                "Cache-Control": "private, max-age=300",
                "Content-Disposition": 'inline; filename="job-preview.pdf"',
                "X-Content-Type-Options": "nosniff",
                "X-Preview-Cache": "HIT",
            },
        )

    # --- Inflight dedupe (prevent stampede) ---
    async with _preview_lock:
        task = _preview_inflight.get(url)
        if task is None:
            print(f"[PREVIEW] {url} (cached=False, starting render)")
            task = asyncio.create_task(_render_pdf(url))
            _preview_inflight[url] = task
        else:
            print(f"[PREVIEW] {url} (waiting on inflight render)")

    try:
        pdf_bytes = await task
    finally:
        # Clear inflight task (only if still the same one)
        async with _preview_lock:
            if _preview_inflight.get(url) is task:
                _preview_inflight.pop(url, None)

    # Store in server-side cache
    _preview_cache[url] = (time.time(), pdf_bytes)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Cache-Control": "private, max-age=300",
            "Content-Disposition": 'inline; filename="job-preview.pdf"',
            "X-Content-Type-Options": "nosniff",
            "X-Preview-Cache": "MISS",
        },
    )


@app.post("/api/hydrate-job")
async def handle_hydrate_job(payload: HandoffPayload):
    try:
        consent = ConsentPayload(
            job_id=payload.job_id,
            scope=payload.consent["scope"],
            granted_at=datetime.fromisoformat(
                payload.consent["granted_at"].replace("Z", "+00:00")
            ),
        )

        # 🔒 Explicit single-scope enforcement
        if consent.scope != "hydrate":
            raise HTTPException(
                status_code=400,
                detail="This endpoint only accepts 'hydrate' scope."
            )

        # 🔒 Canonical job_id enforcement
        parts = payload.job_id.split(":")

        if len(parts) != 3:
            raise HTTPException(
                status_code=400,
                detail="Invalid job_id format. Expected 'provider:company:external_id'."
            )

        provider, company, external_id = parts

        if not provider or not company or not external_id:
            raise HTTPException(
                status_code=400,
                detail="Invalid job_id components."
            )

        from persistence.db import get_connection
        from state import DB_PATH

        # Lookup job URL from DB
        conn = get_connection(DB_PATH)
        row = conn.execute(
            "SELECT url FROM jobs WHERE provider_job_key = ?",
            (consent.job_id,)
        ).fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Job not found.")

        job_url = row[0]

        fetcher = get_fetcher(consent.job_id, job_url)
        read_result = await read_job_for_ui(consent, fetcher)

        raw_availability = read_result.source.availability
        if raw_availability not in {"available", "unavailable"}:
            print(f"[WARN] Unexpected availability value: {raw_availability}")

        if raw_availability == "available":
            availability = "available"
        else:
            # Covers None, "", unexpected values, and explicit "unavailable"
            availability = "unavailable"

        return {
            "job_id": read_result.job_id,
            "content": read_result.content,
            "availability": availability,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Bridge Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))



@app.post("/api/interpret-job")
async def handle_interpret_job(payload: HandoffPayload):

    try:
        scope = payload.consent.get("scope")

        if scope != "interpret_job_posting":
            raise HTTPException(
                status_code=400,
                detail="This endpoint only accepts 'interpret_job_posting' scope."
            )

        job_id = payload.job_id

        if not job_id:
            raise HTTPException(status_code=400, detail="Missing job_id")

        from phase5.phase5_1.types import ConsentPayload
        from persistence.db import get_connection
        from state import DB_PATH

        consent = ConsentPayload(
            job_id=job_id,
            scope="hydrate",
            granted_at=datetime.utcnow()
        )

        # Lookup job URL
        conn = get_connection(DB_PATH)
        row = conn.execute(
            "SELECT url FROM jobs WHERE provider_job_key = ?",
            (job_id,)
        ).fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Job not found.")

        job_url = row[0]

        fetcher = get_fetcher(job_id, job_url)
        read_result = await read_job_for_ui(consent, fetcher)

        print("---- INTERPRET DEBUG ----")
        print("Content length:", len(read_result.content) if read_result.content else 0)
        print("--------------------------")

        if not read_result.content:
            raise HTTPException(
                status_code=400,
                detail="Hydrated content missing"
            )

        interpretation_input = InterpretationInput(
            job_id=job_id,
            raw_content=read_result.content,
            read_at=read_result.read_at,
        )

        interpreter = Phase52Interpreter()
        interpreter.set_input(interpretation_input)

        result = interpreter.interpret()

        return {
            "job_id": job_id,
            "interpretation": result
        }

    except InterpretationNotAuthorizedError as e:
        raise HTTPException(status_code=403, detail=str(e))

    except InvalidInputSourceError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
