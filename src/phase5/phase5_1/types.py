from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass(frozen=True)
class ConsentPayload:
    job_id: str
    scope: str
    granted_at: datetime
    revocable: bool


@dataclass(frozen=True)
class SourceDescriptor:
    origin: str
    availability: str  # "available" | "unavailable"


@dataclass(frozen=True)
class ReadResult:
    """
    Represents the outcome of a Phase 5.1 read attempt.

    IMPORTANT:
    This type does NOT imply interpretation, analysis, or understanding.
    """
    job_id: str
    content: Optional[str]
    source: SourceDescriptor
    read_at: Optional[datetime]

