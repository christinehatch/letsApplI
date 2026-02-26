from .errors import Phase52ValidationError


def _validate_span_list(span_list, context: str):
    if not isinstance(span_list, list) or len(span_list) == 0:
        raise Phase52ValidationError(
            reason_code="GROUNDING_VIOLATION",
            violation_detail=f"Empty or invalid evidence_span_ids in {context}",
        )


def validate_grounding(output: dict, raw_content: str) -> None:
    # RoleSummary
    role_summary = output.get("RoleSummary", {})
    _validate_span_list(role_summary.get("evidence_span_ids", []), "RoleSummary")

    # CapabilityEmphasisSignals
    for idx, item in enumerate(output.get("CapabilityEmphasisSignals", [])):
        _validate_span_list(
            item.get("evidence_span_ids", []),
            f"CapabilityEmphasisSignals[{idx}]",
        )

    # ProjectOpportunitySignals
    for idx, item in enumerate(output.get("ProjectOpportunitySignals", [])):
        _validate_span_list(
            item.get("evidence_span_ids", []),
            f"ProjectOpportunitySignals[{idx}]",
        )
