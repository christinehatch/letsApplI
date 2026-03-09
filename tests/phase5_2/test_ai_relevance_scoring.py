from analysis.ai_relevance import score_ai_relevance


def test_score_ai_relevance_high_when_all_signal_groups_present():
    interpretation = {
        "RoleSummary": {
            "summary_text": "Build intelligent systems for AI-powered workflows."
        },
        "RequirementsAnalysis": {
            "explicit_requirements": [
                {"requirement_text": "Experience with LLM and RAG pipelines"}
            ]
        },
        "CapabilityEmphasisSignals": [
            {"domain_label": "Machine Learning Platform", "description": "AI systems"}
        ],
    }

    result = score_ai_relevance(interpretation)

    assert result["ai_relevance_score"] == 0.9
    assert result["ai_relevance_level"] == "HIGH"
    assert len(result["signals"]) == 3


def test_score_ai_relevance_medium_from_capability_only():
    interpretation = {
        "RoleSummary": {"summary_text": "Own backend services"},
        "RequirementsAnalysis": {"explicit_requirements": []},
        "CapabilityEmphasisSignals": [
            {"domain_label": "GenAI Product Development", "description": ""}
        ],
    }

    result = score_ai_relevance(interpretation)

    assert result["ai_relevance_score"] == 0.4
    assert result["ai_relevance_level"] == "MEDIUM"


def test_score_ai_relevance_low_for_empty_interpretation():
    result = score_ai_relevance({})

    assert result["ai_relevance_score"] == 0.0
    assert result["ai_relevance_level"] == "LOW"
    assert result["signals"] == []
