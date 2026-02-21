# src/ui/read_job.py
import os
from phase5.phase5_1.reader import Phase51Reader
from phase5.phase5_1.types import ReadResult

def get_fetcher(job_id: str):
    def fetch_job_content() -> str:
        # Use absolute path to avoid "where am I?" confusion
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(base_dir, "job.txt")

        print(f"\n--- [CHECKPOINT 1: DISCOVERY] ---")
        print(f"Targeting path: {file_path}")

        try:
            if not os.path.exists(file_path):
                print(f"!!! ERROR: job.txt does not exist at that location.")
                return ""

            with open(file_path, "r") as f:
                content = f.read()
                print(f"SUCCESS: Read {len(content)} characters from job.txt")
                # Print the first 50 chars to be sure
                print(f"PREVIEW: {content[:50]}...")
                return content
        except Exception as e:
            print(f"!!! SYSTEM ERROR: {str(e)}")
            return ""

    return fetch_job_content

    # src/ui/read_job.py


def read_job_for_ui(consent, fetch_job_content) -> ReadResult:
    """Standard Phase 5.1 Entrypoint—Does not interpret or persist."""

    # --- [AUTHORITY VALIDATION] ---
    # Explicitly allow 'hydrate' as a valid level of authority
    allowed_scopes = ["hydrate"]

    if consent.scope not in allowed_scopes:
        print(f"!!! GATEKEEPER REJECTION: Scope '{consent.scope}' is unauthorized.")
        raise ValueError(f"Invalid consent scope: {consent.scope}")

    print(f">>> GATEKEEPER: Authority '{consent.scope}' verified.")
    reader = Phase51Reader(fetch_job_content=fetch_job_content)

    # If Phase51Reader.set_consent still fails, we'll need to
    # check that specific file, but this usually unblocks the flow.
    reader.set_consent(consent)
    return reader.read()