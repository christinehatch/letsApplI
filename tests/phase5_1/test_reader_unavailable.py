import pytest
from datetime import datetime, timezone

from src.phase5.phase5_1.reader import Phase51Reader
from src.phase5.phase5_1.types import ConsentPayload


def test_read_unavailable_source_returns_unavailable_result():
    """
    INV-5.1-READ-003
    If the source is unavailable, Phase 5.1 must:
    - not retry
    - not raise
    - return a truthful unavailable ReadResult
    """

    def failing_fetch():
        raise RuntimeError("403 Forbidden")

    reader = Phase51Reader(fetch_job_content=failing_fetch)

    consent = ConsentPayload(
        job_id="job-404",
        scope="read_job_posting",
        granted_at=datetime.now(timezone.utc),
        revocable=True,
    )

    reader.set_consent(consent)

    result = reader.read()

    assert result.job_id == "job-404"
    assert result.content is None
    assert result.source.origin == "job_posting"
    assert result.source.availability == "unavailable"
    assert result.read_at is not None

