import sys
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from fastapi.responses import Response
from urllib.parse import urlparse
from .validator_schema import validate_schema

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
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class HandoffPayload(BaseModel):
    job_id: str
    consent: dict



ALLOWED_PREVIEW_HOSTS = {
    "boards.greenhouse.io",
    "jobs.lever.co",
    "www.figma.com",  # optional if you want it
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

        fetcher = get_fetcher(consent.job_id)
        read_result = read_job_for_ui(consent, fetcher)

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
    """
    Phase 5.2 Interpretation Endpoint (LOCKED)

    Requires:
    - scope == "interpret_job_posting"
    - Explicit consent
    """

    try:
        scope = payload.consent.get("scope")

        if scope != "interpret_job_posting":
            raise HTTPException(
                status_code=400,
                detail="This endpoint only accepts 'interpret_job_posting' scope."
            )

        # Hard lock — do not unlock yet
        raise HTTPException(
            status_code=501,
            detail="Phase 5.2 interpretation is not yet enabled."
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)