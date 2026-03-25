import sys
import os
import hashlib
import json
import re
import importlib.util
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from fastapi.responses import Response, JSONResponse
from urllib.parse import urlparse
from pathlib import Path

# Ensure local project packages under ./src are importable in all environments.
sys.path.append(os.path.join(os.getcwd(), "src"))

from src.phase5.phase5_2.validator_schema import validate_schema

from src.phase5.phase5_2.determinism import compute_structural_hash
from src.phase5.phase5_2.interpreter import Phase52Interpreter
from src.phase5.phase5_2.types import InterpretationInput
from src.phase5.phase5_2.errors import (
    InterpretationNotAuthorizedError,
    InvalidInputSourceError,
    Phase52ValidationError,
)
from src.discovery.summary import summarize_since
from src.discovery.run_state import load_last_run

from ui.read_job import read_job_for_ui, get_fetcher
from src.phase5.phase5_1.types import ConsentPayload

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
_browser_init_error: Optional[str] = None

# Preview cache: url -> (timestamp, pdf_bytes)
_preview_cache: Dict[str, Tuple[float, bytes]] = {}
PREVIEW_TTL_SECONDS = 300  # 5 minutes
DEFAULT_RESUME_SIGNALS = ["backend", "ai", "platform"]
BLOCKED_HYDRATION_PATTERNS = [
    "sorry, you have been blocked",
    "you are unable to access",
    "performance & security by cloudflare",
    "attention required!",
    "checking your browser before accessing",
    "cloudflare ray id",
    "why have i been blocked?",
]

app = FastAPI()


def _load_allowed_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


def _is_postgres_url(value: str) -> bool:
    lowered = value.strip().lower()
    return lowered.startswith("postgres://") or lowered.startswith("postgresql://")


async def _ensure_browser_context() -> None:
    global _playwright, _browser, _context, _browser_init_error
    if _context is not None:
        return
    try:
        if _playwright is None:
            _playwright = await async_playwright().start()
        if _browser is None:
            _browser = await _playwright.chromium.launch()
        _context = await _browser.new_context()
        _browser_init_error = None
    except Exception as exc:
        _browser_init_error = str(exc)
        raise

@app.on_event("startup")
async def startup_event():
    global _playwright, _browser, _context
    from persistence.db import get_connection
    from persistence.db_init import initialize_database
    from persistence.migrate import migrate
    from state import DB_PATH

    if not _is_postgres_url(DB_PATH):
        Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    migrate(DB_PATH)

    conn = get_connection(DB_PATH)
    try:
        initialize_database(conn)
        print("Database schema initialized")
    finally:
        conn.close()

    try:
        await _ensure_browser_context()
    except Exception as exc:
        # Preview browser is optional for core API availability.
        print(f"Preview browser init skipped at startup: {exc}")


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
    allow_origins=_load_allowed_origins(),
    allow_origin_regex=os.getenv("ALLOW_ORIGIN_REGEX"),
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


class JobIgnorePayload(BaseModel):
    job_id: str

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
        await _ensure_browser_context()
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


def _load_resume_signals_with_fallback() -> list[str]:
    module_path = Path(__file__).resolve().parent / "src" / "state" / "resume_signals.py"
    if not module_path.exists():
        return DEFAULT_RESUME_SIGNALS.copy()


def _extract_discovery_content(raw_provider_payload_json: str | None) -> str | None:
    if not raw_provider_payload_json:
        return None

    try:
        payload = json.loads(raw_provider_payload_json)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None

    if not isinstance(payload, dict):
        return None

    description_text = payload.get("description_text")
    if isinstance(description_text, str) and description_text.strip():
        return description_text

    description_html = payload.get("description_html")
    if isinstance(description_html, str) and description_html.strip():
        return description_html

    return None


