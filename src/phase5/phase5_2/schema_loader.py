import json
from pathlib import Path


SCHEMA_PATH = (
    Path(__file__).parent / "schema" / "phase_5_2_interpretation.schema.json"
)


def load_phase52_schema() -> dict:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
