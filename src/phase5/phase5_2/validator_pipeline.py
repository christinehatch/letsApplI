from .validator_schema import validate_schema
from .validator_language import validate_language_constraints
from .validator_actor import validate_actor_model
from .validator_grounding import validate_grounding
from .determinism import compute_structural_hash


def validate_phase52_output(output: dict, raw_content: str) -> str:
    validate_schema(output)
    validate_language_constraints(output)
    validate_actor_model(output)
    validate_grounding(output, raw_content)

    structural_hash = compute_structural_hash(output)
    return structural_hash
