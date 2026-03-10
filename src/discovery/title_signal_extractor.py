from __future__ import annotations

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


def extract_title_signals(title: str) -> list[str]:
    lower = title.lower()
    signals: list[str] = []

    for keyword, signal in SIGNAL_KEYWORDS:
        if keyword in lower and signal not in signals:
            signals.append(signal)

    if "senior" in lower:
        signals.append("senior")

    return signals
