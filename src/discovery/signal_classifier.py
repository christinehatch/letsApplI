"""Deterministic job signal classification using keyword rules."""

from __future__ import annotations


SIGNAL_RULES = {
    "ai": [
        "machine learning",
        "deep learning",
        "llm",
        "large language model",
        "pytorch",
        "tensorflow",
    ],
    "data": [
        "data pipeline",
        "etl",
        "spark",
        "analytics",
        "data platform",
    ],
    "backend": [
        "api",
        "microservices",
        "distributed systems",
        "backend services",
    ],
    "platform": [
        "developer platform",
        "internal tooling",
        "infrastructure platform",
        "platform engineering",
    ],
    "infra": [
        "kubernetes",
        "docker",
        "infrastructure",
        "observability",
        "cloud infrastructure",
    ],
}


def classify_job_signals(title: str, description_text: str) -> list[str]:
    """Return deterministic signals based on keyword presence."""
    combined = f"{title or ''} {description_text or ''}".lower()
    signals: list[str] = []

    for signal, keywords in SIGNAL_RULES.items():
        if any(keyword in combined for keyword in keywords):
            signals.append(signal)

    return list(dict.fromkeys(signals))


if __name__ == "__main__":
    from src.adapters.greenhouse_board_parser import parse_greenhouse_board

    jobs = parse_greenhouse_board("https://boards.greenhouse.io/datadog")

    for job in jobs[:10]:
        title = str(job.get("title", "")).strip()
        description_text = str(job.get("description_text", "")).strip()
        detected = classify_job_signals(title=title, description_text=description_text)

        print(title)
        print(detected)
        print()