def _looks_like_blocked_hydration_content(content: str | None) -> bool:
    if not content:
        return False
    normalized = content.lower()
    return any(pattern in normalized for pattern in BLOCKED_HYDRATION_PATTERNS)

    try:
        spec = importlib.util.spec_from_file_location("resume_signals_module", module_path)
        if spec is None or spec.loader is None:
            return DEFAULT_RESUME_SIGNALS.copy()
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        load_fn = getattr(module, "load_resume_signals", None)
        if not callable(load_fn):
            return DEFAULT_RESUME_SIGNALS.copy()
        loaded = load_fn()
        if not isinstance(loaded, list):
            return DEFAULT_RESUME_SIGNALS.copy()
        normalized: list[str] = []
        for signal in loaded:
            normalized_signal = str(signal).strip().lower()
            if normalized_signal and normalized_signal not in normalized:
                normalized.append(normalized_signal)
        return normalized or DEFAULT_RESUME_SIGNALS.copy()
    except Exception:
        return DEFAULT_RESUME_SIGNALS.copy()


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


def _normalize_role_and_experience(
    role: Optional[str], experience: Optional[str]
) -> tuple[Optional[str], Optional[str]]:
    normalized_role = _normalize_filter(role)
    normalized_experience = _normalize_filter(experience)
    if not normalized_role:
        return normalized_role, normalized_experience

    working_role = normalized_role
    junior_patterns = [
        r"\bnew\s+grad\b",
        r"\bentry\s+level\b",
        r"\bearly\s+career\b",
        r"\bjunior\b",
        r"\bentry\b",
        r"\bassociate\b",
    ]

    has_junior_intent = False
    for pattern in junior_patterns:
        if re.search(pattern, working_role, flags=re.IGNORECASE):
            has_junior_intent = True
            working_role = re.sub(pattern, " ", working_role, flags=re.IGNORECASE)

    normalized_role = _normalize_filter(" ".join(working_role.split()))
    if has_junior_intent and not normalized_experience:
        normalized_experience = "junior"

    return normalized_role, normalized_experience


def _expand_role_synonyms(role: Optional[str]) -> Optional[str]:
    normalized_role = _normalize_filter(role)
    if not normalized_role:
        return normalized_role

    expanded_tokens = normalized_role.split()
    token_set = set(expanded_tokens)

    phrase_synonyms = [
        (["ml"], ["machine", "learning"]),
        (["machine", "learning"], ["ml"]),
        (["ai"], ["artificial", "intelligence"]),
        (["artificial", "intelligence"], ["ai"]),
    ]

    for source_phrase, target_phrase in phrase_synonyms:
        source_found = all(token in token_set for token in source_phrase)
        if not source_found:
            continue
        for token in target_phrase:
            if token in token_set:
                continue
            expanded_tokens.append(token)
            token_set.add(token)

    return " ".join(expanded_tokens)


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


def _normalize_whitespace(text: str) -> str:
    return " ".join((text or "").split()).strip().lower()


