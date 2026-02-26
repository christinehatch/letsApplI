from .errors import Phase52ValidationError

FORBIDDEN_ACTOR_TERMS = [
    "you ",
    "your ",
    "candidate",
    "applicant",
]

def validate_actor_model(output: dict) -> None:
    serialized = str(output).lower()

    for term in FORBIDDEN_ACTOR_TERMS:
        if term in serialized:
            raise Phase52ValidationError(
                reason_code="ACTOR_VIOLATION",
                violation_detail=f"Actor shift detected: '{term}'",
                raw_excerpt=term,
            )
