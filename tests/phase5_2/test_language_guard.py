import pytest
from src.phase5.phase5_2.validator_pipeline import validate_phase52_output
from src.phase5.phase5_2.errors import Phase52ValidationError


def base_valid_output():
    return {
        "schema_version": "5.2.0",
        "RoleSummary": {
            "summary_text": "Engineers in the role build distributed systems.",
            "evidence_span_ids": ["span_1"]
        },
        "RequirementsAnalysis": {
            "explicit_requirements": [],
            "implicit_signals": []
        },
        "CapabilityEmphasisSignals": [
            {
                "domain_label": "Distributed Systems",
                "description": "Engineers in the role work on scaling systems.",
                "evidence_span_ids": ["span_1"]
            }
        ],
        "ProjectOpportunitySignals": [],
        "InterpretationResult": {
            "structural_notes": "Test"
        },
        "confidence": "LOW"
    }


def test_reject_second_person_language():
    output = base_valid_output()
    output["RoleSummary"]["summary_text"] = "You will build distributed systems."

    with pytest.raises(Phase52ValidationError):
        validate_phase52_output(output, "RAW JOB CONTENT")
def test_reject_you_should_language():
    output = base_valid_output()
    output["CapabilityEmphasisSignals"][0]["description"] = \
        "You should demonstrate distributed systems experience."

    with pytest.raises(Phase52ValidationError):
        validate_phase52_output(output, "RAW JOB CONTENT")

def test_reject_fit_language():
    output = base_valid_output()
    output["InterpretationResult"]["structural_notes"] = \
        "A strong candidate would likely excel in this role."

    with pytest.raises(Phase52ValidationError):
        validate_phase52_output(output, "RAW JOB CONTENT")
