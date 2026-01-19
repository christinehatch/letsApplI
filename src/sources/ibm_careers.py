# src/sources/ibm_careers.py

from datetime import datetime
import urllib.request
from typing import Dict
import re

def _strip_html_tags(html: str) -> str:
    text = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.S)
    text = re.sub(r"<style.*?>.*?</style>", "", text, flags=re.S)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\n\s*\n+", "\n\n", text)

def _normalize(text: str) -> str:
    return (
        text.lower()
        .replace("–", "-")
        .replace("—", "-")
        .strip()
    )

def _extract_job_id(url: str) -> str:
    # Example: jobId=77594
    if "jobId=" in url:
        return url.split("jobId=")[-1].split("&")[0]
    return ""

def _extract_title(html: str) -> str:
    # Placeholder: improve later if needed
    # Safe failure = empty string
    return ""

def _extract_location(html: str) -> str:
    # IBM often embeds location inconsistently
    return ""

def _extract_description(html: str) -> str:
    """
    Extracts the main descriptive body of the job posting.

    Includes:
    - Role overview
    - Responsibilities
    - Contextual explanation

    Excludes:
    - Navigation
    - Footer boilerplate (best effort)
    """

    # Simple heuristic: strip tags later, keep content wide
    text = _strip_html_tags(html)

    # Optionally trim obvious boilerplate phrases later
    return text.strip()

def _extract_section_between(text: str, start_marker: str, end_markers: list[str]) -> str:
    start = text.find(start_marker)
    if start == -1:
        return ""

    start += len(start_marker)

    end_positions = [
        text.find(m, start) for m in end_markers if text.find(m, start) != -1
    ]

    end = min(end_positions) if end_positions else len(text)
    return text[start:end].strip()



def _extract_requirements(html: str) -> str:
    text = _strip_html_tags(html)

    markers = [
        "Required education",
        "Required technical and professional expertise",
        "Hands-on experience is expected",
        "Preferred technical and professional experience",
    ]

    collected = []

    for i, marker in enumerate(markers):
        next_markers = markers[i+1:]
        section = _extract_section_between(text, marker, next_markers)
        if section:
            collected.append(marker + "\n" + section)

    return "\n\n".join(collected).strip()


def fetch_job(url: str) -> Dict[str, str]:
    """
    IBM Careers adapter

    Characteristics:
    - Server-rendered HTML
    - Prose-heavy descriptions
    - Mixed signal sections (marketing + responsibilities + requirements)

    This adapter performs:
    - Raw HTML fetch
    - Conservative text extraction
    - No inference or interpretation
    """

    with urllib.request.urlopen(url) as response:
        raw_html = response.read().decode("utf-8", errors="ignore")

    # --- Minimal metadata extraction (safe defaults) ---
    job = {
        "source": "ibm",
        "fetched_at": datetime.utcnow().isoformat(),
        "url": url,
        "job_id": _extract_job_id(url),

        "title": _extract_title(raw_html),
        "location": _extract_location(raw_html),

        "description_text": _extract_description(raw_html),
        "requirements_text": "",

        # 👇 NEW (this is the important part)
        "extraction_mode": "server_html_only",
        "requirements_available": False,
        "blocked_reason": "client_side_rendered",

        "raw_html": raw_html,
    }

    return job
