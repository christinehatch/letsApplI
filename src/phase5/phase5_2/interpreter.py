from typing import Optional
from datetime import datetime

from .types import InterpretationInput, InterpretationResult
from .errors import (
    InterpretationNotAuthorizedError,
    InvalidInputSourceError,
)


class Phase52Interpreter:
    """
    Phase 5.2 Interpreter — Interpretation Only

    This class is responsible for interpreting content
    that has already been read in Phase 5.1.

    IMPORTANT:
    - This class performs NO reading
    - This class performs NO fetching
    - This class performs NO persistence
    - This class performs NO recommendation
    """

    def __init__(self):
        self._input: Optional[InterpretationInput] = None

    # -------------------------
    # Input lifecycle
    # -------------------------

    def set_input(self, input_payload: InterpretationInput) -> None:
        """
        Attach Phase 5.1-derived input.

        Validation is enforced at interpret-time,
        not here.
        """
        self._input = input_payload

    # -------------------------
    # Interpretation entrypoint
    # -------------------------

    def interpret(self) -> InterpretationResult:
        # ---- Input Guard Checks (Keep your existing guards) ----
        if self._input is None:
            raise InterpretationNotAuthorizedError("No Phase 5.1 input provided")

        if not self._input.raw_content:
            raise InvalidInputSourceError("Empty content cannot be interpreted")

        if self._input.read_at is None:
            raise InvalidInputSourceError("Interpretation requires a Phase 5.1 read timestamp")

        # ---- THE HAPPY PATH IMPLEMENTATION ----

        # 1. Extraction Logic: Identify bullet points or action-oriented lines
            # ---- Interpretation Logic ----
        lines = self._input.raw_content.split('\n')
        extracted_reqs = []

        for line in lines:
            clean = line.strip()
            if clean.startswith(('•', '-', '*', '●')) or any(
                    kw in clean.lower() for kw in ['experience', 'proficient']):
                extracted_reqs.append(clean.lstrip('•-* ●').strip())

        # ---- Build Result according to your Phase 5.2 types ----
        return InterpretationResult(
            job_id=self._input.job_id,
            interpreted_at=datetime.now(),
            source_read_at=self._input.read_at,
            artifacts={
                "requirements": extracted_reqs,
                "context_signals": ["Stripe Greenhouse Source"]
            },
            confidence="high",
            limitations=[]
        )
    # -------------------------
    # Internal helpers (stubs)
    # -------------------------

    def _validate_input(self) -> None:
        raise NotImplementedError

    def _interpret_content(self) -> None:
        raise NotImplementedError

    def _build_result(self) -> InterpretationResult:
        raise NotImplementedError

