import json
import hashlib


def canonicalize_json(data: dict) -> str:
    """
    Deterministic canonical JSON representation.
    """
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
def normalize_for_hash(output: dict) -> dict:
    """
    Reduce interpretation output to structural invariants only.

    Removes lexical variability.
    Preserves architectural invariants.
    """

    return {
        "schema_version": output.get("schema_version"),
        "confidence": output.get("confidence"),

        "requirements_count": len(
            output.get("RequirementsAnalysis", {}).get("explicit_requirements", [])
        ),

        "modality_distribution": sorted([
            r.get("modality")
            for r in output.get("RequirementsAnalysis", {}).get("explicit_requirements", [])
        ]),

        "capability_domains": sorted([
            d.get("domain_label")
            for d in output.get("CapabilityEmphasisSignals", [])
        ]),

        "project_surface_count": len(
            output.get("ProjectOpportunitySignals", [])
        ),
    }


def compute_structural_hash(data: dict) -> str:
    normalized = normalize_for_hash(data)
    canonical = canonicalize_json(normalized)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
