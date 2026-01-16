import json
from pathlib import Path
from datetime import datetime

STATE_DIR = Path(__file__).resolve().parent.parent / "state"
STATE_FILE = STATE_DIR / "seen_jobs.json"


def load_seen_jobs() -> dict:
    if not STATE_FILE.exists():
        return {}
    return json.loads(STATE_FILE.read_text())


def save_seen_jobs(seen: dict) -> None:
    STATE_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(seen, indent=2))


def job_key(job: dict) -> str:
    return f"{job['source']}:{job.get('source_job_id', job['title'])}"

