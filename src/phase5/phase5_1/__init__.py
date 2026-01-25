"""
Phase 5.1 — Consent-Scoped Reading

This package implements the first authorized job-content reading phase.
All behavior is governed by explicit consent and invariant enforcement.
"""
from typing import Optional, Callable

class Phase51Reader:
    def __init__(
        self,
        fetch_job_content: Optional[Callable[[], str]] = None,
    ):
        self._consent: Optional[ConsentPayload] = None
        self._revoked: bool = False

        # Injected fetch dependency (required for tests)
        self._fetch_job_content = fetch_job_content
        self._fetch_count: int = 0
