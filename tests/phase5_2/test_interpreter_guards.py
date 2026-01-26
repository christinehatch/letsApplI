
import pytest
from datetime import datetime, timezone

from src.phase5.phase5_2.interpreter import Phase52Interpreter
from src.phase5.phase5_2.types import InterpretationInput
from src.phase5.phase5_2.errors import (
    InterpretationNotAuthorizedError,
    InvalidInputSourceError,
)


def test_interpret_without_input_raises():
    """
    INV-5.2-GUARD-001
    Interpretation must not run without Phase 5.1 input.
    """
    interpreter = Phase52Interpreter()

    with pytest.raises(InterpretationNotAuthorizedError):
        interpreter.interpret()


def test_interpret_does_not_perform_reading_or_fetching():
    """
    INV-5.2-GUARD-002
    Phase 5.2 must not read, fetch, or access external sources.
    """
    interpreter = Phase52Interpreter()

    input_payload = InterpretationInput(
        job_id="job-123",
        raw_content="RAW JOB CONTENT",
        read_at=datetime.now(timezone.utc),
    )

    interpreter.set_input(input_payload)

    # We expect NotImplementedError for now,
    # but *not* any fetch/read side effects.
    with pytest.raises(NotImplementedError):
        interpreter.interpret()


def test_interpreter_has_no_fetch_or_read_methods():
    """
    INV-5.2-GUARD-003
    Interpreter must not expose fetch/read APIs.
    """
    interpreter = Phase52Interpreter()

    forbidden_methods = [
        "read",
        "fetch",
        "fetch_job_content",
        "read_job",
    ]

    for method in forbidden_methods:
        assert not hasattr(interpreter, method), f"Forbidden method exposed: {method}"
