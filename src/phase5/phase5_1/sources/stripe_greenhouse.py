import json
import urllib.request


def fetch_stripe_job_content(job_id: str) -> str:
    """
    Phase 5.1 — Read-only hydration.
    Fetch raw job description text for a Stripe job.

    - Read-only
    - No interpretation
    - No persistence
    - Minimal structural cleanup only
    """
    job_url = f"https://boards-api.greenhouse.io/v1/boards/stripe/jobs/{job_id}"

    try:
        with urllib.request.urlopen(job_url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return ""

    content_parts = []

    # Greenhouse structure: sections → text/html
    for section in payload.get("content", []):
        text = section.get("text")
        if text:
            content_parts.append(text)

    # Minimal normalization: join blocks, strip whitespace
    return "\n\n".join(content_parts).strip()

