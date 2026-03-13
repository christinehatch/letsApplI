def generate_ai_relevance_explanation(interpretation: dict, score: float):
    signals = []

    capabilities = interpretation.get("CapabilityEmphasisSignals", [])
    projects = interpretation.get("ProjectOpportunitySignals", [])

    for capability in capabilities:
        label = capability.get("domain_label")
        if label:
            signals.append(label)

    for project in projects:
        label = project.get("capability_surface")
        if label:
            signals.append(label)

    signals = list(dict.fromkeys(signals))[:5]

    if score >= 0.75:
        level = "High"
    elif score >= 0.4:
        level = "Moderate"
    else:
        level = "Low"

    return {
        "level": level,
        "signals": signals,
    }
