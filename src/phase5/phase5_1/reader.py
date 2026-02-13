from typing import Optional, Callable
from datetime import datetime, timezone

from .types import ConsentPayload, ReadResult, SourceDescriptor
from .errors import (
    NotAuthorizedError,
    InvalidScopeError,
    ConsentRevokedError,
    SourceUnavailableError,
)


class Phase51Reader:
    """
    Phase 5.1 Reader — Consent-Scoped Reading
    """

    def __init__(
        self,
        fetch_job_content: Optional[Callable[[], str]] = None,
    ):
        self._consent: Optional[ConsentPayload] = None
        self._revoked: bool = False

        # injected dependency (test-controlled)
        self._fetch_job_content = fetch_job_content
        self._fetch_call_count = 0

    # -------------------------
    # Consent lifecycle
    # -------------------------

    def set_consent(self, consent: ConsentPayload) -> None:
        self._consent = consent

    def revoke_consent(self) -> None:
        self._revoked = True

    # -------------------------
    # Read entrypoint
    # -------------------------

    def read(self) -> ReadResult:
        # ---- Consent must exist ----
        if self._consent is None:
            raise NotAuthorizedError("No consent provided")

        # ---- Consent must not be revoked ----
        if self._revoked:
            raise ConsentRevokedError("Consent has been revoked")

        # ---- Scope must be exact ----
        authorized_scopes = ["read_job_posting", "hydrate"]
        if self._consent.scope not in authorized_scopes:
            raise InvalidScopeError(
                f"Invalid consent scope: {self._consent.scope}"
            )

        # ---- Fetch must be injected ----
        if self._fetch_job_content is None:
            raise SourceUnavailableError("No fetch function provided")

        # ---- Single authorized fetch ----
        # ---- Single authorized fetch ----
        self._fetch_call_count += 1

        try:
            content = self._fetch_job_content()
            availability = "available"
        except Exception:
            content = None
            availability = "unavailable"

        return ReadResult(
            job_id=self._consent.job_id,
            content=content,
            source=SourceDescriptor(
                origin="job_posting",
                availability=availability,
            ),
            read_at=datetime.now(timezone.utc),
        )

    # -------------------------
    # Test-only visibility
    # -------------------------

    @property
    def fetch_call_count(self) -> int:
        return self._fetch_call_count
