from src.llm.adapter import LLMAdapter, LLMAdapterError
from .validator_pipeline import validate_phase52_output
from .errors import Phase52ValidationError


class Phase52LLMAdapter:
    """
    Strict Phase 5.2 LLM Adapter.

    - Deterministic configuration
    - JSON-only expectation
    - Immediate validation
    - Fail-closed behavior
    """

    def __init__(self):
        self._llm = LLMAdapter()

    def run(self, raw_content: str) -> dict:
        system_prompt = self._build_system_prompt()

        try:
            parsed = self._llm.generate_structured(
                system_prompt=system_prompt,
                user_prompt=raw_content,
                temperature=0.0,   # enforce determinism
                max_tokens=1500,
            )
        except LLMAdapterError as e:
            raise Phase52ValidationError(
                reason_code="LLM_RUNTIME_FAILURE",
                violation_detail=str(e),
            )

        # Full structural + semantic validation
        validate_phase52_output(parsed, raw_content)

        return parsed

    def _build_system_prompt(self) -> str:
        return """
    You are a structured analytical interpreter operating inside a consent-gated reasoning system.

    You are participating in Phase 5.2 of a multi-phase architecture.

    You must produce structured JSON that EXACTLY matches the following schema.

    You must not add additional keys.
    You must not mirror raw job fields.
    You must not invent new top-level sections.

    The required output structure is:

    {
      "schema_version": "5.2.0",
      "RoleSummary": {
        "summary_text": "...",
        "evidence_span_ids": ["..."]
      },
      "RequirementsAnalysis": {
        "explicit_requirements": [
          {
            "requirement_text": "...",
            "modality": "required|preferred|optional",
            "source_span_id": "..."
          }
        ],
        "implicit_signals": [
          {
            "signal_text": "...",
            "evidence_span_ids": ["..."]
          }
        ]
      },
      "CapabilityEmphasisSignals": [
        {
          "domain_label": "...",
          "description": "...",
          "evidence_span_ids": ["..."]
        }
      ],
      "ProjectOpportunitySignals": [
        {
          "capability_surface": "...",
          "description": "...",
          "evidence_span_ids": ["..."]
        }
      ],
      "InterpretationResult": {
        "structural_notes": "..."
      },
      "confidence": "LOW|MEDIUM|HIGH"
    }

    Rules:

    - Return JSON only.
    - No commentary.
    - No prose outside JSON.
    - No markdown.
    - No explanation.
    - Do not include additional keys.
    - Do not include job metadata fields like title, company, or location.
    - Do not use second-person language.
    - Do not provide advice.
    - Do not evaluate candidate fit.
    - Remain grounded exclusively in the provided raw_content.
    - If uncertain, omit rather than speculate.
    """