"""
Phase 5.2 LLM adapter.

This module is the generation boundary for structured interpretation.
It is responsible for:
- invoking the LLM deterministically
- validating output before returning
- retrying once with explicit correction instructions
- failing closed with a Phase52ValidationError when output remains invalid
"""

import json

from src.llm.adapter import LLMAdapter, LLMAdapterError
from .validator_pipeline import validate_phase52_output
from .errors import Phase52ValidationError


class Phase52LLMAdapter:
    """
    Strict Phase 5.2 LLM adapter.

    Contract:
    - Deterministic generation (temperature=0)
    - JSON-only output contract
    - Validation before returning
    - Single corrective retry on validation failure
    - Fail closed if still invalid
    """

    def __init__(self):
        self._llm = LLMAdapter()

    def run(self, raw_content: str) -> dict:
        """
        Generate and validate Phase 5.2 output.

        Retry policy:
        - Attempt 1: generate + validate.
        - If validation fails, issue one corrective retry using the same
          source content plus validation feedback.
        - Attempt 2: generate + validate.
        - If still invalid, raise Phase52ValidationError with raw_excerpt.
        """
        system_prompt = self._build_system_prompt()
        user_prompt = raw_content

        for attempt in (1, 2):
            try:
                parsed = self._llm.generate_structured(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=0.0,   # enforce determinism
                    max_tokens=1500,
                )
            except LLMAdapterError as e:
                raise Phase52ValidationError(
                    reason_code="LLM_RUNTIME_FAILURE",
                    violation_detail=str(e),
                )

            # Validation is authoritative: nothing returns unless it passes.
            try:
                validate_phase52_output(parsed, raw_content)
                return parsed
            except Phase52ValidationError as e:
                raw_excerpt = json.dumps(parsed, ensure_ascii=False)
                if attempt == 1:
                    # Retry once with explicit correction instructions.
                    correction = self._build_retry_instruction(e)
                    user_prompt = (
                        f"{raw_content}\n\n"
                        "The previous response failed validation.\n"
                        f"Validation error: {e.reason_code}: {e.violation_detail}\n"
                        f"{correction}\n"
                        "Return corrected JSON only."
                    )
                    continue
                raise Phase52ValidationError(
                    reason_code=e.reason_code,
                    violation_detail=e.violation_detail,
                    raw_excerpt=raw_excerpt,
                ) from e
            except Exception as e:
                raw_excerpt = json.dumps(parsed, ensure_ascii=False)
                if attempt == 1:
                    # Unknown validation/runtime path: retry once with context.
                    user_prompt = (
                        f"{raw_content}\n\n"
                        "The previous response failed validation.\n"
                        f"Validation error: {str(e)}\n"
                        "Return corrected JSON only."
                    )
                    continue
                raise Phase52ValidationError(
                    reason_code="VALIDATION_FAILURE",
                    violation_detail=str(e),
                    raw_excerpt=raw_excerpt,
                ) from e

        raise Phase52ValidationError(
            reason_code="VALIDATION_FAILURE",
            violation_detail="Interpretation failed after retry",
        )

    @staticmethod
    def _build_retry_instruction(error: Phase52ValidationError) -> str:
        """
        Produce targeted correction guidance based on validator reason code.
        """
        if error.reason_code == "ACTOR_VIOLATION":
            return (
                "The previous response violated actor neutrality.\n"
                "Rewrite the interpretation so it analyzes the job posting "
                "without evaluating the candidate."
            )
        if error.reason_code == "LANGUAGE_VIOLATION":
            return (
                "The previous response used disallowed advisory language.\n"
                "Rewrite with neutral, descriptive phrasing only."
            )
        if error.reason_code == "SCHEMA_VIOLATION":
            return (
                "The previous response violated schema constraints.\n"
                "Rewrite to match the required JSON schema exactly."
            )
        if error.reason_code == "GROUNDING_VIOLATION":
            return (
                "The previous response lacked valid evidence grounding.\n"
                "Rewrite with valid evidence span IDs for grounded claims."
            )
        return "Rewrite the output so it passes all validation rules."

    def _build_system_prompt(self) -> str:
        """
        Build the Phase 5.2 system prompt.

        The prompt encodes behavioral constraints and the required JSON shape.
        """
        return """
    SYSTEM RULES

    You are a neutral job-structure interpreter.

    Your task is to analyze job postings and describe the structure of the role.

    You MUST NOT:

    - evaluate a candidate
    - infer candidate fit
    - give career advice
    - recommend actions
    - address the reader
    - use second-person language ("you", "your")

    All statements must refer to the ROLE, not to a person.

    If a sentence begins to evaluate a candidate or provide advice,
    rewrite the sentence so that it describes the role instead.

    Your output must remain strictly analytical and role-focused.

    --------------------------------------------------

    TASK

    You are a structured analytical interpreter operating inside a consent-gated reasoning system.

    You are participating in Phase 5.2 of a multi-phase architecture.

    ROLE REALITY

    Explain what the person in this role actually does.

    Describe:
    - the problems the role owns
    - the systems or functions they manage
    - who they work with
    - what success in the role looks like

    Write 4–6 sentences summarizing the day-to-day work of the role.

    Do NOT evaluate a candidate.
    Describe the role only.

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
