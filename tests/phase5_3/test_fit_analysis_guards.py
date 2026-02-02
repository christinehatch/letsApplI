import pytest
from datetime import datetime, timezone

from src.phase5.phase5_3.analyzer import Phase53FitAnalyzer
from src.phase5.phase5_3.errors import (
    FitAnalysisNotAuthorizedError,
    InvalidFitInputError,
)
from src.phase5.phase5_2.types import InterpretationResult


# -------------------------
# Guard: activation & consent
# -------------------------

def test_fit_analysis_without_interpretation_raises():
    """
    INV-5.3-GUARD-001
    Phase 5.3 must not run without Phase 5.2 output.
    """
    analyzer = Phase53FitAnalyzer()

    with pytest.raises(FitAnalysisNotAuthorizedError):
        analyzer.analyze()


def test_fit_analysis_without_user_consent_raises():
    """
    INV-5.3-GUARD-002
    Fit analysis requires explicit user intent.
    """
    analyzer = Phase53FitAnalyzer()

    fake_interpretation = InterpretationResult(
        job_id="job-123",
        interpreted_at=datetime.now(timezone.utc),
        source_read_at=datetime.now(timezone.utc),
        artifacts={},
        confidence="low",
        limitations=[],
    )

    analyzer.set_interpretation(fake_interpretation)

    with pytest.raises(FitAnalysisNotAuthorizedError):
        analyzer.analyze()


# -------------------------
# Guard: input validity
# -------------------------

def test_fit_analysis_requires_user_materials():
    """
    INV-5.3-INPUT-001
    Fit analysis must not run without user-provided data.
    """
    analyzer = Phase53FitAnalyzer()

    analyzer.set_interpretation(
        InterpretationResult(
            job_id="job-123",
            interpreted_at=datetime.now(timezone.utc),
            source_read_at=datetime.now(timezone.utc),
            artifacts={"requirements": ["Python"]},
            confidence="high",
            limitations=[],
        )
    )

    analyzer.set_user_consent(explicit=True)

    with pytest.raises(InvalidFitInputError):
        analyzer.analyze()


# -------------------------
# Guard: non-prescriptive language
# -------------------------

def test_fit_analysis_output_is_non_prescriptive():
    """
    INV-5.3-OUTPUT-001
    Phase 5.3 output must not contain advice or judgments.
    """
    analyzer = Phase53FitAnalyzer()

    analyzer.set_interpretation(
        InterpretationResult(
            job_id="job-123",
            interpreted_at=datetime.now(timezone.utc),
            source_read_at=datetime.now(timezone.utc),
            artifacts={"requirements": ["Python"]},
            confidence="high",
            limitations=[],
        )
    )

    analyzer.set_user_materials(
        {"skills": ["Python"]}
    )
    analyzer.set_user_consent(explicit=True)

    result = analyzer.analyze()

    forbidden_phrases = [
        "you should",
        "good fit",
        "strong candidate",
        "recommend",
        "missing critical",
    ]

    output_text = result.summary.lower()

    for phrase in forbidden_phrases:
        assert phrase not in output_text

