from scoring.ai_relevance_explainer import generate_ai_relevance_explanation


def test_explanation_uses_capability_and_project_signals_with_dedup():
    interpretation = {
        "CapabilityEmphasisSignals": [
            {"domain_label": "GenAI Product Development"},
            {"domain_label": "LLM Experience"},
            {"domain_label": "GenAI Product Development"},
        ],
        "ProjectOpportunitySignals": [
            {"capability_surface": "AI-powered customer workflows"},
            {"capability_surface": "LLM Experience"},
        ],
    }

    result = generate_ai_relevance_explanation(interpretation, 0.81)

    assert result["level"] == "High"
    assert result["signals"] == [
        "GenAI Product Development",
        "LLM Experience",
        "AI-powered customer workflows",
    ]


def test_explanation_level_thresholds():
    interpretation = {"CapabilityEmphasisSignals": [], "ProjectOpportunitySignals": []}

    assert generate_ai_relevance_explanation(interpretation, 0.75)["level"] == "High"
    assert generate_ai_relevance_explanation(interpretation, 0.40)["level"] == "Moderate"
    assert generate_ai_relevance_explanation(interpretation, 0.39)["level"] == "Low"
