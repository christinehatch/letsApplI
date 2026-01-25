from src.phase5.phase5_1.reader import Phase51Reader
from src.phase5.phase5_1.types import ConsentPayload, ReadResult


def read_job_for_ui(
    consent: ConsentPayload,
    fetch_job_content,
) -> ReadResult:
    """
    UI-facing adapter for Phase 5.1.

    This function:
    - does NOT interpret
    - does NOT transform content
    - does NOT persist results
    - returns ReadResult verbatim
    """

    reader = Phase51Reader(fetch_job_content=fetch_job_content)
    reader.set_consent(consent)

    return reader.read()

