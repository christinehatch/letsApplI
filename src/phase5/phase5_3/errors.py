# src/phase5/phase5_3/errors.py

class FitAnalysisNotAuthorizedError(Exception):
    """Raised when Phase 5.3 is invoked without proper consent or prerequisites."""


class InvalidFitInputError(Exception):
    """Raised when required inputs for fit analysis are missing or invalid."""

