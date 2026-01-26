from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass(frozen=True)
class InterpretationInput:
    """
    Input provided to Phase 5.2.

    Must originate from a completed Phase 5.1 read.
    """
    job_id: str
    raw_content: str
    read_at: datetime


@dataclass(frozen=True)
class InterpretationResult:
    """
    Output of Phase 5.2 interpretation.

    IMPORTANT:
    - This is NOT advice
    - This is NOT ranking
    - This is NOT recommendation
    """
    job_id: str
    interpreted_at: datetime

    # intentionally empty for now
    notes: Optional[str] = None

