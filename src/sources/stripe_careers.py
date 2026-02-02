"""
Stripe Careers source adapter (Phase 3).

Read-only ingestion from Stripe's public Greenhouse job board.
No ranking, no persistence, no posting-date inference.
"""

from datetime import datetime
import json
import urllib.request
from typing import List, Dict
from discovery.location_filters import is_stripe_norcal


GREENHOUSE_BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"

SOURCE_LABEL = "stripe"
COMPANY_NAME = "Stripe"






def fetch_jobs() -> List[Dict]:
    """
    Fetch Stripe jobs from Greenhouse and return normalized job dicts.

    Returns:
        List[Dict]: List of job objects conforming to Phase 3 contract.
                    Returns [] on any failure.
    """
    try:
        with urllib.request.urlopen(GREENHOUSE_BOARD_URL, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return []

    jobs = payload.get("jobs", [])
    normalized: List[Dict] = []

    for job in jobs:
        job_id = job.get("id")
        title = job.get("title")
        location = (job.get("location") or {}).get("name")
        url = job.get("absolute_url")

        if not job_id or not title or not location or not url:
            continue

        if not is_stripe_norcal(location):
            continue

        normalized.append(
            {
                "source": SOURCE_LABEL,
                "source_job_id": str(job_id),
                "title": title,
                "company": COMPANY_NAME,
                "location": location,
                "url": url,
            }
        )

    return normalized