def _is_cached_interpretation_stale(
    span_map: Optional[dict[str, str]],
    resolved_content: Optional[str],
) -> bool:
    if not span_map or not resolved_content:
        return False

    normalized_content = _normalize_whitespace(resolved_content)
    if not normalized_content:
        return False

    checked = 0
    matched = 0
    for value in span_map.values():
        if not isinstance(value, str):
            continue
        candidate = _normalize_whitespace(value)
        if len(candidate) < 24:
            continue
        checked += 1
        if candidate in normalized_content:
            matched += 1

    if checked == 0:
        return False
    return matched == 0


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
        normalized_role, normalized_experience = _normalize_role_and_experience(
            role, experience
        )
        expanded_role = _expand_role_synonyms(normalized_role)

        jobs, total_jobs = repo.list_discovery_feed_jobs(
            page=page,
            page_size=page_size,
            location=_normalize_filter(location),
            role=expanded_role,
            experience=normalized_experience,
            company=_normalize_filter(company),
            ai_filter=_normalize_filter(ai_filter),
            signal=normalized_signal,
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

        return {
            "page": page,
            "page_size": page_size,
            "total_jobs": total_jobs,
            "jobs": jobs,
        }
    finally:
        conn.close()


@app.get("/api/new-jobs-count")
async def new_jobs_count():
    from persistence.db import get_connection
    from persistence.repos.jobs_repo import JobsRepo
    from state import DB_PATH
    try:
        from user_session import get_last_seen
    except ModuleNotFoundError:
        from src.user_session import get_last_seen

    last_seen_at = get_last_seen()
    new_jobs = 0

    conn = get_connection(DB_PATH)
    try:
        repo = JobsRepo(conn)
        new_jobs = repo.count_jobs_since(last_seen_at or "1970-01-01T00:00:00Z")
    finally:
        conn.close()

    return {"new_jobs": new_jobs}


@app.post("/api/new-jobs-count/ack")
async def acknowledge_new_jobs_count():
    try:
        from user_session import update_last_seen
    except ModuleNotFoundError:
        from src.user_session import update_last_seen

    last_seen_at = update_last_seen()
    return {"ok": True, "last_seen_at": last_seen_at}


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/api/resume-signals")
async def get_resume_signals():
    return {"signals": _load_resume_signals_with_fallback()}


@app.get("/api/market-alignment")
async def get_market_alignment():
    from analysis.market_alignment import compute_market_alignment
    from persistence.db import get_connection
    from persistence.repos.jobs_repo import JobsRepo
    from state import DB_PATH

    resume_signals = _load_resume_signals_with_fallback()

    if not resume_signals:
        return {"alignment": {}}

    conn = get_connection(DB_PATH)
    try:
        repo = JobsRepo(conn)
        page = 1
        page_size = 500
        all_jobs: list[dict[str, Any]] = []

        while True:
            jobs, total_jobs = repo.list_discovery_feed_jobs(
                page=page,
                page_size=page_size,
            )
            all_jobs.extend(jobs)
            if len(all_jobs) >= total_jobs or not jobs:
                break
            page += 1
    finally:
        conn.close()

    alignment = compute_market_alignment(all_jobs, resume_signals)
    return {"alignment": alignment}


@app.get("/api/debug/discovery-status")
async def debug_discovery_status():
    from discovery.registry import load_registry
    from persistence.db import get_connection
    from state import DB_PATH

    signals = load_registry()
    available = [s for s in signals if getattr(s, "availability", "") == "available"]
    unavailable = [s for s in signals if getattr(s, "availability", "") != "available"]

    conn = get_connection(DB_PATH)
    try:
        row = conn.execute("SELECT COUNT(*) AS c FROM jobs").fetchone()
        jobs_count = int(row["c"]) if row and row["c"] is not None else 0
    finally:
        conn.close()

    return {
        "db_path": DB_PATH,
        "jobs_count": jobs_count,
        "signals_total": len(signals),
        "signals_available": len(available),
        "signals_unavailable": len(unavailable),
        "sample_failures": [
            {
                "signal_id": s.signal_id,
                "company": s.company,
                "notes": s.notes,
            }
            for s in unavailable[:10]
        ],
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
        job_row = conn.execute(
            """
            SELECT raw_provider_payload_json
            FROM jobs
            WHERE provider_job_key = ?
            LIMIT 1
            """,
            (job_id,),
        ).fetchone()

        if job_row and job_row["raw_provider_payload_json"]:
            discovery_content = _extract_discovery_content(
                job_row["raw_provider_payload_json"]
            )
            if discovery_content:
                return {
                    "job_id": job_id,
                    "content": discovery_content,
                    "content_source": "discovery",
                }

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
                "content": None,
                "content_source": None,
            }

        return {
            "job_id": job_id,
            "content": row["raw_content"],
            "content_source": "hydration",
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

        job_row = conn.execute(
            """
            SELECT raw_provider_payload_json
            FROM jobs
            WHERE provider_job_key = ?
            LIMIT 1
            """,
            (job_id,),
        ).fetchone()

        hydration_row = conn.execute(
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

        resolved_content: str | None = None
        if job_row and job_row["raw_provider_payload_json"]:
            try:
                provider_payload = json.loads(job_row["raw_provider_payload_json"])
            except (TypeError, ValueError, json.JSONDecodeError):
                provider_payload = None

            if isinstance(provider_payload, dict):
                description_html = provider_payload.get("description_html")
                description_text = provider_payload.get("description_text")

                if isinstance(description_html, str) and description_html.strip():
                    resolved_content = description_html
                elif isinstance(description_text, str) and description_text.strip():
                    resolved_content = description_text

        if resolved_content is None and hydration_row and hydration_row["raw_content"]:
            resolved_content = hydration_row["raw_content"]

        if interpretation is not None and _is_cached_interpretation_stale(
            span_map, resolved_content
        ):
            repo.delete_interpretation(job_id)
            interpretation = None
            span_map = {}

        if interpretation is not None:
            if not span_map and resolved_content:
                span_map = {
                    span["span_id"]: span["text"]
                    for span in build_spans(resolved_content)
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

        if not resolved_content:
            result = {
                "job_id": job_id,
                "interpretation": None,
                "span_map": {},
                "ai_relevance": score_ai_relevance({}),
            }
            print("===== INTERPRETATION SENT TO UI =====")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result

        job_text = resolved_content

        interpreter = Phase52Interpreter()
        interpretation_input = InterpretationInput(
            job_id=job_id,
            raw_content=job_text,
            read_at=datetime.utcnow(),
        )
        interpreter.set_input(interpretation_input)
        try:
            interpretation = interpreter.interpret()
        except Phase52ValidationError as e:
            return JSONResponse(
                status_code=200,
                content={
                    "status": "validation_failed",
                    "reason": str(e),
                },
            )
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

@app.delete("/api/job-interpretation")
async def clear_job_interpretation(
    job_id: str = Query(..., description="Canonical job id"),
):
    from persistence.db import get_connection
    from persistence.repos.job_interpretation_repo import JobInterpretationRepo
    from state import DB_PATH

    conn = get_connection(DB_PATH)
    try:
        repo = JobInterpretationRepo(conn)
        repo.delete_interpretation(job_id)
    finally:
        conn.close()

    return {"success": True, "job_id": job_id}


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


@app.post("/api/job-ignore")
async def ignore_job(payload: JobIgnorePayload):
    from persistence.db import get_connection
    from persistence.repos.job_user_state_repo import JobUserStateRepo
    from state import DB_PATH

    conn = get_connection(DB_PATH)
    try:
        repo = JobUserStateRepo(conn)
        repo.set_state(payload.job_id, "ignored")
        conn.commit()
    finally:
        conn.close()

    return {"status": "ignored"}

@app.get("/api/user-preview")
async def user_preview(url: str = Query(..., description="Job listing URL")):
    # --- Validate URL ---
    print(f"[REQ] url param = {repr(url)}")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Invalid URL scheme.")
    if parsed.netloc not in ALLOWED_PREVIEW_HOSTS:
        raise HTTPException(status_code=400, detail=f"Host not allowed: {parsed.netloc}")

    if _context is None:
        try:
            await _ensure_browser_context()
        except Exception:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Preview browser is unavailable on this instance."
                    + (f" Last error: {_browser_init_error}" if _browser_init_error else "")
                ),
            )

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
            "SELECT url, raw_provider_payload_json FROM jobs WHERE provider_job_key = ?",
            (consent.job_id,)
        ).fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Job not found.")

        job_url = row["url"] if "url" in row.keys() else row[0]
        discovery_content = _extract_discovery_content(
            row["raw_provider_payload_json"]
            if "raw_provider_payload_json" in row.keys()
            else None
        )

        fetcher = get_fetcher(consent.job_id, job_url)
        read_result = await read_job_for_ui(consent, fetcher)

        hydrated_content = (read_result.content or "").strip()
        if not hydrated_content or _looks_like_blocked_hydration_content(hydrated_content):
            hydrated_content = discovery_content or ""

        raw_availability = read_result.source.availability
        if raw_availability not in {"available", "unavailable"}:
            print(f"[WARN] Unexpected availability value: {raw_availability}")

        if hydrated_content:
            availability = "available"
        else:
            # Covers None, "", unexpected values, and explicit "unavailable"
            availability = "unavailable"

        return {
            "job_id": read_result.job_id,
            "content": hydrated_content or None,
            "availability": availability,
            "content_source": "hydration" if read_result.content else "discovery",
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
            "SELECT url, raw_provider_payload_json FROM jobs WHERE provider_job_key = ?",
            (job_id,)
        ).fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Job not found.")

        job_url = row["url"] if "url" in row.keys() else row[0]
        discovery_content = _extract_discovery_content(
            row["raw_provider_payload_json"]
            if "raw_provider_payload_json" in row.keys()
            else None
        )

        fetcher = get_fetcher(job_id, job_url)
        read_result = await read_job_for_ui(consent, fetcher)

        if not read_result.content or _looks_like_blocked_hydration_content(read_result.content):
            if discovery_content:
                read_result.content = discovery_content

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
