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


# ADD THIS FUNCTION BACK:
def read_job_for_ui(consent, fetch_job_content) -> ReadResult:
    """Standard Phase 5.1 Entrypoint—Does not interpret or persist."""
    reader = Phase51Reader(fetch_job_content=fetch_job_content)
    reader.set_consent(consent)
    return reader.read()