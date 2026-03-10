import sys
import os
import hashlib
import json
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
    Phase52ValidationError,
)
from discovery.summary import summarize_since
from discovery.run_state import load_last_run

# Adds the project root to the Python path so 'src' is discoverable
sys.path.append(os.path.join(os.getcwd(), "src"))

from ui.read_job import read_job_for_ui, get_fetcher
from phase5.phase5_1.types import ConsentPayload

import time
from playwright.async_api import async_playwright, Browser, Playwright
from typing import Optional, Dict, Tuple, Any
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


class ReadJobPayload(BaseModel):
    job_id: str


class ManualInterpretPayload(BaseModel):
    raw_content: str

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


def _normalize_signal_filters(value: Optional[str]) -> list[str]:
    if value is None:
        return []
    normalized = [part.strip().lower() for part in value.split(",")]
    out: list[str] = []
    for signal in normalized:
        if not signal or signal == "all":
            continue
        if signal not in out:
            out.append(signal)
    return out


def _parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value or not isinstance(value, str):
        return None
    try:
        # Support common UTC "Z" suffix.
        normalized = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
        return dt
    except ValueError:
        return None


def classify_discovery_jobs(jobs: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """
    Deterministically group discovery jobs for future UI consumption.

    Rules:
    - new_today_high:
      within last 24h and has >=1 strong signal.
    - new_today_low:
      within last 24h and has no strong signal.
    - skipped:
      older than 48h OR user state is ignored/archived.
    """
    now = datetime.now().astimezone()
    strong_signals = {
        "ai",
        "machine_learning",
        "product",
        "backend",
        "frontend",
        "platform",
    }

    grouped: dict[str, list[dict[str, Any]]] = {
        "new_today_high": [],
        "new_today_low": [],
        "skipped": [],
    }

    for job in jobs:
        first_seen_raw = job.get("first_seen_at")
        first_seen = _parse_iso_datetime(first_seen_raw)
        state = str(job.get("state") or "").strip().lower()
        job_signals = {
            str(signal).strip().lower()
            for signal in (job.get("signals") or [])
            if str(signal).strip()
        }

        has_strong_signal = len(job_signals.intersection(strong_signals)) > 0
        age_hours: Optional[float] = None
        if first_seen:
            age_hours = (now - first_seen).total_seconds() / 3600.0

        is_skipped = state in {"ignored", "archived"} or (
            age_hours is not None and age_hours > 48.0
        )
        if is_skipped:
            grouped["skipped"].append(job)
            continue

        is_new_today = age_hours is not None and age_hours <= 24.0
        if is_new_today and has_strong_signal:
            grouped["new_today_high"].append(job)
            continue
        if is_new_today:
            grouped["new_today_low"].append(job)

    return grouped


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
    ai_filter: Optional[str] = Query(None, description="Optional AI filter: ai_only"),
    signal: Optional[str] = Query(None, description="Optional title-signal bucket"),
    signals: Optional[str] = Query(None, description="Optional comma-separated title-signal buckets"),
):
    from analysis.ai_relevance import score_ai_relevance
    from persistence.db import get_connection
    from persistence.repos.jobs_repo import JobsRepo
    from state import DB_PATH

    conn = get_connection(DB_PATH)
    try:
        repo = JobsRepo(conn)
        selected_signals = _normalize_signal_filters(signals)
        normalized_signal = _normalize_filter(signal)
        if normalized_signal and normalized_signal not in selected_signals:
            selected_signals.append(normalized_signal)

        jobs, total_jobs = repo.list_discovery_feed_jobs(
            page=page,
            page_size=page_size,
            location=_normalize_filter(location),
            role=_normalize_filter(role),
            experience=_normalize_filter(experience),
            company=_normalize_filter(company),
            ai_filter=_normalize_filter(ai_filter),
            signals=selected_signals or None,
        )

        job_ids = [job.get("job_id") for job in jobs if job.get("job_id")]
        interpretation_map: dict[str, dict] = {}
        if job_ids:
            placeholders = ",".join(["?"] * len(job_ids))
            rows = conn.execute(
                f"""
                SELECT job_id, interpretation_json
                FROM job_interpretations
                WHERE job_id IN ({placeholders})
                """,
                tuple(job_ids),
            ).fetchall()

            for row in rows:
                interpretation_json = row["interpretation_json"]
                if not interpretation_json:
                    continue
                try:
                    interpretation_map[row["job_id"]] = json.loads(interpretation_json)
                except json.JSONDecodeError:
                    continue

        for job in jobs:
            interpretation = interpretation_map.get(job.get("job_id", ""))
            if interpretation:
                ai_score = score_ai_relevance(interpretation)
                job["ai_relevance_score"] = ai_score["ai_relevance_score"]
                job["ai_relevance_level"] = ai_score["ai_relevance_level"]
            else:
                job["ai_relevance_score"] = None
                job["ai_relevance_level"] = None
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


