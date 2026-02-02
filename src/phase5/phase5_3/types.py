# src/phase5/phase5_3/types.py

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass(frozen=True)
class FitAnalysisResult:
    job_id: str
    analyzed_at: datetime
    interpretation_source_at: datetime

    matches: Dict[str, List[str]]
    gaps: Dict[str, List[str]]
    ambiguities: List[str]

    summary: str
    limitations: List[str]