from typing import Optional
from datetime import datetime

from .types import InterpretationInput
from .errors import (
    InterpretationNotAuthorizedError,
    InvalidInputSourceError,
)
from .llm_adapter import Phase52LLMAdapter
from .span_indexer import build_spans
from .shadow_logger import log_shadow_run

class Phase52Interpreter:
    """
    Phase 5.2 Interpreter — Interpretation Only

    This class is responsible for interpreting content
    that has already been read in Phase 5.1.

    IMPORTANT:
    - This class performs NO reading
    - This class performs NO fetching
    - This class performs NO persistence
    - This class performs NO recommendation (strategic inference will come later)
    """


    def __init__(self):
        self._input: Optional[InterpretationInput] = None
        self._last_span_map: dict[str, str] = {}

    # -------------------------
    # Input lifecycle
    # -------------------------

    def set_input(self, input_payload: InterpretationInput) -> None:
        self._input = input_payload

    # -------------------------
    # Interpretation entrypoint
    # -------------------------
    def interpret(self) -> dict:
        # ---- Guard Checks ----
        if self._input is None:
            raise InterpretationNotAuthorizedError("No Phase 5.1 input provided")

        if not self._input.raw_content:
            raise InvalidInputSourceError("Empty content cannot be interpreted")

        if self._input.read_at is None:
            raise InvalidInputSourceError(
                "Interpretation requires a Phase 5.1 read timestamp"
            )

        # ---- Build final analysis text ----
        analysis_text = self._build_analysis_text(self._input.raw_content)

        # ---- LLM Execution (Authoritative) ----
        llm_adapter = Phase52LLMAdapter()
        spans = build_spans(analysis_text)
        self._last_span_map = {
            span["span_id"]: span["text"]
            for span in spans
        }

        # Hard guard: never proceed to validation with an empty span map.
        if not self._last_span_map:
            raise RuntimeError("Phase 5.2 span_map generation failed")

        output = llm_adapter.run(
            analysis_text,
            spans=spans,
            pre_validate_sanitizer=lambda parsed: self._sanitize_span_references(
                parsed, self._last_span_map
            ),
        )

        # ---- Structural Hash Logging ----
        log_shadow_run(self._input.job_id, output)

        return output

    def get_last_span_map(self) -> dict[str, str]:
        return dict(self._last_span_map)

    @staticmethod
    def _build_analysis_text(raw_content: str) -> str:
        # Single source of truth for interpretation input text.
        # Any future context augmentation should be applied here before span building.
        analysis_text = raw_content.strip()
        if not analysis_text:
            raise RuntimeError("Phase 5.2 received empty content")
        return analysis_text

    @staticmethod
    def _sanitize_span_references(output: dict, span_map: dict[str, str]) -> dict:
        valid_spans = set(span_map.keys())

        def filter_spans(span_list):
            if not isinstance(span_list, list):
                return span_list
            return [s for s in span_list if s in valid_spans]

        role_summary = output.get("RoleSummary")
        if isinstance(role_summary, dict):
            role_summary["evidence_span_ids"] = filter_spans(
                role_summary.get("evidence_span_ids", [])
            )

        requirements = output.get("RequirementsAnalysis")
        if isinstance(requirements, dict):
            explicit = requirements.get("explicit_requirements")
            if isinstance(explicit, list):
                sanitized_explicit = []
                for item in explicit:
                    if not isinstance(item, dict):
                        continue
                    source_span_id = item.get("source_span_id")
                    if source_span_id in valid_spans:
                        sanitized_explicit.append(item)
                requirements["explicit_requirements"] = sanitized_explicit

            implicit = requirements.get("implicit_signals")
            if isinstance(implicit, list):
                for item in implicit:
                    if not isinstance(item, dict):
                        continue
                    item["evidence_span_ids"] = filter_spans(item.get("evidence_span_ids", []))

        capability_signals = output.get("CapabilityEmphasisSignals")
        if isinstance(capability_signals, list):
            for item in capability_signals:
                if not isinstance(item, dict):
                    continue
                item["evidence_span_ids"] = filter_spans(item.get("evidence_span_ids", []))

        project_signals = output.get("ProjectOpportunitySignals")
        if isinstance(project_signals, list):
            for item in project_signals:
                if not isinstance(item, dict):
                    continue
                item["evidence_span_ids"] = filter_spans(item.get("evidence_span_ids", []))

        return output