@app.get("/api/hydrated-job")
async def get_hydrated_job(
    job_id: str = Query(..., description="Canonical job id"),
):
    from persistence.db import get_connection
    from state import DB_PATH

    conn = get_connection(DB_PATH)

    try:
        row = conn.execute(
            """
            SELECT h.raw_content
            FROM hydrations h
            JOIN jobs j
              ON j.id = h.job_id
            WHERE j.provider_job_key = ?
            ORDER BY h.created_at DESC
            LIMIT 1
            """,
            (job_id,),
        ).fetchone()

        if not row:
            return {
                "job_id": job_id,
                "content": None
            }

        return {
            "job_id": job_id,
            "content": row["raw_content"]
        }

    finally:
        conn.close()


@app.get("/api/job-interpretation")
async def job_interpretation(
    job_id: str = Query(..., description="Canonical job id"),
):
    from analysis.ai_relevance import score_ai_relevance
    from persistence.db import get_connection
    from persistence.repos.job_interpretation_repo import JobInterpretationRepo
    from phase5.phase5_2.span_indexer import build_spans
    from state import DB_PATH

    conn = get_connection(DB_PATH)
    try:
        repo = JobInterpretationRepo(conn)
        record = repo.get_interpretation_record(job_id)
        interpretation = record["interpretation"] if record else None
        span_map = record["span_map"] if record else {}

        row = conn.execute(
            """
            SELECT h.raw_content
            FROM hydrations h
            JOIN jobs j
              ON j.id = h.job_id
            WHERE j.provider_job_key = ?
            ORDER BY h.created_at DESC
            LIMIT 1
            """,
            (job_id,),
        ).fetchone()

        if interpretation is not None:
            if not span_map and row and row["raw_content"]:
                span_map = {
                    span["span_id"]: span["text"]
                    for span in build_spans(row["raw_content"])
                }
            ai_score = score_ai_relevance(interpretation)
            result = {
                "job_id": job_id,
                "interpretation": interpretation,
                "span_map": span_map,
                "ai_relevance": ai_score,
            }
            print("===== INTERPRETATION SENT TO UI =====")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result

        if not row:
            result = {
                "job_id": job_id,
                "interpretation": None,
                "span_map": {},
                "ai_relevance": score_ai_relevance({}),
            }
            print("===== INTERPRETATION SENT TO UI =====")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result

        job_text = row["raw_content"]

        interpreter = Phase52Interpreter()
        interpretation_input = InterpretationInput(
            job_id=job_id,
            raw_content=job_text,
            read_at=datetime.utcnow(),
        )
        interpreter.set_input(interpretation_input)
        interpretation = interpreter.interpret()
        span_map = interpreter.get_last_span_map()

        repo.save_interpretation(
            job_id,
            interpretation,
            "phase52-placeholder",
            span_map=span_map,
        )
    finally:
        conn.close()

    result = {
        "job_id": job_id,
        "interpretation": interpretation,
        "span_map": span_map,
        "ai_relevance": score_ai_relevance(interpretation),
    }
    print("===== INTERPRETATION SENT TO UI =====")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


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


