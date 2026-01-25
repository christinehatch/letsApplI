import pytest
from datetime import datetime

from src.phase5.phase5_1.reader import Phase51Reader
from src.phase5.phase5_1.types import ConsentPayload
from src.phase5.phase5_1.errors import (
    NotAuthorizedError,
    InvalidScopeError,
)

def test_read_without_consent_raises_not_authorized():
    """
    INV-5.1-CONSENT-001
    Reading must not occur without explicit consent.
    """
    reader = Phase51Reader()

    with pytest.raises(NotAuthorizedError):
        reader.read()
def test_read_with_wrong_scope_raises_invalid_scope():
    """
    INV-5.1-CONSENT-002
    Consent scope must be exactly 'read_job_posting'.
    """
    reader = Phase51Reader()

    consent = ConsentPayload(
        job_id="job-123",
        scope="read_anything_else",
        granted_at=datetime.utcnow(),
        revocable=True,
    )

    reader.set_consent(consent)

    with pytest.raises(InvalidScopeError):
        reader.read()

def test_read_does_not_return_content_when_not_authorized():
    """
    INV-5.1-READ-002 (guarded)
    No job content may be returned when authorization fails.
    """
    reader = Phase51Reader()

    try:
        reader.read()
    except Exception:
        pass

    # There must be no accidental content leakage
    assert not hasattr(reader, "content")


