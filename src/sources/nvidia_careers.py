from datetime import datetime
from typing import Dict
import urllib.request

def fetch_job(url: str) -> Dict[str, str]:
    with urllib.request.urlopen(url) as response:
        raw_html = response.read().decode("utf-8", errors="ignore")

    return {
        "source": "nvidia",
        "fetched_at": datetime.utcnow().isoformat(),
        "url": url,
        "job_id": "",

        "description_text": "",
        "requirements_text": "",

        "extraction_mode": "js_hydrated",
        "requirements_available": False,
        "blocked_reason": "workday_client_rendered",

        "raw_html": raw_html,
    }

