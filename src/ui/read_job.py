from datetime import datetime, timezone

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


def read_job_interactive(job_id: str) -> None:
    """
    UX-facing interactive job reader.

    This function is responsible for:
    - creating consent
    - wiring fetch behavior
    - displaying results to the user

    It does NOT interpret or analyze.
    """

    # --- TEMP fetch stub (safe + replaceable) ---
    def fetch_job_content() -> str:
        return f"[Stub] Raw job content for {job_id}"

    consent = ConsentPayload(
        job_id=job_id,
        scope="read_job_posting",
        granted_at=datetime.now(timezone.utc),
        revocable=True,
    )

    result = read_job_for_ui(
        consent=consent,
        fetch_job_content=fetch_job_content,
    )

    print("\n--- Job Content ---\n")
    print(result.content or "[No content available]")
    print("\n-------------------\n")
