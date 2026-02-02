# src/phase5/phase5_3/analyzer.py

from typing import Optional, Dict, Any
from datetime import datetime, timezone

from .errors import (
    FitAnalysisNotAuthorizedError,
    InvalidFitInputError,
)
from .types import FitAnalysisResult
from src.phase5.phase5_2.types import InterpretationResult


class Phase53FitAnalyzer:
    """
    Phase 5.3 Fit Analyzer — Non-Prescriptive Analysis

    This class compares Phase 5.2 interpretation artifacts
    with explicit user-provided data to surface alignment signals.

    IMPORTANT:
    - Performs NO recommendations
    - Performs NO resume modification
    - Performs NO scoring or ranking
    """

    def __init__(self):
        self._interpretation: Optional[InterpretationResult] = None
        self._user_materials: Optional[Dict[str, Any]] = None
        self._user_consented: bool = False

    # -------------------------
    # Input lifecycle
    # -------------------------

    def set_interpretation(self, interpretation: InterpretationResult) -> None:
        self._interpretation = interpretation

    def set_user_materials(self, materials: Dict[str, Any]) -> None:
        self._user_materials = materials

    def set_user_consent(self, explicit: bool) -> None:
        self._user_consented = explicit

    # -------------------------
    # Analysis entrypoint
    # -------------------------

    def analyze(self) -> FitAnalysisResult:
        # ---- Guard: interpretation required ----
        if self._interpretation is None:
            raise FitAnalysisNotAuthorizedError(
                "Phase 5.2 interpretation is required"
            )

        # ---- Guard: explicit user consent required ----
        if not self._user_consented:
            raise FitAnalysisNotAuthorizedError(
                "Explicit user consent is required for fit analysis"
            )

        # ---- Guard: user materials required ----
        if not self._user_materials:
            raise InvalidFitInputError(
                "User-provided materials are required for fit analysis"
            )

        # ---- Minimal non-prescriptive stub output ----
        return FitAnalysisResult(
            job_id=self._interpretation.job_id,
            analyzed_at=datetime.now(timezone.utc),
            interpretation_source_at=self._interpretation.source_read_at,

            matches={},
            gaps={},
            ambiguities=[],

            summary=(
                "This analysis describes observable alignment between "
                "job requirements and user-provided materials."
            ),

            limitations=[
                "Fit analysis logic not yet implemented",
                "No evaluative or prescriptive conclusions drawn",
            ],
        )
