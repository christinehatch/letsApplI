from __future__ import annotations


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def score_ai_relevance(interpretation: dict) -> dict:
    capability_terms = ("genai", "ai", "machine learning")
    requirement_terms = (
        "llm",
        "rag",
        "embeddings",
        "vector database",
        "prompt engineering",
    )
    role_summary_terms = ("ai-powered", "conversational ai", "intelligent systems")

    score = 0.0
    signals: list[str] = []
    description_parts: list[str] = []

    capabilities = interpretation.get("CapabilityEmphasisSignals", [])
    capability_blob = " ".join(
        f"{item.get('domain_label', '')} {item.get('description', '')}"
        for item in capabilities
        if isinstance(item, dict)
    )
    if _contains_any(capability_blob, capability_terms):
        score += 0.4
        signals.append("Capability signals indicate AI/ML emphasis")
        description_parts.append(
            "the role emphasizes AI/ML platform or product capabilities"
        )

    requirements = (
        interpretation.get("RequirementsAnalysis", {}).get("explicit_requirements", [])
    )
    requirements_blob = " ".join(
        item.get("requirement_text", "")
        for item in requirements
        if isinstance(item, dict)
    )
    if _contains_any(requirements_blob, requirement_terms):
        score += 0.3
        signals.append("Requirements reference LLM/RAG/embeddings tooling")
        description_parts.append(
            "the job requires experience with modern AI or LLM tooling"
        )

    role_summary_text = (
        interpretation.get("RoleSummary", {}).get("summary_text", "")
        if isinstance(interpretation.get("RoleSummary", {}), dict)
        else ""
    )
    if _contains_any(role_summary_text, role_summary_terms):
        score += 0.2
        signals.append("Role summary references AI-powered or intelligent systems")
        description_parts.append(
            "the role description references AI-powered systems or intelligent products"
        )

    score = min(score, 1.0)

    if score >= 0.75:
        level = "HIGH"
    elif score >= 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"

    if not description_parts:
        description = "No clear AI-related signals were detected in the role interpretation."
    else:
        description = "This role shows AI relevance because " + ", ".join(description_parts) + "."

    return {
        "ai_relevance_score": round(score, 4),
        "ai_relevance_level": level,
        "description": description,
        "signals": signals,
    }
