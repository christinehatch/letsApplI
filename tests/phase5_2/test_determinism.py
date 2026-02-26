from src.phase5.phase5_2.interpreter import Phase52Interpreter
from src.phase5.phase5_2.types import InterpretationInput
from datetime import datetime, timezone


def test_structural_hash_stable():
    interpreter = Phase52Interpreter()

    input_payload = InterpretationInput(
        job_id="job-123",
        raw_content="RAW JOB CONTENT",
        read_at=datetime.now(timezone.utc),
    )

    interpreter.set_input(input_payload)

    result1 = interpreter.interpret()
    result2 = interpreter.interpret()

    assert result1 == result2
