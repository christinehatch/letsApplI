# src/persistence/models.py

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class JobRecord:
    id: int
    provider: str
    external_id: str
    provider_job_key: str
    company: str
    title: str
    location_raw: Optional[str]
    location_norm: Optional[str]
    url: str
    posted_at: Optional[str]
    discovered_at: str
    raw_provider_payload_json: Optional[str]
    is_archived: int
    first_seen_at: Optional[str]
