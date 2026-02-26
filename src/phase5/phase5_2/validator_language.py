from .errors import Phase52ValidationError

FORBIDDEN_LANGUAGE_PHRASES = [
    "you should",
    "should ",
    "recommend",
    "recommended",
    "apply ",
    "good fit",
    "strong fit",
    "likely",
    "unlikely",
    "competitive",
    "ideal candidate",
    "we suggest",
]

def validate_language_constraints(output: dict) -> None:
    serialized = str(output).lower()

    for phrase in FORBIDDEN_LANGUAGE_PHRASES:
        if phrase in serialized:
            raise Phase52ValidationError(
                reason_code="LANGUAGE_VIOLATION",
                violation_detail=f"Forbidden language detected: '{phrase}'",
                raw_excerpt=phrase,
            )
