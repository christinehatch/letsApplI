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
from typing import Optional

from src.llm.adapter import LLMAdapter, LLMAdapterError
from .span_indexer import build_spans, format_span_prompt
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

    def run(self, raw_content: str, spans: Optional[list[dict]] = None) -> dict:
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
        base_prompt = self._build_user_prompt(raw_content, spans=spans)
        user_prompt = base_prompt

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

            print("\n\n===== RAW LLM OUTPUT =====")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
            print("==========================\n\n")

            self._drop_empty_capability_signal_evidence(parsed)
            print("\n\n===== POST CLEANUP OUTPUT =====")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
            print("===============================\n\n")

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
                        f"{base_prompt}\n\n"
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
                        f"{base_prompt}\n\n"
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
    def _build_user_prompt(raw_content: str, spans: Optional[list[dict]] = None) -> str:
        spans = spans if spans is not None else build_spans(raw_content)
        span_section = format_span_prompt(spans)
        return (
            "The following job posting has been segmented into spans.\n\n"
            f"{span_section}\n\n"
            "Use these span IDs when referencing evidence.\n\n"
            "Job Content:\n"
            f"{raw_content}"
        )

    @staticmethod
    def _drop_empty_capability_signal_evidence(parsed: dict) -> None:
        signals = parsed.get("CapabilityEmphasisSignals")
        if not isinstance(signals, list):
            return

        parsed["CapabilityEmphasisSignals"] = [
            s
            for s in signals
            if not isinstance(s, dict) or s.get("evidence_span_ids")
        ]

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

    ROLE INTERPRETATION RULES

    Your task is to explain what a person working in this role would
    generally be responsible for.

    Interpret the role using evidence from the job posting.

    Focus on:
    - day-to-day responsibilities
    - decisions the role likely makes
    - systems, products, or domains the role interacts with
    - the type of work environment implied by the posting
    - the stakeholders the role collaborates with

    You may synthesize responsibilities from multiple spans of evidence.

    Responsibilities do NOT need to appear as explicit bullet points in
    the job posting.

    However, every claim must be grounded in evidence spans.

    ROLE SUMMARY EXPECTATION

    The RoleSummary must describe the real nature of the role.

    It should answer:

    "What would someone in this role actually spend their time doing?"

    Avoid simply repeating requirement bullets.

    Instead explain the responsibilities implied by the posting.

    Example transformation:

    Input text:

    "Drive sales into BFSI enterprise accounts"

    Good RoleSummary statement:

    "This role focuses on building relationships with large financial
    sector organizations and managing complex enterprise sales cycles
    for Cloudflare's networking and security products."

    CAPABILITY SIGNAL GUIDANCE

    CapabilityEmphasisSignals should describe the types of work the role
    emphasizes.

    Examples:
    - Enterprise Account Sales
    - Network Security Solution Selling
    - Complex B2B Sales Cycles
    - Enterprise Relationship Management

    Descriptions should explain why the capability matters in this role.

    GROUNDING REQUIREMENT

    Every claim must reference evidence_span_ids.

    Signals may reference multiple spans.

    Example:

    "evidence_span_ids": ["span_3","span_8"]

    STRICT LIMITS

    Do NOT:
    - evaluate a candidate
    - give career advice
    - recommend actions
    - speculate beyond the job text

    Interpret the role, not the candidate.

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
    - Evidence spans are provided above.
    - Every evidence_span_ids entry MUST reference one of the provided span IDs.
    - Never invent span IDs.
    - If a claim cannot reference a valid span, omit the claim.
    - If uncertain, omit rather than speculate.
    """
