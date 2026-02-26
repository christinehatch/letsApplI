import json
from pathlib import Path
from datetime import datetime, timezone
from .determinism import compute_structural_hash

SHADOW_LOG_PATH = Path("state/phase5_2_shadow_log.json")


def log_shadow_run(job_id: str, output: dict):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "job_id": job_id,
        "structural_hash": compute_structural_hash(output),
    }

    if SHADOW_LOG_PATH.exists():
        with open(SHADOW_LOG_PATH, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)

    with open(SHADOW_LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)
