from datetime import datetime, timezone

import pytest

from src.phase5.phase5_1.reader import Phase51Reader
from src.phase5.phase5_1.types import ConsentPayload


def test_read_with_valid_consent_calls_fetch_once():
    calls = {"count": 0}

    def fake_fetch():
        calls["count"] += 1
        return "JOB CONTENT"

    reader = Phase51Reader(fetch_job_content=fake_fetch)

    consent = ConsentPayload(
        job_id="job-123",
        scope="read_job_posting",
        granted_at=datetime.now(timezone.utc),
        revocable=True,
    )

    reader.set_consent(consent)

    reader.read()

    assert calls["count"] == 1

