from typing import Optional
from datetime import datetime

from .types import (
    InterpretationInput,
    InterpretationResult,
    RoleSummary,
    RequirementsAnalysis,
    ResumeAlignment,
    ProjectOpportunities,
)
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
    - This class performs NO recommendation (strategic inference will come later)
    """

    def __init__(self):
        self._input: Optional[InterpretationInput] = None

    # -------------------------
    # Input lifecycle
    # -------------------------

    def set_input(self, input_payload: InterpretationInput) -> None:
        self._input = input_payload

    # -------------------------
    # Interpretation entrypoint
    # -------------------------

    def interpret(self) -> InterpretationResult:
        # ---- Guard Checks ----
        if self._input is None:
            raise InterpretationNotAuthorizedError("No Phase 5.1 input provided")

        if not self._input.raw_content:
            raise InvalidInputSourceError("Empty content cannot be interpreted")

        if self._input.read_at is None:
            raise InvalidInputSourceError(
                "Interpretation requires a Phase 5.1 read timestamp"
            )

        # ---- Hard Lock ----
        raise NotImplementedError("Phase 5.2 is locked (hardening mode)")