# src/discovery/run_state.py
from __future__ import annotations

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

DEFAULT_RUN_STATE_PATH = os.path.join("state", "discovery_run_state.json")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_last_run(path: str = DEFAULT_RUN_STATE_PATH) -> str:
    """
    Returns ISO UTC timestamp string.
    Default: 24 hours ago (ISO).
    """
    if not os.path.exists(path):
        fallback = datetime.now(timezone.utc) - timedelta(hours=24)
        return fallback.isoformat()

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("last_run_at", _now_iso())


def save_last_run(ts_iso: str, path: str = DEFAULT_RUN_STATE_PATH) -> None:
    """
    Expects ISO UTC string.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"last_run_at": ts_iso}, f, indent=2, sort_keys=True)