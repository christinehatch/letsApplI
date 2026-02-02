# src/discovery/run_state.py
from __future__ import annotations

import json
import os
import time
from typing import Optional

DEFAULT_RUN_STATE_PATH = os.path.join("state", "discovery_run_state.json")


def load_last_run(path: str = DEFAULT_RUN_STATE_PATH) -> float:
    if not os.path.exists(path):
        return time.time() - 24 * 3600  # fallback: last 24h
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return float(data.get("last_run_at", time.time() - 24 * 3600))


def save_last_run(ts: float, path: str = DEFAULT_RUN_STATE_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"last_run_at": ts}, f, indent=2, sort_keys=True)

