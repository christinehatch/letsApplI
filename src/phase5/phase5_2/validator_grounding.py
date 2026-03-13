from .errors import Phase52ValidationError
from .span_indexer import build_spans


def _validate_span_list(span_list, context: str):
    if not isinstance(span_list, list) or len(span_list) == 0:
        raise Phase52ValidationError(
            reason_code="GROUNDING_VIOLATION",
            violation_detail=f"Empty or invalid evidence_span_ids in {context}",
        )


def _validate_span_ids_exist(span_list, valid_span_ids: set[str], context: str) -> None:
    for span_id in span_list:
        if not isinstance(span_id, str) or not span_id.strip():
            raise Phase52ValidationError(
                reason_code="GROUNDING_VIOLATION",
                violation_detail=f"Invalid span id in {context}",
                raw_excerpt=str(span_id),
            )
        if span_id not in valid_span_ids:
            raise Phase52ValidationError(
                reason_code="GROUNDING_VIOLATION",
                violation_detail=f"Unknown span id '{span_id}' in {context}",
                raw_excerpt=span_id,
            )


def validate_grounding(output: dict, raw_content: str) -> None:
    valid_span_ids = {span["span_id"] for span in build_spans(raw_content)}
    if not valid_span_ids:
        raise Phase52ValidationError(
            reason_code="GROUNDING_VIOLATION",
            violation_detail="No valid span ids available for grounding validation",
        )

    # RoleSummary
    role_summary = output.get("RoleSummary", {})
    role_summary_spans = role_summary.get("evidence_span_ids", [])
    _validate_span_list(role_summary_spans, "RoleSummary")
    _validate_span_ids_exist(role_summary_spans, valid_span_ids, "RoleSummary")

    # RequirementsAnalysis
    requirements = output.get("RequirementsAnalysis", {})
    explicit_requirements = requirements.get("explicit_requirements", [])
    if isinstance(explicit_requirements, list):
        for idx, item in enumerate(explicit_requirements):
            if not isinstance(item, dict):
                continue
            requirement_text = item.get("requirement_text")
            if isinstance(requirement_text, str) and requirement_text.strip():
                source_span_id = item.get("source_span_id")
                if not isinstance(source_span_id, str) or not source_span_id.strip():
                    raise Phase52ValidationError(
                        reason_code="GROUNDING_VIOLATION",
                        violation_detail=(
                            f"Missing source_span_id for explicit requirement "
                            f"at index {idx}"
                        ),
                    )
                if source_span_id not in valid_span_ids:
                    raise Phase52ValidationError(
                        reason_code="GROUNDING_VIOLATION",
                        violation_detail=(
                            f"Unknown source_span_id '{source_span_id}' in "
                            f"RequirementsAnalysis.explicit_requirements[{idx}]"
                        ),
                        raw_excerpt=source_span_id,
                    )

    implicit_signals = requirements.get("implicit_signals", [])
    if isinstance(implicit_signals, list):
        for idx, item in enumerate(implicit_signals):
            if not isinstance(item, dict):
                continue
            signal_text = item.get("signal_text")
            if isinstance(signal_text, str) and signal_text.strip():
                context = f"RequirementsAnalysis.implicit_signals[{idx}]"
                spans = item.get("evidence_span_ids", [])
                _validate_span_list(spans, context)
                _validate_span_ids_exist(spans, valid_span_ids, context)

    # CapabilityEmphasisSignals
    for idx, item in enumerate(output.get("CapabilityEmphasisSignals", [])):
        if not isinstance(item, dict):
            continue
        description = item.get("description")
        if isinstance(description, str) and description.strip():
            context = f"CapabilityEmphasisSignals[{idx}]"
            spans = item.get("evidence_span_ids", [])
            _validate_span_list(spans, context)
            _validate_span_ids_exist(spans, valid_span_ids, context)

    # ProjectOpportunitySignals
    for idx, item in enumerate(output.get("ProjectOpportunitySignals", [])):
        if not isinstance(item, dict):
            continue
        description = item.get("description")
        if isinstance(description, str) and description.strip():
            context = f"ProjectOpportunitySignals[{idx}]"
            spans = item.get("evidence_span_ids", [])
            _validate_span_list(spans, context)
            _validate_span_ids_exist(spans, valid_span_ids, context)
