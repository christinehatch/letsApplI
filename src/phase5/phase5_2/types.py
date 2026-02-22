from dataclasses import dataclass
from typing import  List, Dict
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
class RoleSummary:
    what_is_this_role: str
    core_mission: str
    org_context: str

@dataclass(frozen=True)
class ConsentPayload:
    job_id: str
    scope: str
    granted_at: datetime
    revocable: bool = True

@dataclass(frozen=True)
class RequirementsAnalysis:
    explicit_requirements: List[str]
    implicit_signals: List[str]
    seniority_indicators: List[str]


@dataclass(frozen=True)
class ResumeAlignment:
    strength_matches: List[str]
    resume_gaps: List[str]
    suggested_resume_bullets: List[str]


@dataclass(frozen=True)
class ProjectOpportunities:
    portfolio_project_ideas: List[str]
    apply_ai_opportunities: List[str]
    demo_angles: List[str]

@dataclass(frozen=True)
class InterpretationResult:
    job_id: str
    interpreted_at: datetime
    source_read_at: datetime
    artifacts: Dict[str, List[str]]
    confidence: str
    limitations: List[str]