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
        # ---- Input must exist ----
        if self._input is None:
            raise InterpretationNotAuthorizedError(
                "No Phase 5.1 input provided"
            )

        # ---- Content must be present ----
        if not self._input.raw_content:
            raise InvalidInputSourceError(
                "Empty content cannot be interpreted"
            )

        # ---- Read timestamp must exist ----
        if self._input.read_at is None:
            raise InvalidInputSourceError(
                "Interpretation requires a Phase 5.1 read timestamp"
            )

        # ---- Stop here (happy path intentionally unimplemented) ----
        raise NotImplementedError(
            "Phase 5.2 interpretation happy-path not yet implemented"
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

