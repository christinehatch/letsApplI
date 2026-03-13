from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from .schema_loader import load_phase52_schema
from .errors import Phase52ValidationError


def validate_schema(output_json: dict) -> None:
    schema = load_phase52_schema()
    validator = Draft202012Validator(schema)

    errors = sorted(validator.iter_errors(output_json), key=lambda e: e.path)

    if errors:
        first_error = errors[0]
        path = "$"
        if first_error.path:
            path += "".join(
                f"[{part}]" if isinstance(part, int) else f".{part}"
                for part in first_error.path
            )
        raise Phase52ValidationError(
            reason_code="SCHEMA_VIOLATION",
            violation_detail=f"{path}: {first_error.message}",
            raw_excerpt=str(first_error.instance)
        )
