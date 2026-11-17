from __future__ import annotations

import re

SIGNAL_KEYWORDS: list[tuple[str, str]] = [
    ("ai", "ai"),
    ("ai platform", "ai"),
    ("ai systems", "ai"),
    ("ai infrastructure", "ai"),
    ("ai research", "ai"),
    ("ai safety", "ai"),
    ("ai programs", "ai"),
    ("ai tooling", "ai"),
    ("ai engineer", "ai"),
    ("ai developer", "ai"),
    ("ai architect", "ai"),
    ("machine learning", "machine_learning"),
    ("ml", "ml"),
    ("genai", "genai"),
    ("llm", "llm"),
    ("software engineer", "backend"),
    ("backend", "backend"),
    ("frontend", "frontend"),
    ("platform", "platform"),
    ("data", "data"),
    ("product", "product"),
]


def _has_word(text: str, keyword: str) -> bool:
    # Whole words only: "ai" must not match "Campaigns", "ml" not "HTML".
    return re.search(r"(?<![a-z0-9])" + re.escape(keyword) + r"(?![a-z0-9])", text) is not None


def extract_title_signals(title: str) -> list[str]:
    lower = title.lower()
    signals: list[str] = []

    for keyword, signal in SIGNAL_KEYWORDS:
        if signal not in signals and _has_word(lower, keyword):
            signals.append(signal)

    if _has_word(lower, "senior"):
        signals.append("senior")

    return signals
