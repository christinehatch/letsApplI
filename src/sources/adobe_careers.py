"""
Adobe Careers Job Source

Deterministic job ingestion adapter.
Fetch-only implementation (Step 3).

{
  "source": "adobe",
  "fetch_status": "js_required",
  "description_text": "",
}
"""

"""

### Adobe Careers

Status: JS-gated

Adobe job listings require JavaScript execution to render job content.
Deterministic HTTP fetching returns a placeholder “job filled” page.

Support deferred to a future phase that explicitly allows
browser-based fetching with user consent and clear scope boundaries.
"""

import urllib.request
from bs4 import BeautifulSoup


class AdobeCareersError(Exception):
    pass

def _extract_job_body(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Adobe pages typically wrap job content in a main container.
    # We intentionally grab a broad section and filter later.
    main = soup.find("main")
    if not main:
        return ""

    text = main.get_text("\n", strip=True)

    return text


def fetch_job(job_url: str) -> dict:
    try:
        req = urllib.request.Request(
            job_url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="replace")

    except Exception as e:
        raise AdobeCareersError(f"Failed to fetch Adobe job page: {e}")

    job_text = _extract_job_body(html)

    return {
        "source": "adobe",
        "job_url": job_url,
        "company": "Adobe",
        "fetch_status": "js_required",
        "description_text": "",
        "requirements_text": "",
        "notes": (
            "Adobe job pages require JavaScript rendering. "
            "Deterministic HTTP fetch returns placeholder content."
        ),
    }

