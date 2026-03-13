"""Parse Greenhouse jobs using the official Job Board API."""

from __future__ import annotations

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


USER_AGENT = "letsApplI/greenhouse-board-parser"
API_URL_TEMPLATE = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"


def _extract_board_token(board_url: str) -> str:
    parsed = urlparse(board_url)
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        raise RuntimeError("Greenhouse API request failed")
    return parts[0]

def parse_greenhouse_board(board_url: str) -> list[dict]:
    """Extract jobs from the official Greenhouse Job Board API."""
    token = _extract_board_token(board_url)
    api_url = API_URL_TEMPLATE.format(token=token)
    response = requests.get(
        api_url,
        timeout=20,
        headers={"User-Agent": USER_AGENT},
    )
    if response.status_code != 200:
        raise RuntimeError("Greenhouse API request failed")
    payload = response.json()
    job_entries = payload.get("jobs", []) if isinstance(payload, dict) else []

    jobs: list[dict] = []
    for entry in job_entries:
        location_value = entry.get("location")
        if isinstance(location_value, dict):
            location = str(location_value.get("name", "")).strip()
        else:
            location = str(location_value or "").strip()

        description_html = str(entry.get("content") or "")
        description_text = BeautifulSoup(description_html, "html.parser").get_text(
            " ", strip=True
        )

        jobs.append(
            {
                "job_id": str(entry.get("id", "")).strip(),
                "title": str(entry.get("title", "")).strip(),
                "location": location,
                "description_html": description_html,
                "description_text": description_text,
                "absolute_url": str(entry.get("absolute_url") or "").strip(),
            }
        )

    return jobs


if __name__ == "__main__":
    test_url = "https://boards.greenhouse.io/coinbase"
    parsed_jobs = parse_greenhouse_board(test_url)

    for job in parsed_jobs:
        preview = (job.get("description_text") or "")[:200]
        print(f"{job['title']} - {job['location']}")
        print(preview)
        print()
