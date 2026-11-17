# src/discovery/models.py
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional
import time


BANNED_META_KEYS = {
    "description",
    "content",
    "requirements",
    "responsibilities",
    "qualifications",
    "job_description",
    "body",
    "text",
    "html",
}


def assert_metadata_only(raw_meta: Dict[str, Any]) -> None:
    """Hard guard: discovery is metadata-only. No description-like fields allowed."""
    lower_keys = {str(k).lower() for k in raw_meta.keys()}
    banned = sorted(lower_keys.intersection(BANNED_META_KEYS))
    if banned:
        raise ValueError(f"Discovery meta contained banned content keys: {banned}")


@dataclass(frozen=True)
class Signal:
    signal_id: str
    company: str
    method: str  # e.g. "greenhouse_job_board_api"
    poll_interval_minutes: int = 360
    last_polled_at: float = 0.0
    availability: str = "available"  # available | unavailable
    notes: str = ""
    config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def to_utc_iso(value: Any) -> Optional[str]:
    """
    Normalize a board's date (ISO string with any offset, or epoch
    milliseconds) to UTC ISO-8601, so dates sort correctly as text.
    Returns None for anything unreadable.
    """
    from datetime import datetime, timezone

    if value is None or value == "" or isinstance(value, bool):
        return None
    try:
        if isinstance(value, (int, float)):
            dt = datetime.fromtimestamp(value / 1000, tz=timezone.utc)
        else:
            text = str(value).strip().replace("Z", "+00:00")
            dt = datetime.fromisoformat(text)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()
    except (ValueError, OverflowError, OSError):
        return None


@dataclass
class DiscoveredJob:
    job_uid: str                 # deterministic unique key per job
    company: str
    source_signal_id: str
    external_job_id: str
    title: str
    location: str
    url: str
    first_seen_at: float
    last_seen_at: float
    status: str = "active"       # active | stale
    raw_meta: Dict[str, Any] = field(default_factory=dict)
    posted_at: Optional[str] = None  # when the company published it (UTC ISO), if the board says

    def __post_init__(self) -> None:
        assert_metadata_only(self.raw_meta)

    @staticmethod
    def now_ts() -> float:
        return time.time()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

