
import pytest
from datetime import datetime, timezone

from src.phase5.phase5_2.interpreter import Phase52Interpreter
from src.phase5.phase5_2.types import InterpretationInput
from src.phase5.phase5_2.errors import InvalidInputSourceError


def test_interpreter_rejects_empty_content():
    """
    INV-5.2-INPUT-001
    Interpretation requires actual content.
    """
    interpreter = Phase52Interpreter()

    bad_input = InterpretationInput(
        job_id="job-123",
        raw_content="",
        read_at=datetime.now(timezone.utc),
    )

    interpreter.set_input(bad_input)

    with pytest.raises(InvalidInputSourceError):
        interpreter.interpret()


def test_interpreter_requires_read_timestamp():
    """
    INV-5.2-INPUT-002
    Interpretation must be traceable to a Phase 5.1 read.
    """
    interpreter = Phase52Interpreter()

    bad_input = InterpretationInput(
        job_id="job-123",
        raw_content="RAW JOB CONTENT",
        read_at=None,  # type: ignore
    )

    interpreter.set_input(bad_input)

    with pytest.raises(InvalidInputSourceError):
        interpreter.interpret()


def test_interpreter_does_not_emit_advice_or_recommendations():
    """
    INV-5.2-GUARD-004
    Phase 5.2 must not provide advice, fit, or recommendations.
    """
    interpreter = Phase52Interpreter()

    input_payload = InterpretationInput(
        job_id="job-123",
        raw_content="RAW JOB CONTENT",
        read_at=datetime.now(timezone.utc),
    )

    interpreter.set_input(input_payload)

    result = interpreter.interpret()
    assert "recommend" not in str(result).lower()
    assert "should" not in str(result).lower()
    # If this ever returns, these must never appear
    forbidden_language = [
        "you should",
        "recommend",
        "fit",
        "good match",
        "apply",
    ]

    serialized = str(result).lower()
    for phrase in forbidden_language:
        assert phrase not in serialized
