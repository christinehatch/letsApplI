"""Greenhouse adapter with API-first discovery and board JSON fallback."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import requests
from bs4 import BeautifulSoup

from adapters.greenhouse_board_parser import parse_greenhouse_board
from discovery.signal_classifier import classify_job_signals


API_TIMEOUT_SECONDS = 20
USER_AGENT = "letsApplI/greenhouse-adapter"


@dataclass(frozen=True)
class DiscoveredJob:
    provider: str
    provider_job_key: str
    company: str
    title: str
    location_raw: str
    url: str
    description_html: str
    description_text: str
    signals: list[str]
    discovered_at: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _html_to_text(html: str) -> str:
    return BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)


def _from_api_payload(company: str, token: str, jobs: list[dict[str, Any]]) -> list[DiscoveredJob]:
    discovered_at = _now_iso()
    out: list[DiscoveredJob] = []

    for job in jobs:
        job_id = str(job.get("id", "")).strip()
        if not job_id:
            continue

        title = str(job.get("title", "")).strip()
        location = str(((job.get("location") or {}).get("name") or "")).strip()
        url = str(job.get("absolute_url", "")).strip()
        description_html = str(job.get("content") or "")
        description_text = _html_to_text(description_html)
        signals = classify_job_signals(title, description_text)

        out.append(
            DiscoveredJob(
                provider="greenhouse",
                provider_job_key=f"greenhouse:{token}:{job_id}",
                company=company,
                title=title,
                location_raw=location,
                url=url,
                description_html=description_html,
                description_text=description_text,
                signals=signals,
                discovered_at=discovered_at,
            )
        )

    return out


def _from_board_fallback(company: str, token: str, board_url: str) -> list[DiscoveredJob]:
    discovered_at = _now_iso()
    parsed_jobs = parse_greenhouse_board(board_url)

    out: list[DiscoveredJob] = []
    for job in parsed_jobs:
        job_id = str(job.get("job_id", "")).strip()
        if not job_id:
            continue

        description_html = str(job.get("description_html") or "")
        description_text = str(job.get("description_text") or "")
        title = str(job.get("title") or "").strip()
        signals = classify_job_signals(title, description_text)

        out.append(
            DiscoveredJob(
                provider="greenhouse",
                provider_job_key=f"greenhouse:{token}:{job_id}",
                company=company,
                title=title,
                location_raw=str(job.get("location") or "").strip(),
                url=str(job.get("absolute_url") or "").strip(),
                description_html=description_html,
                description_text=description_text,
                signals=signals,
                discovered_at=discovered_at,
            )
        )

    return out


class GreenhouseAdapter:
    """Discover Greenhouse jobs with deterministic API+fallback behavior."""

    def discover(self, token: str, company: str) -> list[DiscoveredJob]:
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
        board_url = f"https://boards.greenhouse.io/{token}"

        try:
            response = requests.get(
                api_url,
                timeout=API_TIMEOUT_SECONDS,
                headers={"User-Agent": USER_AGENT},
            )
        except requests.RequestException:
            return _from_board_fallback(company=company, token=token, board_url=board_url)

        if response.status_code != 200:
            return _from_board_fallback(company=company, token=token, board_url=board_url)

        payload = response.json()
        jobs = payload.get("jobs", []) if isinstance(payload, dict) else []
        return _from_api_payload(company=company, token=token, jobs=jobs)


def discover_greenhouse_jobs(token: str, company: str) -> list[DiscoveredJob]:
    """Convenience wrapper for call sites that do not need class instantiation."""
    return GreenhouseAdapter().discover(token=token, company=company)
