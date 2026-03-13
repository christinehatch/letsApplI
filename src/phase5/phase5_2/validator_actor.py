from .errors import Phase52ValidationError

DISALLOWED_EVALUATION_PHRASES = [
    "you would be a good fit",
    "you would succeed",
    "you might struggle",
    "this role matches your background",
    "this role suits you",
    "you should apply",
    "you are well suited",
    "this role is perfect for you",
]

def validate_actor_model(output: dict) -> None:
    text_fields: list[str] = []

    role_summary = output.get("RoleSummary", {})
    if isinstance(role_summary, dict):
        summary_text = role_summary.get("summary_text")
        if isinstance(summary_text, str):
            text_fields.append(summary_text)

    requirements = output.get("RequirementsAnalysis", {})
    if isinstance(requirements, dict):
        explicit = requirements.get("explicit_requirements", [])
        if isinstance(explicit, list):
            for item in explicit:
                if isinstance(item, dict):
                    requirement_text = item.get("requirement_text")
                    if isinstance(requirement_text, str):
                        text_fields.append(requirement_text)

        implicit = requirements.get("implicit_signals", [])
        if isinstance(implicit, list):
            for item in implicit:
                if isinstance(item, dict):
                    signal_text = item.get("signal_text")
                    if isinstance(signal_text, str):
                        text_fields.append(signal_text)

    capability_signals = output.get("CapabilityEmphasisSignals", [])
    if isinstance(capability_signals, list):
        for item in capability_signals:
            if isinstance(item, dict):
                description = item.get("description")
                if isinstance(description, str):
                    text_fields.append(description)

    project_signals = output.get("ProjectOpportunitySignals", [])
    if isinstance(project_signals, list):
        for item in project_signals:
            if isinstance(item, dict):
                description = item.get("description")
                if isinstance(description, str):
                    text_fields.append(description)

    interpretation_result = output.get("InterpretationResult", {})
    if isinstance(interpretation_result, dict):
        structural_notes = interpretation_result.get("structural_notes")
        if isinstance(structural_notes, str):
            text_fields.append(structural_notes)

    serialized = "\n".join(text_fields).lower()

    for phrase in DISALLOWED_EVALUATION_PHRASES:
        if phrase in serialized:
            raise Phase52ValidationError(
                reason_code="ACTOR_VIOLATION",
                violation_detail=f"Candidate-evaluative language detected: '{phrase}'",
                raw_excerpt=phrase,
            )
