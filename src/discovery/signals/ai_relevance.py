from __future__ import annotations

import re
from typing import Any

CATEGORY_TERMS: dict[str, tuple[str, ...]] = {
    "direct_ai_language": (
        "llm",
        "large language model",
        "generative ai",
        "machine learning",
        "artificial intelligence",
        "prompt engineering",
        "rag",
        "fine-tuning",
        "embeddings",
        "inference",
        "model evaluation",
        "agent",
        "agents",
        "ai assistant",
        "copilot",
    ),
    "ai_infrastructure": (
        "model serving",
        "ml infrastructure",
        "feature store",
        "vector database",
        "evaluation pipeline",
        "inference platform",
        "training pipeline",
        "model observability",
        "retrieval system",
    ),
    "ai_product": (
        "ai product",
        "conversational system",
        "conversational interface",
        "human-in-the-loop",
        "trust and safety",
        "model behavior",
        "ai workflow",
        "applied ai",
        "ai ux",
    ),
    "weak_supporting_signals": (
        "python",
        "experimentation",
        "api platform",
        "analytics",
        "distributed systems",
        "data pipeline",
    ),
}

CATEGORY_WEIGHTS: dict[str, int] = {
    "direct_ai_language": 5,
    "ai_infrastructure": 3,
    "ai_product": 3,
    "weak_supporting_signals": 1,
}

CATEGORY_ORDER = (
    "direct_ai_language",
    "ai_infrastructure",
    "ai_product",
    "weak_supporting_signals",
)

SCORE_CAP = 15.0


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _contains_term(haystack: str, term: str) -> bool:
    pattern = r"\b" + re.escape(term).replace(r"\ ", r"\s+") + r"\b"
    return re.search(pattern, haystack) is not None


def _collect_metadata_strings(value: Any) -> list[str]:
    out: list[str] = []

    if value is None:
        return out

    if isinstance(value, str):
        stripped = value.strip()
        if stripped:
            out.append(stripped)
        return out

    if isinstance(value, dict):
        for item in value.values():
            out.extend(_collect_metadata_strings(item))
        return out

    if isinstance(value, (list, tuple, set)):
        for item in value:
            out.extend(_collect_metadata_strings(item))
        return out

    return out


def compute_ai_relevance(
    title: str,
    description: str | None,
    metadata: dict | None = None,
    tags: list[str] | None = None,
) -> dict:
    """
    Deterministic AI relevance signal extractor.

    Uses explicit keyword evidence only from provided fields.
    """

    parts: list[str] = []
    if title:
        parts.append(title)
    if description:
        parts.append(description)
    if tags:
        parts.extend([t for t in tags if isinstance(t, str) and t.strip()])
    if metadata:
        parts.extend(_collect_metadata_strings(metadata))

    corpus = _normalize("\n".join(parts))

    matches_by_category: dict[str, list[str]] = {}

    for category in CATEGORY_ORDER:
        terms = CATEGORY_TERMS[category]
        matched = sorted({term for term in terms if _contains_term(corpus, term)})
        if matched:
            matches_by_category[category] = matched

    raw_score = 0
    for category, matches in matches_by_category.items():
        raw_score += CATEGORY_WEIGHTS[category] * len(matches)

    score = min(raw_score / SCORE_CAP, 1.0)

    categories = [c for c in CATEGORY_ORDER if c in matches_by_category]

    reasons = [
        f"Matched {category}: {', '.join(matches_by_category[category])}"
        for category in categories
    ]

    all_matches: list[str] = []
    for category in categories:
        all_matches.extend(matches_by_category[category])

    return {
        "ai_relevance_score": round(score, 4),
        "ai_signal_categories": categories,
        "ai_signal_reasons": reasons,
        "ai_signal_matches": all_matches,
    }
