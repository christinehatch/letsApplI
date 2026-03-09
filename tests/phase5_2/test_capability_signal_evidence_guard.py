from src.phase5.phase5_2.llm_adapter import Phase52LLMAdapter


def test_drop_empty_capability_signal_evidence_removes_only_empty_entries():
    parsed = {
        "CapabilityEmphasisSignals": [
            {
                "domain_label": "AI Systems",
                "description": "Mentions LLM systems",
                "evidence_span_ids": [],
            },
            {
                "domain_label": "Backend",
                "description": "Mentions APIs",
                "evidence_span_ids": ["span_4"],
            },
        ]
    }

    Phase52LLMAdapter._drop_empty_capability_signal_evidence(parsed)

    assert len(parsed["CapabilityEmphasisSignals"]) == 1
    assert parsed["CapabilityEmphasisSignals"][0]["domain_label"] == "Backend"
