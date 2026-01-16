import json
from pathlib import Path
from datetime import datetime

STATE_DIR = Path(__file__).resolve().parent.parent / "state"
STATE_FILE = STATE_DIR / "seen_jobs.json"


def job_identity(job: dict) -> str:
    """
    Canonical, deterministic job identity.
    """
    return f"{job['source']}:{job['source_job_id']}"


def load_seen_jobs() -> dict:
    if not STATE_FILE.exists():
        return {}
    return json.loads(STATE_FILE.read_text())


def save_seen_jobs(seen: dict) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(seen, indent=2))


def apply_first_seen(jobs: list[dict], now: datetime) -> list[dict]:
    """
    Assign first_seen_at deterministically using local state.
    """
    seen = load_seen_jobs()
    updated = False

    for job in jobs:
        key = job_identity(job)

        if key in seen:
            job["first_seen_at"] = datetime.fromisoformat(seen[key])
        else:
            job["first_seen_at"] = now
            seen[key] = now.isoformat()
            updated = True

    if updated:
        save_seen_jobs(seen)

    return jobs