@app.post("/api/read-job")
async def read_job(payload: ReadJobPayload):
    from persistence.db import get_connection
    from persistence.repos.hydrations_repo import HydrationsRepo
    from state import DB_PATH

    job_id = payload.job_id
    if not job_id:
        raise HTTPException(status_code=400, detail="Missing job_id")

    conn = get_connection(DB_PATH)
    try:
        row = conn.execute(
            """
            SELECT h.raw_content
            FROM hydrations h
            JOIN jobs j
              ON j.id = h.job_id
            WHERE j.provider_job_key = ?
            ORDER BY h.created_at DESC
            LIMIT 1
            """,
            (job_id,),
        ).fetchone()

        if row:
            return {"content": row["raw_content"]}

        job = conn.execute(
            "SELECT id, url FROM jobs WHERE provider_job_key = ?",
            (job_id,),
        ).fetchone()
    finally:
        conn.close()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    consent = ConsentPayload(
        job_id=job_id,
        scope="hydrate",
        granted_at=datetime.utcnow(),
    )

    fetcher = get_fetcher(job_id, job["url"])
    read_result = await read_job_for_ui(consent, fetcher)

    if read_result.content:
        hydration_hash = hashlib.sha256(
            read_result.content.encode("utf-8")
        ).hexdigest()
        hydrator_config_hash = hashlib.sha256(
            b"phase5.1:read-job"
        ).hexdigest()

        conn = get_connection(DB_PATH)
        try:
            repo = HydrationsRepo(conn)
            repo.create_hydration(
                job_id=job["id"],
                hydration_hash=hydration_hash,
                raw_content=read_result.content,
                content_type="text/plain",
                hydrator_version="phase5.1-read-job",
                hydrator_config_hash=hydrator_config_hash,
                created_at=datetime.utcnow().isoformat() + "Z",
            )
            conn.commit()
        finally:
            conn.close()

    return {"content": read_result.content}



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
        from persistence.repos.job_interpretation_repo import JobInterpretationRepo
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
        span_map = interpreter.get_last_span_map()

        conn = get_connection(DB_PATH)
        try:
            repo = JobInterpretationRepo(conn)
            repo.save_interpretation(
                job_id,
                result,
                "phase52-placeholder",
                span_map=span_map,
            )
        finally:
            conn.close()

        return {
            "job_id": job_id,
            "interpretation": result,
            "span_map": span_map,
        }

    except InterpretationNotAuthorizedError as e:
        raise HTTPException(status_code=403, detail=str(e))

    except InvalidInputSourceError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Phase52ValidationError as e:
        from persistence.db import get_connection
        from persistence.repos.interpretation_attempts_repo import InterpretationAttemptsRepo
        from state import DB_PATH

        conn = get_connection(DB_PATH)
        try:
            repo = InterpretationAttemptsRepo(conn)
            repo.create_attempt(
                job_id=payload.job_id,
                raw_llm_output=e.raw_excerpt,
                validation_error=f"{e.reason_code}: {e.violation_detail}",
                timestamp=datetime.utcnow().isoformat() + "Z",
            )
            conn.commit()
        finally:
            conn.close()

        raise HTTPException(status_code=400, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/interpret-manual")
async def handle_interpret_manual(payload: ManualInterpretPayload):
    try:
        raw_content = (payload.raw_content or "").strip()
        if not raw_content:
            raise HTTPException(status_code=400, detail="raw_content is required")

        interpretation_input = InterpretationInput(
            job_id="manual:input:adhoc",
            raw_content=raw_content,
            read_at=datetime.utcnow(),
        )

        interpreter = Phase52Interpreter()
        interpreter.set_input(interpretation_input)
        result = interpreter.interpret()
        span_map = interpreter.get_last_span_map()

        return {
            "interpretation": result,
            "span_map": span_map,
        }

    except InterpretationNotAuthorizedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except InvalidInputSourceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Phase52ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
