from dataclasses import dataclass
from typing import Optional, List, Dict
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
    Output of Phase 5.2 Interpretation.

    IMPORTANT:
    This represents structured interpretation ONLY.
    It does not imply evaluation, fit, or recommendation.
    """

    job_id: str
    interpreted_at: datetime
    source_read_at: datetime

    artifacts: Dict[str, List[str]]
    confidence: str
    limitations: List[str]
