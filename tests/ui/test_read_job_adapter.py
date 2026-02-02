from datetime import datetime, timezone
from src.ui.read_job import read_job_for_ui
from src.phase5.phase5_1.types import ConsentPayload


def test_ui_adapter_returns_read_result_verbatim():
    def fake_fetch():
        return "RAW JOB CONTENT"

    consent = ConsentPayload(
        job_id="job-1",
        scope="read_job_posting",
        granted_at=datetime.now(timezone.utc),
        revocable=True,
    )

    result = read_job_for_ui(consent, fake_fetch)

    assert result.content == "RAW JOB CONTENT"
    assert result.source.availability == "available"

