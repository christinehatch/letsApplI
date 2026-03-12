from __future__ import annotations

from collections import Counter
from typing import Any


def compute_market_alignment(
    jobs: list[dict[str, Any]],
    resume_signals: list[str],
) -> dict[str, int]:
    """
    Count how many jobs match each resume signal.

    - Reads job["signals"] as a list of strings.
    - Increments only for signals present in resume_signals.
    - Ignores jobs with missing/invalid signals.
    """
    normalized_resume = [str(signal).strip().lower() for signal in resume_signals if str(signal).strip()]
    if not normalized_resume:
        return {}

    resume_set = set(normalized_resume)
    counts: Counter[str] = Counter()

    for job in jobs:
        raw_signals = job.get("signals")
        if not isinstance(raw_signals, list):
            continue

        job_signals = {
            str(signal).strip().lower()
            for signal in raw_signals
            if str(signal).strip()
        }
        for signal in job_signals:
            if signal in resume_set:
                counts[signal] += 1

    return dict(counts)
