import pytest

from src.phase5.phase5_2.validator_actor import validate_actor_model
from src.phase5.phase5_2.validator_schema import Phase52ValidationError


def test_actor_validator_allows_neutral_second_person_job_language():
    payload = {
        "RoleSummary": {
            "summary_text": "You will build backend systems for financial trading platforms."
        },
        "RequirementsAnalysis": {
            "explicit_requirements": [
                {
                    "requirement_text": "You have at least 2+ years of experience in software engineering.",
                    "modality": "required",
                    "source_span_id": "span_1",
                }
            ],
            "implicit_signals": [],
        },
        "CapabilityEmphasisSignals": [],
        "ProjectOpportunitySignals": [],
        "InterpretationResult": {
            "structural_notes": "The role focuses on high availability backend infrastructure."
        },
    }

    validate_actor_model(payload)


def test_actor_validator_rejects_candidate_evaluation_language():
    payload = {
        "RoleSummary": {
            "summary_text": "You would be a good fit for this role."
        },
        "RequirementsAnalysis": {
            "explicit_requirements": [],
            "implicit_signals": [],
        },
        "CapabilityEmphasisSignals": [],
        "ProjectOpportunitySignals": [],
        "InterpretationResult": {
            "structural_notes": "The role involves backend engineering."
        },
    }

    with pytest.raises(Phase52ValidationError):
        validate_actor_model(payload)


def test_actor_validator_rejects_recommendation_language():
    payload = {
        "RoleSummary": {
            "summary_text": "You should apply if you enjoy working on distributed systems."
        },
        "RequirementsAnalysis": {
            "explicit_requirements": [],
            "implicit_signals": [],
        },
        "CapabilityEmphasisSignals": [],
        "ProjectOpportunitySignals": [],
        "InterpretationResult": {
            "structural_notes": "The role involves backend engineering."
        },
    }

    with pytest.raises(Phase52ValidationError):
        validate_actor_model(payload)
