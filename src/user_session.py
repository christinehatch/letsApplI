from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.state import STATE_DIR

DEFAULT_SESSION_PATH = STATE_DIR / "user_session.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_last_seen(path: Optional[Path] = None) -> Optional[str]:
    session_path = path or DEFAULT_SESSION_PATH
    if not session_path.exists():
        return None

    try:
        data = json.loads(session_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    value = data.get("last_seen_at")
    if isinstance(value, str) and value.strip():
        return value
    return None


def update_last_seen(path: Optional[Path] = None) -> str:
    session_path = path or DEFAULT_SESSION_PATH
    now_iso = _now_iso()
    session_path.parent.mkdir(parents=True, exist_ok=True)
    session_path.write_text(
        json.dumps({"last_seen_at": now_iso}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return now_iso
