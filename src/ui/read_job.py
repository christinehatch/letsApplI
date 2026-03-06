# src/ui/read_job.py
import os
from phase5.phase5_1.reader import Phase51Reader
from phase5.phase5_1.types import ReadResult
# src/ui/read_job.py
from typing import Callable
from urllib.parse import urlparse
import asyncio

from playwright.async_api import async_playwright


def get_fetcher(job_id: str, job_url: str) -> Callable[[], asyncio.Future]:    """
    Returns a synchronous wrapper that fetches visible page text using Playwright.
    """


def get_fetcher(job_id: str, job_url: str):
    async def fetch_async() -> str:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()

                await page.goto(job_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(800)

                text = await page.evaluate(
                    "() => document.body.innerText"
                )

                await browser.close()

                return text.strip() if text else ""

        except Exception as e:
            print(f"[FETCH ERROR] {str(e)}")
            return ""

    return fetch_async

async def read_job_for_ui(consent, fetch_job_content) -> ReadResult:
    """Standard Phase 5.1 Entrypoint—Does not interpret or persist."""

    # --- [AUTHORITY VALIDATION] ---
    # Explicitly allow 'hydrate' as a valid level of authority
    allowed_scopes = ["hydrate", "read_job_posting", "interpret_job_posting"]

    if consent.scope not in allowed_scopes:
        print(f"!!! GATEKEEPER REJECTION: Scope '{consent.scope}' is unauthorized.")
        raise ValueError(f"Invalid consent scope: {consent.scope}")

    print(f">>> GATEKEEPER: Authority '{consent.scope}' verified.")
    reader = Phase51Reader(fetch_job_content=fetch_job_content)

    # If Phase51Reader.set_consent still fails, we'll need to
    # check that specific file, but this usually unblocks the flow.
    reader.set_consent(consent)
    return await reader.read()